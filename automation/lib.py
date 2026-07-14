"""Shared plumbing for Syltech automation. stdlib only — no pip installs, ever.

Rules for any model editing this file:
- No third-party imports. If a change seems to need one, stop and open an
  issue labeled `automation-failure` explaining why, instead of adding it.
- Every network call goes through http_get / gh_api; they own the retries.
- On unrecoverable errors, entrypoints call file_failure() and exit 1.
  Never print-and-continue, never guess.
"""

import json
import re
import sys
import time
import hashlib
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree

USER_AGENT = "syltech-automation/1.0 (+https://github.com/sylvester-francis/sylvester-francis)"
GITHUB_API = "https://api.github.com"

FETCH_RETRIES = 2          # attempts = FETCH_RETRIES + 1
GH_RETRIES = 3
BACKOFF_BASE_SECONDS = 2   # 2s, 4s, 8s...


class AutomationError(Exception):
    """Raised with a stage string so failures are attributable."""

    def __init__(self, stage, message):
        self.stage = stage
        super().__init__(f"[{stage}] {message}")


def now_utc():
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------- HTTP


def http_get(url, timeout=25, retries=FETCH_RETRIES, headers=None):
    """GET with retries and backoff. Returns bytes. Raises AutomationError."""
    hdrs = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    if headers:
        hdrs.update(headers)
    last = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=hdrs)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except Exception as exc:  # URLError, HTTPError, timeout, TLS
            last = exc
            if isinstance(exc, urllib.error.HTTPError) and exc.code in (401, 403, 404):
                break  # non-transient: do not burn retries
            if attempt < retries:
                time.sleep(BACKOFF_BASE_SECONDS * (2 ** attempt))
    raise AutomationError("http_get", f"{url} failed after {retries + 1} attempts: {last}")


def gh_api(method, path, token, body=None, retries=GH_RETRIES):
    """GitHub API call. `path` starts with '/'. Returns parsed JSON (or {})."""
    url = GITHUB_API + path
    data = json.dumps(body).encode() if body is not None else None
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=data, method=method)
            req.add_header("Authorization", f"Bearer {token}")
            req.add_header("Accept", "application/vnd.github+json")
            req.add_header("User-Agent", USER_AGENT)
            if data is not None:
                req.add_header("Content-Type", "application/json")
            with urllib.request.urlopen(req, timeout=25) as resp:
                raw = resp.read()
                return json.loads(raw) if raw.strip() else {}
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code == 422:
                raise  # semantic error (e.g. label exists) — caller decides
            if 400 <= exc.code < 500:
                break  # other 4xx: not transient
            if attempt < retries - 1:
                time.sleep(BACKOFF_BASE_SECONDS * (2 ** attempt))
        except Exception as exc:
            last = exc
            if attempt < retries - 1:
                time.sleep(BACKOFF_BASE_SECONDS * (2 ** attempt))
    raise AutomationError("gh_api", f"{method} {path} failed after {retries} attempts: {last}")


# ---------------------------------------------------------------- feed parsing


def _strip_ns(tag):
    return tag.rsplit("}", 1)[-1]


