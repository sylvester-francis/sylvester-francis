# The Syltech Operating System — runbook and specs

Three unattended loops that do the recurring work: find what to write,
keep the canonical context fresh, and count whether the whole thing is
working. Designed to be run by schedulers and small models with zero
judgment: every decision in this system is a number, a fixed list, or an
explicit rule. Where a rule runs out, the system fails loudly instead of
guessing.

**Design invariants** (violating any of these is a bug, not a choice):

1. stdlib-only Python — nothing to `pip install`, nothing to rot.
2. The core loops need zero AI. The only model call (scout enrichment) is
   optional and degrades to "—" without blocking anything.
3. Every scheduled run produces a visible artifact, even on a zero-result
   day. Silence always means breakage, never "nothing found".
4. Machines never publish, email, or send. Blast radius = GitHub issues in
   this repo + one machine-owned file (`context/RECENT.md`).
5. Every issue carries a self-check block of counts. "Looks good" is not
   a check; a count is.
6. Retries are capped and identical failures are collapsed into one loud,
   structured `automation-failure` issue.

---

## SPEC 1 — Morning Scout

**Vague version (before):** "I spend hours every week scanning AI news to
find what to write."

**Bounded version (now):**

> Every day at 09:30 UTC, fetch 8 fixed sources. Keep items ≤7 days old.
> Score each against three fixed keyword tiers (weights 3/2/1, title
> matches ×2, each keyword counted once) plus recency (+2 under 24h,
> +1 under 48h) and popularity (+1/+2/+3 at 50/100/300 points). A story
> qualifies at score ≥8 AND ≥1 tier-A/B match AND no negative keyword in
> the title. Drop anything delivered in the last 21 days, and anything
> whose title token-set overlaps a published post at Jaccard ≥0.5. File
> the top ≤3 as one GitHub issue labeled `scout-brief`.

- **Trigger:** `.github/workflows/scout.yml`, cron `30 9 * * *` (~05:30
  Toronto), plus manual `workflow_dispatch`.
- **Steps (zero-judgment order):** selftest → fetch → age-filter → score →
  batch-dedupe → seen-dedupe → own-post-dedupe → (optional enrich) →
  render → validate → file issue → persist state.
- **One-job sub-agents:** fetcher (URL → parsed items), scorer (item →
  number), deduper (items → fewer items), enricher (items → 3 annotation
  fields, isolated in `enrich.py`, deletable), renderer (data → fixed
  template), poster (body → issue).
- **Enrichment cage:** Haiku (`claude-haiku-4-5-20251001`), temperature 0,
  one call, JSON-array-only output, exact ids and keys enforced, and the
  "number" field must be verbatim-verifiable against the item's own
  title/summary digits or it is replaced with an instruction to go find
  one. 2 attempts, then the brief ships degraded.
- **Proof it worked (no human):** the issue's self-check block — sources
  ok/total, items scanned, qualified, deduped, delivered (0-3), dedupe
  memory size, enrichment status, rules hash. The validator refuses to
  ship a malformed brief (missing self-check, >3 items, non-http URLs,
  under-threshold leaks, >60k chars).
- **Exits:** per-source fetch = 3 attempts (2s/4s backoff); <2 sources ok
  = hard fail; issue POST = 3 attempts; state push = 4 attempts
  (2s/4s/8s/16s); job timeout 10 min. Hard fail ⇒ `automation-failure`
  issue with a JSON block (component, stage, error, counts) and exit 1.
  Max 5 open failure issues; further failures become comments.

**Numbers that define it:** threshold 8 · max 3 delivered · 21-day dedupe
window · 7-day item age · min 2 live sources · 8 sources · Jaccard 0.5.

## SPEC 2 — Context Pack

**Vague version (before):** "I keep re-explaining my voice to AI tools,
what Syltech does, and what my projects are."

**Bounded version (now):**

> The canonical explanation exists exactly once, in five files under
> `context/` with a manifest. Four are human-owned (`VOICE.md`,
> `SYLTECH.md`, `PROJECTS.md`, `PLAYBOOK.md`) and machines may quote but
> never edit them. One is machine-owned (`RECENT.md`: latest posts + live
> repo facts) and is regenerated every Sunday. A human-owned file older
> than 45 days (by last git commit) triggers a `pack-stale` issue naming
> the file and its age; the issue auto-closes when everything is fresh
> again. Injection points: `CLAUDE.md` for repo AI sessions, the scout's
> enrichment capsule (`VOICE.md` CAPSULE markers), and a copy-paste block
> in `PLAYBOOK.md` for external tools.

- **Trigger:** `.github/workflows/context-pack.yml`, cron `0 10 * * 0`.
- **Steps:** selftest → fetch Medium feed → fetch Substack (via rss2json)
  → fetch repo facts (fixed list in `automation/pack/repos.json`) →
  render `RECENT.md` → post-render check → write if changed → measure
  human-file ages → manage `pack-stale` issue.
- **Proof it worked:** the newest fetched post title must appear in the
  rendered file (hard check); `RECENT.md` carries its own self-check
  footer (source statuses, counts); the Monday scorecard independently
  reports pack max age.
