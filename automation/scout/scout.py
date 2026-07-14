#!/usr/bin/env python3
"""Morning Scout — finds 0-3 in-beat story angles and files them as a GitHub issue.

Contract (the full spec lives in automation/README.md):
- Runs daily. ALWAYS files exactly one issue per run, even on a zero-result
  day — silence means breakage, never "nothing found".
- Deterministic core: fixed sources (sources.json), fixed keyword scoring
  (keywords.json), fixed thresholds. No judgment calls anywhere.
- Optional enrichment via enrich.py; when it fails, the brief still ships,
  marked "degraded". The scout must never depend on a model to function.
- Exit 0 = brief filed (possibly degraded). Exit 1 = hard failure, reported
  via a structured `automation-failure` issue before exiting.

Usage:
  python3 automation/scout/scout.py             # live (needs GITHUB_TOKEN, GITHUB_REPOSITORY)
  python3 automation/scout/scout.py --dry-run   # fetch + score + print, no issue
  python3 automation/scout/scout.py --selftest  # offline fixture tests, no network
"""

import json
import os
import re
import sys
from datetime import timedelta

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import lib  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
STATE_PATH = os.path.join(REPO_ROOT, "automation", "state", "seen.json")
README_PATH = os.path.join(REPO_ROOT, "README.md")

ISSUE_LABEL = "scout-brief"
MAX_BODY_CHARS = 60000


# ---------------------------------------------------------------- config + state


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_state():
    try:
        return load_json(STATE_PATH)
    except Exception:
        return {}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=1, sort_keys=True)
        fh.write("\n")


def load_own_titles(readme_text):
    """Titles of already-published posts, parsed from the README marker blocks
    (kept fresh daily by the existing blog-posts workflow)."""
    titles = []
    for marker in ("MEDIUM-POST-LIST", "SUBSTACK-POST-LIST"):
        match = re.search(
            rf"<!-- {marker}:START -->(.*?)<!-- {marker}:END -->", readme_text, re.S
        )
        if match:
            titles += re.findall(r"- \[([^\]]+)\]", match.group(1))
    return titles


# ---------------------------------------------------------------- scoring


def keyword_hits(item, kw):
    """Returns (points, matched_labels). Each keyword counts once; title hits
    use the title multiplier. Fixed rule, no judgment."""
    title = " " + item["title"].lower() + " "
    summary = " " + (item.get("summary") or "").lower() + " "
    points, matched = 0, []
    for tier, weight in (("tier_a", kw["weights"]["tier_a"]),
                         ("tier_b", kw["weights"]["tier_b"]),
                         ("tier_c", kw["weights"]["tier_c"])):
        for keyword in kw[tier]:
            pattern = r"\b" + re.escape(keyword.lower()) + r"\b"
            if re.search(pattern, title):
                points += weight * kw["title_multiplier"]
                matched.append(f"`{keyword}`({tier[-1].upper()},title)")
            elif re.search(pattern, summary):
                points += weight
                matched.append(f"`{keyword}`({tier[-1].upper()})")
    return points, matched


def score_item(item, kw, now):
    title_lower = item["title"].lower()
    for bad in kw["negative"]:
        if bad in title_lower:
            return 0, [f"negative:`{bad}`"]
    points, matched = keyword_hits(item, kw)
    if not any("(A" in m or "(B" in m for m in matched):
        return 0, matched  # tier_c alone never qualifies
    if item.get("ts"):
        age = now - item["ts"]
        if age <= timedelta(hours=24):
            points += kw["recency_bonus"]["under_24h"]
        elif age <= timedelta(hours=48):
            points += kw["recency_bonus"]["under_48h"]
    if item.get("points"):
        for cutoff in sorted((int(k) for k in kw["popularity_bonus"]), reverse=True):
            if item["points"] >= cutoff:
                points += kw["popularity_bonus"][str(cutoff)]
                break
    return points, matched


# ---------------------------------------------------------------- pipeline


