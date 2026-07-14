#!/usr/bin/env python3
"""Context-pack refresh — keeps the machine-owned half of the pack current and
nags (loudly, via issue) when the human-owned half goes stale.

Ownership rule (never violate):
- context/RECENT.md is MACHINE-OWNED: this script regenerates it wholesale.
- context/VOICE.md, SYLTECH.md, PROJECTS.md, PLAYBOOK.md are HUMAN-OWNED:
  this script only measures their age (last git commit) and files/refreshes a
  `pack-stale` issue past MAX_AGE_DAYS. It NEVER edits them.

Exit 0 = pack refreshed (possibly with degraded sources, noted in the file).
Exit 1 = hard failure, reported via `automation-failure` issue.

Usage:
  python3 automation/pack/pack_refresh.py             # live
  python3 automation/pack/pack_refresh.py --dry-run   # print RECENT.md, no write/issues
  python3 automation/pack/pack_refresh.py --selftest  # offline
"""

import json
import os
import re
import subprocess
import sys
import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import lib  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
RECENT_PATH = os.path.join(REPO_ROOT, "context", "RECENT.md")

MEDIUM_FEED = "https://medium.com/feed/@sylvesterranjithfrancis"
SUBSTACK_VIA_RSS2JSON = ("https://api.rss2json.com/v1/api.json?rss_url="
                         + urllib.parse.quote("https://techwithsyl.substack.com/feed", safe=""))
HUMAN_FILES = ["context/VOICE.md", "context/SYLTECH.md",
               "context/PROJECTS.md", "context/PLAYBOOK.md"]
MAX_AGE_DAYS = 45
STALE_LABEL = "pack-stale"
MAX_POSTS = 5


def fetch_medium():
    items = lib.parse_feed(lib.http_get(MEDIUM_FEED))
    return [(i["title"], i["url"].split("?")[0]) for i in items[:MAX_POSTS]]


def fetch_substack():
    data = json.loads(lib.http_get(SUBSTACK_VIA_RSS2JSON))
    if data.get("status") != "ok":
        raise lib.AutomationError("substack", f"rss2json status={data.get('status')}")
    return [(i["title"], i["link"]) for i in data.get("items", [])[:MAX_POSTS]]


def fetch_repo_facts(cfg, token):
    facts = []
    for name in cfg["repos"]:
        data = lib.gh_api("GET", f"/repos/{cfg['owner']}/{name}", token)
        facts.append({
            "name": name,
            "stars": data.get("stargazers_count", 0),
            "pushed": (data.get("pushed_at") or "")[:10],
            "description": (data.get("description") or "").strip(),
            "flagship": name in cfg["flagships"],
        })
    return facts