def _parse_when(text):
    """Best-effort timestamp parse. Returns aware datetime or None. Never raises."""
    if not text:
        return None
    text = text.strip()
    try:
        dt = parsedate_to_datetime(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        pass
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def parse_feed(raw_bytes):
    """Tolerant RSS 2.0 / Atom parser. Returns [{title,url,summary,ts,points}]."""
    items = []
    try:
        root = ElementTree.fromstring(raw_bytes)
    except ElementTree.ParseError as exc:
        raise AutomationError("parse_feed", f"XML parse error: {exc}")
    for node in root.iter():
        if _strip_ns(node.tag) not in ("item", "entry"):
            continue
        title, url, summary, when = "", "", "", None
        for child in node:
            tag = _strip_ns(child.tag)
            text = (child.text or "").strip()
            if tag == "title":
                title = re.sub(r"\s+", " ", text)
            elif tag == "link":
                url = text or child.get("href", "") or url
            elif tag in ("description", "summary", "content", "encoded") and not summary:
                summary = re.sub(r"<[^>]+>", " ", text)[:1500]
            elif tag in ("pubDate", "published", "updated", "date") and when is None:
                when = _parse_when(text)
        if title:
            items.append({"title": title, "url": url, "summary": summary,
                          "ts": when, "points": None})
    return items


def parse_algolia(raw_bytes):
    """HN Algolia API. Returns same item shape as parse_feed."""
    data = json.loads(raw_bytes)
    items = []
    for hit in data.get("hits", []):
        title = (hit.get("title") or "").strip()
        if not title:
            continue
        url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
        ts = None
        if hit.get("created_at_i"):
            ts = datetime.fromtimestamp(hit["created_at_i"], tz=timezone.utc)
        items.append({"title": title, "url": url,
                      "summary": (hit.get("story_text") or "")[:1500],
                      "ts": ts, "points": hit.get("points")})
    return items


def parse_lobsters(raw_bytes):
    data = json.loads(raw_bytes)
    items = []
    for story in data:
        title = (story.get("title") or "").strip()
        if not title:
            continue
        items.append({"title": title,
                      "url": story.get("url") or story.get("comments_url", ""),
                      "summary": " ".join(story.get("tags", []))[:1500],
                      "ts": _parse_when(story.get("created_at")),
                      "points": story.get("score")})
    return items


PARSERS = {"rss": parse_feed, "atom": parse_feed,
           "algolia": parse_algolia, "lobsters": parse_lobsters}


# ---------------------------------------------------------------- URL + text utils

_TRACKING_PARAMS = re.compile(r"^(utm_|ref$|ref_|source$|si$|fbclid|gclid)")

_STOPWORDS = {"the", "and", "for", "you", "your", "not", "now", "with", "that",
              "this", "its", "has", "have", "are", "was", "how", "why", "what",
              "when", "who", "will", "can", "into", "from", "out", "our"}


def normalize_url(url):
    try:
        parts = urllib.parse.urlsplit(url.strip())
        query = "&".join(
            kv for kv in parts.query.split("&")
            if kv and not _TRACKING_PARAMS.match(kv.split("=")[0].lower())
        )
        return urllib.parse.urlunsplit(
            (parts.scheme.lower(), parts.netloc.lower(),
             parts.path.rstrip("/"), query, "")
        )
    except Exception:
        return url.strip().lower()


def url_hash(url):
    return hashlib.sha1(normalize_url(url).encode()).hexdigest()[:16]


def title_tokens(title):
    return {w for w in re.findall(r"[a-z0-9]{3,}", title.lower()) if w not in _STOPWORDS}


def jaccard(a_tokens, b_tokens):
    if not a_tokens or not b_tokens:
        return 0.0
    return len(a_tokens & b_tokens) / len(a_tokens | b_tokens)


# ---------------------------------------------------------------- GitHub issue helpers


def repo_env():
    import os
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    token = os.environ.get("GITHUB_TOKEN", "")
    return repo, token


def ensure_label(repo, token, name, color, description):
    try:
        gh_api("POST", f"/repos/{repo}/labels",
               token, {"name": name, "color": color, "description": description})
    except urllib.error.HTTPError as exc:
        if exc.code != 422:  # 422 = already exists = fine
            raise


def create_issue(repo, token, title, body, labels):
    return gh_api("POST", f"/repos/{repo}/issues", token,
                  {"title": title, "body": body, "labels": labels})


def comment_issue(repo, token, number, body):
    return gh_api("POST", f"/repos/{repo}/issues/{number}/comments", token,
                  {"body": body})


def list_issues(repo, token, labels, state="open", per_page=30, extra=""):
    path = (f"/repos/{repo}/issues?labels={urllib.parse.quote(labels)}"
            f"&state={state}&per_page={per_page}&sort=created&direction=desc{extra}")
    result = gh_api("GET", path, token)
    return [i for i in result if "pull_request" not in i]


MAX_OPEN_FAILURE_ISSUES = 5


def file_failure(component, stage, error, counts=None):
    """Loud, structured failure. Files/updates an `automation-failure` issue.

    Never raises: if even this fails, we print to stderr and the red workflow
    run (plus GitHub's own failure email to the repo owner) is the backstop.
    """
    payload = {
        "component": component,
        "stage": stage,
        "error": str(error)[:2000],
        "utc": now_utc().isoformat(timespec="seconds"),
        "counts": counts or {},
    }
    block = "```json\n" + json.dumps(payload, indent=2) + "\n```"
    body = (
        f"**{component}** failed at stage **{stage}**.\n\n{block}\n\n"
        "Runbook: `automation/README.md` → *When something fails*. "
        "Re-run manually from the Actions tab (`workflow_dispatch`) after fixing."
    )
    sys.stderr.write(f"FAILURE {json.dumps(payload)}\n")
    try:
        repo, token = repo_env()
        if not repo or not token:
            return
        ensure_label(repo, token, "automation-failure", "b60205",
                     "An automation broke and needs a human")
        open_failures = list_issues(repo, token, "automation-failure")
        same = [i for i in open_failures if f"· {component} ·" in i["title"]]
        if same:
            comment_issue(repo, token, same[0]["number"], body)
        elif len(open_failures) >= MAX_OPEN_FAILURE_ISSUES:
            comment_issue(repo, token, open_failures[0]["number"],
                          f"(cap of {MAX_OPEN_FAILURE_ISSUES} open failure issues reached)\n\n" + body)
        else:
            create_issue(repo, token,
                         f"Automation failure · {component} · {now_utc().date()}",
                         body, ["automation-failure"])
    except Exception as exc:  # reporting must never crash the reporter
        sys.stderr.write(f"failure-reporting itself failed: {exc}\n")