def fetch_sources(cfg):
    ok, failed, items = [], [], []
    for src in cfg["sources"]:
        try:
            raw = lib.http_get(src["url"])
            parsed = lib.PARSERS[src["type"]](raw)
            for item in parsed:
                item["source"] = src["id"]
            items += parsed
            ok.append(src["id"])
        except Exception as exc:
            failed.append(f"{src['id']} ({str(exc)[:120]})")
    return ok, failed, items


def run_pipeline(cfg, kw, items, state, own_titles, now):
    counts = {"scanned": len(items)}

    fresh = []
    for item in items:
        if item.get("ts") and (now - item["ts"]).days > kw["max_item_age_days"]:
            continue
        fresh.append(item)
    counts["within_age_window"] = len(fresh)

    scored = []
    for item in fresh:
        score, matched = score_item(item, kw, now)
        if score >= kw["threshold"]:
            item["score"], item["matched"] = score, matched
            scored.append(item)
    counts["qualified"] = len(scored)

    best = {}
    for item in scored:  # same story from two sources: keep the higher score
        key = lib.url_hash(item["url"])
        if key not in best or item["score"] > best[key]["score"]:
            best[key] = item
    counts["after_batch_dedupe"] = len(best)

    cutoff = (now - timedelta(days=kw["seen_window_days"])).date().isoformat()
    live_seen = {h: d for h, d in state.items() if d >= cutoff}
    unseen = [i for k, i in best.items() if k not in live_seen]
    counts["dropped_already_delivered"] = counts["after_batch_dedupe"] - len(unseen)

    own_sets = [lib.title_tokens(t) for t in own_titles]
    final = []
    for item in unseen:
        tokens = lib.title_tokens(item["title"])
        if any(lib.jaccard(tokens, own) >= kw["own_overlap_jaccard"] for own in own_sets):
            continue
        final.append(item)
    counts["dropped_own_overlap"] = len(unseen) - len(final)

    final.sort(key=lambda i: (i["score"], i["ts"].isoformat() if i.get("ts") else ""),
               reverse=True)
    delivered = final[:kw["max_delivered"]]
    counts["delivered"] = len(delivered)
    return delivered, live_seen, counts


# ---------------------------------------------------------------- rendering