def file_age_days(rel_path):
    """Days since last commit touching the file. Requires full clone history."""
    out = subprocess.run(
        ["git", "log", "-1", "--format=%ct", "--", rel_path],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=30,
    )
    stamp = out.stdout.strip()
    if not stamp:
        return None  # never committed — treat as unknown, reported as stale
    return int((lib.now_utc().timestamp() - int(stamp)) // 86400)


def render_recent(medium, substack, repo_facts, statuses, today):
    lines = [
        "# RECENT — machine-owned. Do not hand-edit.",
        "",
        "Regenerated weekly by `automation/pack/pack_refresh.py` "
        "(workflow: `context-pack.yml`). Hand edits will be overwritten.",
        f"Last regenerated: {today}",
        "",
        "## Latest published posts",
        "",
        "### Medium",
    ]
    lines += [f"- [{t}]({u})" for t, u in medium] or ["- (fetch failed this week)"]
    lines += ["", "### Substack"]
    lines += [f"- [{t}]({u})" for t, u in substack] or ["- (fetch failed this week)"]
    lines += ["", "## Project facts (live)", ""]
    if repo_facts:
        lines.append("| Repo | Stars | Last push | Description |")
        lines.append("|---|---|---|---|")
        for fact in repo_facts:
            marker = "**" if fact["flagship"] else ""
            lines.append(f"| {marker}{fact['name']}{marker} | {fact['stars']} "
                         f"| {fact['pushed']} | {fact['description'][:100]} |")
    else:
        lines.append("(repo facts unavailable this week)")
    lines += [
        "",
        "## Self-check",
        f"- Sources this run: {', '.join(f'{k}: {v}' for k, v in statuses.items())}",
        f"- Posts listed: {len(medium)} medium + {len(substack)} substack "
        f"· repos listed: {len(repo_facts)}",
    ]
    return "\n".join(lines) + "\n"


def stale_issue_body(stale):
    rows = "\n".join(f"- `{path}` — last commit {age if age is not None else 'unknown'} "
                     f"days ago (limit {MAX_AGE_DAYS})" for path, age in stale)
    return (
        "These human-owned context files are past their freshness limit. "
        "The machines keep quoting them, so stale files mean the system speaks "
        "with an outdated voice.\n\n" + rows +
        "\n\nFix: edit the file (even a reviewed no-change commit resets the clock). "
        "This issue closes itself on the next weekly run once everything is fresh."
    )


def manage_stale_issue(repo, token, stale):
    lib.ensure_label(repo, token, STALE_LABEL, "fbca04", "Human-owned context files need review")
    existing = lib.list_issues(repo, token, STALE_LABEL)
    if stale:
        body = stale_issue_body(stale)
        if existing:
            lib.gh_api("PATCH", f"/repos/{repo}/issues/{existing[0]['number']}",
                       token, {"body": body})
        else:
            lib.create_issue(repo, token, "Context pack: stale sections need a human",
                             body, [STALE_LABEL])
    else:
        for issue in existing:
            lib.comment_issue(repo, token, issue["number"],
                              "All context files fresh again — closing automatically.")
            lib.gh_api("PATCH", f"/repos/{repo}/issues/{issue['number']}",
                       token, {"state": "closed"})


def main(dry_run):
    today = lib.now_utc().date().isoformat()
    cfg = json.load(open(os.path.join(HERE, "repos.json"), encoding="utf-8"))
    repo, token = lib.repo_env()

    statuses, medium, substack, repo_facts = {}, [], [], []
    try:
        medium = fetch_medium()
        statuses["medium"] = "ok"
    except Exception as exc:
        statuses["medium"] = f"failed ({str(exc)[:80]})"
    try:
        substack = fetch_substack()
        statuses["substack"] = "ok"
    except Exception as exc:
        statuses["substack"] = f"failed ({str(exc)[:80]})"
    try:
        if not token:
            raise lib.AutomationError("repos", "no GITHUB_TOKEN")
        repo_facts = fetch_repo_facts(cfg, token)
        statuses["repo-facts"] = "ok"
    except Exception as exc:
        statuses["repo-facts"] = f"failed ({str(exc)[:80]})"

    if not medium and not substack and not repo_facts:
        raise lib.AutomationError("fetch", f"every source failed: {statuses}")

    content = render_recent(medium, substack, repo_facts, statuses, today)

    # Post-render check: the newest fetched post title must appear in the output.
    for title, _ in (medium[:1] + substack[:1]):
        if title not in content:
            raise lib.AutomationError("render-check", f"latest title missing: {title[:80]}")

    if dry_run:
        print(content)
        return

    old = ""
    if os.path.exists(RECENT_PATH):
        old = open(RECENT_PATH, encoding="utf-8").read()
    strip_date = lambda s: re.sub(r"Last regenerated: .*", "", s)  # noqa: E731
    if strip_date(old) != strip_date(content):
        os.makedirs(os.path.dirname(RECENT_PATH), exist_ok=True)
        open(RECENT_PATH, "w", encoding="utf-8").write(content)
        print("RECENT.md regenerated")
    else:
        print("RECENT.md unchanged")

    stale = []
    for rel in HUMAN_FILES:
        age = file_age_days(rel)
        if age is None or age > MAX_AGE_DAYS:
            stale.append((rel, age))
    if repo and token:
        manage_stale_issue(repo, token, stale)
    print(json.dumps({"statuses": statuses, "stale": [s[0] for s in stale]}))


def selftest():
    checks = []
    medium = [("Post A", "https://m/a"), ("Post B", "https://m/b")]
    substack = [("Sub A", "https://s/a")]
    facts = [{"name": "Watchdog", "stars": 42, "pushed": "2026-07-01",
              "description": "monitoring", "flagship": True}]
    body = render_recent(medium, substack, facts, {"medium": "ok"}, "2026-07-14")
    checks.append(("recent has machine-owned banner", "machine-owned" in body))
    checks.append(("recent lists posts", "[Post A](https://m/a)" in body))
    checks.append(("recent lists repo row", "**Watchdog**" in body and "| 42 " in body))
    checks.append(("recent has self-check", "Self-check" in body))
    degraded = render_recent([], [], facts, {"medium": "failed (x)"}, "2026-07-14")
    checks.append(("degraded fetch is visible", "(fetch failed this week)" in degraded))
    stale_body = stale_issue_body([("context/VOICE.md", 50)])
    checks.append(("stale body names file and age", "VOICE.md" in stale_body and "50" in stale_body))

    failures = [name for name, ok in checks if not ok]
    for name, ok in checks:
        print(("PASS " if ok else "FAIL ") + name)
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
        lib.file_failure("context-pack", getattr(exc, "stage", "unhandled"), exc)
        sys.exit(1)
