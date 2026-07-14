#!/usr/bin/env python3
"""Optional LLM enrichment for scout briefs. Isolated on purpose:
the scout must work with this entire file deleted.

Hard rules (these compensate for running on a small model):
- One API call per run, temperature 0, bounded max_tokens.
- Output must be a JSON array with EXACTLY the expected ids and keys.
- The "number" field must be VERBATIM from the item's own title/summary —
  a deterministic digit-check enforces this. A number the model cannot
  support from the given text is replaced with an instruction to go find one.
- 2 attempts, then degrade. Degraded enrichment never blocks the brief.
"""

import json
import os
import re
import sys
import time
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import lib  # noqa: E402

API_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-haiku-4-5-20251001"  # cheap by design; override via ANTHROPIC_MODEL
MAX_ATTEMPTS = 2
MAX_TOKENS = 800
FIELD_LIMITS = {"angle": 240, "number": 120, "syltech_tie": 240}
NO_NUMBER = "no verifiable number in the source — open the link and find one before writing"

SYSTEM = (
    "You annotate story candidates for Sylvester Francis (Syltech AI Systems). "
    "You are given his voice rules and a JSON list of stories. For each story return "
    "an object with keys exactly: id, angle, number, syltech_tie. "
    "angle: one sentence, his voice, stating the take he could argue. "
    "number: ONE concrete figure copied verbatim from the story's title or summary text; "
    "if no figure appears there, use an empty string. NEVER invent or convert figures. "
    "syltech_tie: one sentence on why this matters to a small or mid-size business "
    "buying AI or platform work. "
    "Respond with ONLY the JSON array. No prose, no code fences."
)


def voice_capsule(repo_root):
    """Deterministic extraction of the machine-facing capsule from VOICE.md."""
    path = os.path.join(repo_root, "context", "VOICE.md")
    try:
        text = open(path, encoding="utf-8").read()
        match = re.search(r"<!-- CAPSULE:START -->(.*?)<!-- CAPSULE:END -->", text, re.S)
        return match.group(1).strip()[:2500] if match else ""
    except Exception:
        return ""


def digit_groups(text):
    return {g.replace(",", "").rstrip(".") for g in re.findall(r"\d[\d,.]*", text or "")}


def call_api(prompt):
    body = json.dumps({
        "model": os.environ.get("ANTHROPIC_MODEL", DEFAULT_MODEL),
        "max_tokens": MAX_TOKENS,
        "temperature": 0,
        "system": SYSTEM,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    req = urllib.request.Request(API_URL, data=body, method="POST")
    req.add_header("x-api-key", os.environ["ANTHROPIC_API_KEY"])
    req.add_header("anthropic-version", "2023-06-01")
    req.add_header("content-type", "application/json")
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())
    return "".join(part.get("text", "") for part in data.get("content", []))


def validate(raw_text, items):
    """Returns enrichment dict or raises ValueError with the reason."""
    text = raw_text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    parsed = json.loads(text)
    if not isinstance(parsed, list):
        raise ValueError("not a JSON array")
    expected = {item["id"]: item for item in items}
    result = {}
    for obj in parsed:
        if not isinstance(obj, dict) or set(obj) != {"id", "angle", "number", "syltech_tie"}:
            raise ValueError(f"bad keys: {sorted(obj) if isinstance(obj, dict) else type(obj)}")
        if obj["id"] not in expected:
            raise ValueError(f"unknown id {obj['id']!r}")
        item = expected[obj["id"]]
        clean = {}
        for field, limit in FIELD_LIMITS.items():
            value = str(obj[field]).strip()[:limit]
            clean[field] = value
        source_digits = digit_groups(item["title"] + " " + (item.get("summary") or ""))
        number_digits = digit_groups(clean["number"])
        if not clean["number"] or not number_digits or not number_digits <= source_digits:
            clean["number"] = NO_NUMBER  # deterministic hallucination guard
        result[obj["id"]] = clean
    missing = set(expected) - set(result)
    if missing:
        raise ValueError(f"missing ids: {sorted(missing)}")
    return result


def enrich_items(items, repo_root):
    """Returns (enrichment_map, status_string). Never raises on model failure."""
    payload = [{"id": i["id"], "title": i["title"],
                "summary": (i.get("summary") or "")[:600]} for i in items]
    prompt = (
        "VOICE RULES:\n" + (voice_capsule(repo_root) or "(capsule unavailable)") +
        "\n\nSTORIES:\n" + json.dumps(payload, indent=1)
    )
    last_error = None
    for attempt in range(MAX_ATTEMPTS):
        try:
            raw = call_api(prompt)
            return validate(raw, items), "ok"
        except Exception as exc:
            last_error = exc
            if attempt < MAX_ATTEMPTS - 1:
                time.sleep(lib.BACKOFF_BASE_SECONDS * (2 ** attempt))
    return {}, f"degraded: {str(last_error)[:200]}"


if __name__ == "__main__":
    # offline selftest for the validator (never calls the API)
    items = [{"id": "item1", "title": "GPU prices fall 30% in 2026",
              "summary": "from $4,000 to lower"}]
    good = validate('[{"id":"item1","angle":"a","number":"30%","syltech_tie":"t"}]', items)
    assert good["item1"]["number"] == "30%", good
    fabricated = validate('[{"id":"item1","angle":"a","number":"47%","syltech_tie":"t"}]', items)
    assert fabricated["item1"]["number"] == NO_NUMBER, fabricated
    empty = validate('[{"id":"item1","angle":"a","number":"","syltech_tie":"t"}]', items)
    assert empty["item1"]["number"] == NO_NUMBER
    try:
        validate('[{"id":"item1","angle":"a"}]', items)
        raise SystemExit("SELFTEST FAILED: bad keys accepted")
    except ValueError:
        pass
    print("SELFTEST OK (enrich validator)")
