# PLAYBOOK — how the human and the machines share this system

Human-owned. This is the operating manual. The machine specs live in
`automation/README.md`; this file is your side of the contract.

## The system in one screen

| Loop | When | What arrives | Your move |
|---|---|---|---|
| Morning scout | Daily ~05:30 Toronto | Issue `Scout · <date>`: 0-3 scored angles | Pick ≤1, write, close the issue |
| Context pack | Sundays | `RECENT.md` refreshed; `pack-stale` issue if files age past 45d | Edit the named file |
| Scorecard | Mondays ~07:00 | Issue with 7 numbers vs targets | Read, act on reds, close |

Labels: `scout-brief` (daily angles) · `scorecard` (weekly numbers) ·
`pack-stale` (context needs you) · `automation-failure` (a machine broke).

## Daily ritual (under 30 minutes)

1. Open today's `Scout ·` issue.
2. Pick at most one angle — or none. Zero is a valid day.
3. **Open the source link before writing. Verify the number yourself.**
   The machine's "The number:" line is a pointer, not a fact.
4. Write in voice (see `VOICE.md`), publish, add the CTA per `SYLTECH.md`.
5. Close the issue. Closing means "processed", even when you picked nothing.
   (The Monday scorecard counts briefs left open past 48h.)

## Weekly ritual (Monday, 10 minutes)

Read the scorecard. One red row: fix the thing it names. The same row red
two weeks running: change the system (thresholds, keywords, sources — all
one-file edits), not the effort.

## Quarterly ritual (first Monday of Jan/Apr/Jul/Oct, 15 minutes)

The beat drifts; keyword lists do not. Skim the last ~12 briefs: which
delivered angles did you actually use? Prune keywords that only ever
surfaced skipped stories; add the words you now see in stories you wanted.
Edit `automation/scout/keywords.json` (tiers and negatives) and
`automation/scout/sources.json`. Commit. Done.

## Hard rules (the machines are built to obey these — hold them to it)

- Machines never publish, post, email, or send anything anywhere.
  They file GitHub issues and edit `context/RECENT.md`. That is the
  entire blast radius.
- Machines never edit `VOICE.md`, `SYLTECH.md`, `PROJECTS.md`, `PLAYBOOK.md`.
- No number goes from a brief into a published post unverified.
- Money decisions (pricing, proposals) are never machine-drafted from
  guesswork — `SYLTECH.md` deliberately holds those as `[EDIT ME]` until
  you write them.

## Copy-paste capsule for external AI tools

Paste the block below into: ChatGPT → Settings → Personalization → Custom
Instructions ("How would you like ChatGPT to respond?"), or a Claude.ai
Project → Project knowledge / custom instructions, or any tool's system
prompt slot. Refresh your paste when you edit the pack (the scorecard's
"pack age" row reminds you).

```text
You are assisting Sylvester Francis. Standing context:

WHO: Principal-level platform engineer (Go, Kubernetes, OpenStack; golden
images; Ory-based identity/RBAC). Founder of Syltech AI Systems, Inc.
(Kitchener-Waterloo, ON) — AI systems, platform infrastructure, and
full-stack builds for small and mid-size businesses. Writes daily for
expert engineers: agent engineering and AI infrastructure economics.
Flagship OSS: WatchDog (outbound-only fleet monitoring, Go), Sentry
(Trivy/Grype/Snyk container scanning as a Dagger module), ctxforge
(manifest-driven reproducible LLM context, Rust).

VOICE (non-negotiable): No contractions. Short declarative sentences;
land big points in 3-6 words. Every claim carries a real number with its
source; never invent or convert figures — a missing number is stated as
missing. Titles: two clauses split by a period, or a number-forward
promise, under 80 chars. Open with the thesis; strongest number in the
first five sentences. First-person practitioner; one credential line max.
Pick a side; end with "what I would watch", never a recap. Audience is
expert — explain costs and failure modes, never basics. Banned: emoji,
exclamation marks, "delve", "game-changer", "revolutionary", hype.

DEFAULT CTA: "Book a call — https://topmate.io/sylvester_francis" or
sylvesterranjithfrancis@gmail.com.
```