- **Exits:** any single source may fail (visible in the file as "fetch
  failed this week"); ALL sources failing = hard fail ⇒ failure issue.
  Push retries ×4 with backoff.

**Numbers:** 45-day staleness limit · 5 posts per feed · 11 repos ·
1 stale issue at a time (updated in place, auto-closed).

## SPEC 3 — Monday Scorecard

**Vague version (before):** "Is the system — and my publishing cadence —
actually working?"

**Bounded version (now):**

> Every Monday at 11:00 UTC, compute seven counts and compare each to a
> fixed threshold. No model, no prose judgment: a table of numbers with
> green/yellow/red states, filed as one issue labeled `scorecard`.

| Row | Source | Green | Yellow | Red |
|---|---|---|---|---|
| Posts published (7d) | Medium + Substack feeds | ≥5 | 3-4 | ≤2 |
| Scout briefs delivered | `scout-brief` issues | 7 | 5-6 | <5 |
| Briefs unprocessed >48h | open `scout-brief` | ≤1 | 2-3 | ≥4 |
| Repeated story URLs | last 7 brief bodies | 0 | — | ≥1 |
| Automation failures (7d) | failure issues + red runs | 0 | 1 | ≥2 |
| Context pack max age | `git log` on human files | <45d | 45-60d | >60d |
| Scout source health | brief footers, min ratio | ≥80% | 60-79% | <60% |

- **Escalation rule:** posts row red two consecutive weeks ⇒ the issue
  title is prefixed with a double red flag and a banner states: the
  system is fine; the pipeline above it is starving.
- **Proof it worked:** self-check reports metrics computed N/7 with the
  named reason for any n/a row. >2 uncomputable rows = the scorecard
  declares ITSELF unreliable ⇒ hard fail, failure issue.
- **Exits:** each row degrades to a visible n/a rather than a fake value;
  job timeout 10 min.

---

## Activation (one-time, human)

1. Merge this branch to `main`. GitHub only runs scheduled workflows from
   the default branch — the merge is the on-switch. Labels self-create on
   first run.
2. *(Optional, enables enrichment)* Add an Anthropic API key: repo →
   Settings → Secrets and variables → Actions → New repository secret →
   name `ANTHROPIC_API_KEY`. Skipping this is fine — briefs ship without
   the Angle/Number/Tie lines. Cost when enabled: one Haiku call/day,
   roughly $1-2 per YEAR.
3. Review the two `[CONFIRM]`/`[EDIT ME]` blocks in `context/SYLTECH.md`
   and delete the markers. Paste the `PLAYBOOK.md` capsule into your
   external AI tools.
4. *(Recommended)* Repo → Settings → Notifications: ensure you receive
   Actions failure emails — that is the backstop if issue-filing itself
   ever breaks.

## Testing without waiting for the schedule

```bash
python3 automation/scout/scout.py --selftest      # offline logic checks
python3 automation/scout/scout.py --dry-run       # real fetch+score, prints brief, files nothing
python3 automation/scout/enrich.py                # enrichment validator selftest
python3 automation/pack/pack_refresh.py --selftest
python3 automation/pack/pack_refresh.py --dry-run
python3 automation/scorecard/scorecard.py --selftest
python3 automation/scorecard/scorecard.py --dry-run
```

Or run any workflow now: repo → Actions → pick one → "Run workflow".

## Changing the beat (the only regular maintenance)

- **Keywords/weights/threshold:** `automation/scout/keywords.json`.
- **Sources:** `automation/scout/sources.json` (must be reachable
  unauthenticated and parse as rss/atom/algolia/lobsters; verify with
  `--dry-run`).
- **Cadence targets:** `THRESHOLDS` at the top of
  `automation/scorecard/scorecard.py`.
- **Repo list:** `automation/pack/repos.json`.

Quarterly review ritual: `context/PLAYBOOK.md`.

## When something fails

1. An issue labeled `automation-failure` appears (or a red run + GitHub's
   failure email if even that broke). The JSON block names component,
   stage, and error.
2. Fix is usually one of: a dead source (delete its entry in
   `sources.json`), a feed format change (the parser is 40 lines in
   `automation/lib.py`), or a GitHub API hiccup (re-run from the Actions
   tab).
3. Close the failure issue after the next green run.

## Silent-failure watchlist (how this system lies, and where to look)

1. **Source rot:** feeds die one by one; briefs keep arriving, quietly
   narrower. You will see it in the brief footer ("Sources fetched: 4/8")
   and the scorecard's source-health row going yellow→red.
2. **Schema-valid hallucination:** enrichment returns a plausible but
   wrong number. The verbatim-digit check strips most of these; the
   playbook rule ("open the source before publishing a number") is the
   permanent backstop. If "The number:" ever disagrees with the linked
   page, the cage has a hole — file it.
3. **Beat drift:** keywords stay, your interests move; delivery counts
   stay green while usefulness decays. The canary is the "briefs
   unprocessed" row rising, plus your own quarterly review. No count can
   save you from skipping this ritual — that is the one loop with a human
   inside by design.