def render_item(rank, item, enrichment):
    age = ""
    if item.get("ts"):
        hours = int((lib.now_utc() - item["ts"]).total_seconds() // 3600)
        age = f" · {hours}h old"
    pop = f" · {item['points']} points" if item.get("points") else ""
    extra = enrichment.get(item["id"], {}) if enrichment else {}
    angle = extra.get("angle") or "—"
    number = extra.get("number") or "—"
    tie = extra.get("syltech_tie") or "—"
    matched = ", ".join(item["matched"][:6])
    return (
        f"### {rank}. [{item['title']}]({item['url']}) — score {item['score']}\n"
        f"- **Source:** {item['source']}{age}{pop}\n"
        f"- **Why in-beat:** {matched}\n"
        f"- **Angle:** {angle}\n"
        f"- **The number:** {number}\n"
        f"- **Syltech tie:** {tie}\n"
    )


def render_body(delivered, enrichment, enrich_status, ok, failed, counts,
                seen_size, rules_hash, today):
    lines = [f"## Scout · {today}", ""]
    if delivered:
        for rank, item in enumerate(delivered, 1):
            lines.append(render_item(rank, item, enrichment))
    else:
        lines.append("**0 qualified stories today.** That is a report, not a failure — "
                     "see the self-check below for what was scanned.")
    lines += [
        "",
        "---",
        "### Self-check",
        f"- Sources fetched: {len(ok)}/{len(ok) + len(failed)} ok"
        + (f" (failed: {'; '.join(failed)})" if failed else ""),
        f"- Items scanned: {counts['scanned']} · in age window: {counts['within_age_window']}"
        f" · passed scoring: {counts['qualified']}",
        f"- Dropped as already delivered: {counts['dropped_already_delivered']}"
        f" · dropped as overlapping own posts: {counts['dropped_own_overlap']}",
        f"- Delivered: {counts['delivered']} (max 3)",
        f"- Dedupe memory: {seen_size} URLs (21-day window)",
        f"- Enrichment: {enrich_status}",
        f"- Rules: keywords.json sha1:{rules_hash}",
        "",
        "**Process rule:** pick at most one, or close with no pick. Never publish "
        "a number above without opening the source link first. Close this issue "
        "once processed (the Monday scorecard counts open briefs older than 48h).",
    ]
    return "\n".join(lines)


def validate_body(body, delivered, kw):
    """Machine check that the brief is well-formed before it ships."""
    problems = []
    if len(body) > MAX_BODY_CHARS:
        problems.append(f"body too large: {len(body)}")
    if "Self-check" not in body:
        problems.append("missing self-check block")
    if not 0 <= len(delivered) <= kw["max_delivered"]:
        problems.append(f"delivered count out of range: {len(delivered)}")
    for item in delivered:
        if not str(item.get("url", "")).startswith("http"):
            problems.append(f"bad url: {item.get('url')!r}")
        if item["score"] < kw["threshold"]:
            problems.append(f"under-threshold item leaked: {item['title'][:60]}")
    return problems


# ---------------------------------------------------------------- main


def main(dry_run):
    now = lib.now_utc()
    today = now.date().isoformat()
    cfg = load_json(os.path.join(HERE, "sources.json"))
    kw = load_json(os.path.join(HERE, "keywords.json"))
    with open(os.path.join(HERE, "keywords.json"), "rb") as fh:
        rules_hash = __import__("hashlib").sha1(fh.read()).hexdigest()[:8]

    try:
        readme = open(README_PATH, encoding="utf-8").read()
    except Exception:
        readme = ""
    own_titles = load_own_titles(readme)

    ok, failed, items = fetch_sources(cfg)
    if len(ok) < cfg["min_sources_ok"]:
        raise lib.AutomationError(
            "fetch", f"only {len(ok)}/{len(cfg['sources'])} sources fetched: {failed}")

    state = load_state()
    delivered, live_seen, counts = run_pipeline(cfg, kw, items, state, own_titles, now)
    for rank, item in enumerate(delivered, 1):
        item["id"] = f"item{rank}"

    enrichment, enrich_status = {}, "off (no ANTHROPIC_API_KEY)"
    if os.environ.get("ANTHROPIC_API_KEY") and delivered:
        try:
            import enrich
            enrichment, enrich_status = enrich.enrich_items(delivered, REPO_ROOT)
        except Exception as exc:
            enrichment, enrich_status = {}, f"degraded: {str(exc)[:200]}"

    body = render_body(delivered, enrichment, enrich_status, ok, failed, counts,
                       len(live_seen) + len(delivered), rules_hash, today)
    problems = validate_body(body, delivered, kw)
    if problems:
        raise lib.AutomationError("validate", "; ".join(problems))

    if dry_run:
        print(body)
        print(f"\nDRY RUN — no issue filed. counts={json.dumps(counts)}")
        return

    repo, token = lib.repo_env()
    if not repo or not token:
        raise lib.AutomationError("post", "GITHUB_TOKEN / GITHUB_REPOSITORY not set")
    lib.ensure_label(repo, token, ISSUE_LABEL, "ff5c00", "Daily story angles from the scout")
    issue = lib.create_issue(repo, token, f"Scout · {today}", body, [ISSUE_LABEL])

    for item in delivered:
        live_seen[lib.url_hash(item["url"])] = today
    save_state(live_seen)
    print(json.dumps({"issue": issue.get("number"), "counts": counts,
                      "enrichment": enrich_status}))


# ---------------------------------------------------------------- selftest (offline)

RSS_FIXTURE = b"""<?xml version="1.0"?><rss version="2.0"><channel>
<item><title>New MCP sandbox escapes, patched</title>
<link>https://example.com/a?utm_source=x</link>
<description>Prompt injection via tool calling in agent frameworks.</description>
<pubDate>Mon, 13 Jul 2026 09:00:00 GMT</pubDate></item>
<item><title>Bitcoin agent hits new high</title>
<link>https://example.com/b</link><description>crypto news</description></item>
</channel></rss>"""

ATOM_FIXTURE = b"""<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom">
<entry><title>Kubernetes release notes</title>
<link href="https://example.com/k8s"/><updated>2026-07-13T08:00:00Z</updated>
<summary>model inference on gpu</summary></entry></feed>"""

ALGOLIA_FIXTURE = json.dumps({"hits": [
    {"title": "Show HN: my coding agent harness", "url": None,
     "objectID": "123", "points": 150, "created_at_i": 1783000000},
]}).encode()


def selftest():
    kw = load_json(os.path.join(HERE, "keywords.json"))
    now = lib.now_utc()
    checks = []

    rss = lib.parse_feed(RSS_FIXTURE)
    checks.append(("rss parses 2 items", len(rss) == 2))
    checks.append(("rss title", rss[0]["title"] == "New MCP sandbox escapes, patched"))

    atom = lib.parse_feed(ATOM_FIXTURE)
    checks.append(("atom parses with ts", len(atom) == 1 and atom[0]["ts"] is not None))

    alg = lib.parse_algolia(ALGOLIA_FIXTURE)
    checks.append(("algolia fallback url",
                   alg[0]["url"] == "https://news.ycombinator.com/item?id=123"))
    checks.append(("algolia points", alg[0]["points"] == 150))

    fresh_ts = now - timedelta(hours=3)
    strong = {"title": "New MCP sandbox escapes, patched", "summary": "agents everywhere",
              "ts": fresh_ts, "points": None}
    score, matched = score_item(strong, kw, now)
    checks.append((f"tier_a title story qualifies (score {score})", score >= kw["threshold"]))

    weak = {"title": "A new model benchmark release", "summary": "", "ts": fresh_ts,
            "points": None}
    wscore, _ = score_item(weak, kw, now)
    checks.append(("tier_c-only story rejected", wscore == 0))

    neg = {"title": "Bitcoin agent trading bot", "summary": "agent agent agent",
           "ts": fresh_ts, "points": None}
    nscore, _ = score_item(neg, kw, now)
    checks.append(("negative keyword kills story", nscore == 0))

    checks.append(("url normalize strips utm + slash",
                   lib.normalize_url("https://Ex.com/a/?utm_source=x") ==
                   lib.normalize_url("https://ex.com/a")))

    own = lib.title_tokens("The harness is the product now, not the model")
    cand = lib.title_tokens("The harness is the product, not the model")
    checks.append(("own-post overlap detected", lib.jaccard(own, cand) >= 0.5))

    item = {"title": "T", "url": "https://x.com", "score": 9, "matched": ["`mcp`(A,title)"],
            "source": "hn-front", "ts": None, "points": None, "id": "item1"}
    body = render_body([item], {}, "off", ["s1", "s2"], [], {
        "scanned": 10, "within_age_window": 9, "qualified": 3,
        "after_batch_dedupe": 3, "dropped_already_delivered": 1,
        "dropped_own_overlap": 1, "delivered": 1}, 5, "abcd1234", "2026-07-14")
    checks.append(("render has self-check", "Self-check" in body and "score 9" in body))

    zero = render_body([], {}, "off", ["s1", "s2"], [], {
        "scanned": 10, "within_age_window": 9, "qualified": 0,
        "after_batch_dedupe": 0, "dropped_already_delivered": 0,
        "dropped_own_overlap": 0, "delivered": 0}, 5, "abcd1234", "2026-07-14")
    checks.append(("zero-day body is a report", "0 qualified stories" in zero))

    failures = [name for name, passed in checks if not passed]
    for name, passed in checks:
        print(("PASS " if passed else "FAIL ") + name)
    if failures:
        print(f"SELFTEST FAILED: {failures}")
        sys.exit(1)
    print(f"SELFTEST OK ({len(checks)} checks)")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
        sys.exit(0)
    try:
        main(dry_run="--dry-run" in sys.argv)
    except Exception as exc:
        stage = getattr(exc, "stage", "unhandled")
        lib.file_failure("scout", stage, exc)
        sys.exit(1)
