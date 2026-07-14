#!/usr/bin/env python3
"""Monday Scorecard — counts what happened last week and states it in numbers.

This is the watchdog for the whole system AND for the human's publishing
cadence. It uses NO model at all: every row is a count compared against a
fixed threshold. If this file ever grows an LLM call, that is a bug.

Rows (all thresholds are in THRESHOLDS below, nowhere else):
  1. Posts published (Medium + Substack feeds, last 7 days)
  2. Scout briefs delivered (issues labeled scout-brief, last 7 days)
  3. Briefs unprocessed (scout-brief issues still open after 48h)
  4. Repeated story URLs across last 7 briefs (dedupe health)
  5. Automation failures (open failure issues + red workflow runs, 7 days)
  6. Context pack max age (last commit to human-owned files)
  7. Scout source health (min sources-ok ratio parsed from brief footers)

Escalation rule: if row 1 is RED this week AND was RED on the previous
scorecard, the issue title gets a leading double red flag.

Exit 0 = scorecard filed. Exit 1 = hard failure (reported, loud).
"""

import json
import os
import re
import subprocess
import sys
from datetime import timedelta

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import lib  # noqa: E402

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

GREEN, YELLOW, RED, NA = "🟢", "🟡", "🔴", "⚪"
LABEL = "scorecard"
MEDIUM_FEED = "https://medium.com/feed/@sylvesterranjithfrancis"
SUBSTACK_VIA_RSS2JSON = ("https://api.rss2json.com/v1/api.json?rss_url="
                         "https%3A%2F%2Ftechwithsyl.substack.com%2Ffeed")
HUMAN_FILES = ["context/VOICE.md", "context/SYLTECH.md",
               "context/PROJECTS.md", "context/PLAYBOOK.md"]
WORKFLOW_FILES = ["scout.yml", "context-pack.yml", "scorecard.yml"]
MAX_METRIC_FAILURES = 2  # 3+ broken rows means the scorecard itself is unreliable

THRESHOLDS = {
    "posts":       {"green": lambda v: v >= 5, "yellow": lambda v: v >= 3, "target": "5-7"},
    "briefs":      {"green": lambda v: v == 7, "yellow": lambda v: v >= 5, "target": "7/7"},
    "unprocessed": {"green": lambda v: v <= 1, "yellow": lambda v: v <= 3, "target": "<=1"},
    "repeats":     {"green": lambda v: v == 0, "yellow": lambda v: False,  "target": "0"},
    "failures":    {"green": lambda v: v == 0, "yellow": lambda v: v <= 1, "target": "0"},
    "pack_age":    {"green": lambda v: v < 45, "yellow": lambda v: v <= 60, "target": "<45d"},
    "src_health":  {"green": lambda v: v >= 0.8, "yellow": lambda v: v >= 0.6, "target": ">=80%"},
}


def grade(key, value):
    rule = THRESHOLDS[key]
    if rule["green"](value):
        return GREEN
    if rule["yellow"](value):
        return YELLOW
    return RED


def iso_to_dt(text):
    from datetime import datetime, timezone
    return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)


# ---------------------------------------------------------------- metric collectors


def posts_last_7d(now):
    titles = []
    for fetch in (
        lambda: [(i["title"], i["ts"]) for i in lib.parse_feed(lib.http_get(MEDIUM_FEED))],
        lambda: [(i["title"], lib._parse_when(i.get("pubDate")))
                 for i in json.loads(lib.http_get(SUBSTACK_VIA_RSS2JSON)).get("items", [])],
    ):
        try:
            for title, ts in fetch():
                if ts and now - ts <= timedelta(days=7):
                    titles.append(title)
        except Exception:
            continue  # one dead feed must not sink the row; both dead -> low count is visible
    return titles


def briefs_last_7d(repo, token, now):
    issues = lib.list_issues(repo, token, "scout-brief", state="all", per_page=30)
    cutoff = now - timedelta(days=7)
    return [i for i in issues if iso_to_dt(i["created_at"]) >= cutoff]


def unprocessed_briefs(repo, token, now):
    issues = lib.list_issues(repo, token, "scout-brief", state="open", per_page=30)
    return [i for i in issues if now - iso_to_dt(i["created_at"]) > timedelta(hours=48)]


def repeated_urls(briefs):
    seen, repeats = set(), set()
    for issue in briefs[:7]:
        for url in re.findall(r"^### \d+\. \[[^\]]*\]\((http[^)]+)\)",
                              issue.get("body") or "", re.M):
            key = lib.url_hash(url)
            if key in seen:
                repeats.add(key)
            else:
                seen.add(key)
    return len(repeats)


def source_health(briefs):
    ratios = []
    for issue in briefs[:7]:
        match = re.search(r"Sources fetched: (\d+)/(\d+)", issue.get("body") or "")
        if match and int(match.group(2)) > 0:
            ratios.append(int(match.group(1)) / int(match.group(2)))
    return min(ratios) if ratios else None


def automation_failures(repo, token, now):
    count = len(lib.list_issues(repo, token, "automation-failure", state="open"))
    cutoff = now - timedelta(days=7)
    for fname in WORKFLOW_FILES:
        try:
            runs = lib.gh_api("GET",
                              f"/repos/{repo}/actions/workflows/{fname}/runs?per_page=20",
                              token)
            for run in runs.get("workflow_runs", []):
                if (run.get("conclusion") == "failure"
                        and iso_to_dt(run["created_at"]) >= cutoff):
                    count += 1
        except Exception:
            continue  # workflow may not exist yet (first weeks) — not a failure
    return count


def pack_max_age():
    ages = []
    for rel in HUMAN_FILES:
        out = subprocess.run(["git", "log", "-1", "--format=%ct", "--", rel],
                             cwd=REPO_ROOT, capture_output=True, text=True, timeout=30)
        stamp = out.stdout.strip()
        if not stamp:
            return 999  # untracked human file = maximally stale, loudly
        ages.append(int((lib.now_utc().timestamp() - int(stamp)) // 86400))
    return max(ages) if ages else 999


def previous_posts_row_red(repo, token):
    issues = lib.list_issues(repo, token, LABEL, state="all", per_page=5)
    if not issues:
        return False
    body = issues[0].get("body") or ""
    row = next((l for l in body.splitlines() if "Posts published" in l), "")
    return RED in row


# ---------------------------------------------------------------- render


def render(rows, notes, computed, failed_metrics, today, escalated):
    lines = [f"## Scorecard · week ending {today}", ""]
    if escalated:
        lines += ["**Second consecutive red week on publishing. The system is fine; "
                  "the pipeline above it is starving.**", ""]
    lines += ["| Metric | Value | Target | State |", "|---|---|---|---|"]
    lines += rows
    lines += ["", "### Detail"] + (notes or ["- (none)"])
    lines += [
        "",
        "---",
        "### Self-check",
        f"- Metrics computed: {computed}/7"
        + (f" (failed: {', '.join(failed_metrics)})" if failed_metrics else ""),
        "- Thresholds: fixed in `automation/scorecard/scorecard.py` (THRESHOLDS)",
        "",
        "Close this issue after reading it. Two rows red for two straight weeks "
        "means change the system, not the effort — see `automation/README.md`.",
    ]
    return "\n".join(lines)


def main(dry_run):
    now = lib.now_utc()
    today = now.date().isoformat()
    repo, token = lib.repo_env()
    have_gh = bool(repo and token)
    if not dry_run and not have_gh:
        raise lib.AutomationError("env", "GITHUB_TOKEN / GITHUB_REPOSITORY not set")

    rows, notes, failed_metrics = [], [], []

    def add_row(label, key, value, display=None):
        rows.append(f"| {label} | {display if display is not None else value} "
                    f"| {THRESHOLDS[key]['target']} | {grade(key, value)} |")

    def add_na(label, target, reason):
        rows.append(f"| {label} | n/a | {target} | {NA} |")
        failed_metrics.append(f"{label}: {reason[:80]}")

    # 1. posts
    posts_red = False
    try:
        titles = posts_last_7d(now)
        add_row("Posts published", "posts", len(titles))
        posts_red = grade("posts", len(titles)) == RED
        notes += [f"- Published: {t}" for t in titles[:10]]
    except Exception as exc:
        add_na("Posts published", "5-7", str(exc))

    briefs = []
    # 2. briefs delivered
    try:
        briefs = briefs_last_7d(repo, token, now) if have_gh else []
        if have_gh:
            add_row("Scout briefs delivered", "briefs", len(briefs))
        else:
            add_na("Scout briefs delivered", "7/7", "no GitHub env (dry run)")
    except Exception as exc:
        add_na("Scout briefs delivered", "7/7", str(exc))

    # 3. unprocessed
    try:
        if have_gh:
            stale = unprocessed_briefs(repo, token, now)
            add_row("Briefs unprocessed >48h", "unprocessed", len(stale))
            notes += [f"- Unprocessed: #{i['number']} {i['title']}" for i in stale[:5]]
        else:
            add_na("Briefs unprocessed >48h", "<=1", "no GitHub env (dry run)")
    except Exception as exc:
        add_na("Briefs unprocessed >48h", "<=1", str(exc))

    # 4. repeats
    try:
        add_row("Repeated story URLs (7 briefs)", "repeats", repeated_urls(briefs))
    except Exception as exc:
        add_na("Repeated story URLs (7 briefs)", "0", str(exc))

    # 5. failures
    try:
        if have_gh:
            add_row("Automation failures (7d)", "failures",
                    automation_failures(repo, token, now))
        else:
            add_na("Automation failures (7d)", "0", "no GitHub env (dry run)")
    except Exception as exc:
        add_na("Automation failures (7d)", "0", str(exc))

    # 6. pack age
    try:
        age = pack_max_age()
        add_row("Context pack max age", "pack_age", age, display=f"{age}d")
    except Exception as exc:
        add_na("Context pack max age", "<45d", str(exc))

    # 7. source health
    try:
        ratio = source_health(briefs)
        if ratio is None:
            add_na("Scout source health", ">=80%", "no brief footers to parse")
        else:
            add_row("Scout source health", "src_health", ratio,
                    display=f"{int(ratio * 100)}%")
    except Exception as exc:
        add_na("Scout source health", ">=80%", str(exc))

    if not dry_run and len(failed_metrics) > MAX_METRIC_FAILURES:
        raise lib.AutomationError(
            "metrics", f"{len(failed_metrics)} rows uncomputable: {failed_metrics}")

    escalated = False
    if posts_red and have_gh:
        try:
            escalated = previous_posts_row_red(repo, token)
        except Exception:
            escalated = False

    body = render(rows, notes, 7 - len(failed_metrics), failed_metrics, today, escalated)
    title = ("🔴🔴 " if escalated else "") + f"Scorecard · week ending {today}"

    if dry_run:
        print(title + "\n\n" + body)
        return
    lib.ensure_label(repo, token, LABEL, "0e8a16", "Weekly numbers for the whole system")
    issue = lib.create_issue(repo, token, title, body, [LABEL])
    print(json.dumps({"issue": issue.get("number"), "failed_metrics": failed_metrics}))


# ---------------------------------------------------------------- selftest

BRIEF_FIXTURE = {
    "number": 1, "created_at": "2026-07-13T09:30:00Z",
    "body": ("### 1. [Story A](https://example.com/a) — score 12\n"
             "### 2. [Story B](https://example.com/b?utm_source=x) — score 9\n"
             "- Sources fetched: 7/8 ok\n"),
}
BRIEF_FIXTURE_2 = {
    "number": 2, "created_at": "2026-07-12T09:30:00Z",
    "body": ("### 1. [Story B again](https://example.com/b) — score 10\n"
             "- Sources fetched: 4/8 ok\n"),
}


def selftest():
    checks = [
        ("posts 6 is green", grade("posts", 6) == GREEN),
        ("posts 3 is yellow", grade("posts", 3) == YELLOW),
        ("posts 1 is red", grade("posts", 1) == RED),
        ("briefs 7 green / 4 red", grade("briefs", 7) == GREEN and grade("briefs", 4) == RED),
        ("repeats 1 is red (no yellow band)", grade("repeats", 1) == RED),
        ("pack 44d green / 61d red", grade("pack_age", 44) == GREEN and grade("pack_age", 61) == RED),
        ("src 0.5 red", grade("src_health", 0.5) == RED),
        ("repeated url across briefs detected (utm ignored)",
         repeated_urls([BRIEF_FIXTURE, BRIEF_FIXTURE_2]) == 1),
        ("source health takes the minimum",
         source_health([BRIEF_FIXTURE, BRIEF_FIXTURE_2]) == 0.5),
    ]
    body = render(["| Posts published | 6 | 5-7 | 🟢 |"], ["- Published: X"],
                  7, [], "2026-07-14", escalated=False)
    checks.append(("render has table and self-check",
                   "| Metric |" in body and "Metrics computed: 7/7" in body))
    esc = render([], [], 7, [], "2026-07-14", escalated=True)
    checks.append(("escalation banner renders", "Second consecutive red week" in esc))

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
        lib.file_failure("scorecard", getattr(exc, "stage", "unhandled"), exc)
        sys.exit(1)
