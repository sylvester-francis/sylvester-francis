# CLAUDE.md — standing orders for any AI session in this repo

This is Sylvester Francis's profile repo AND the home of his automation
system. Read this before doing anything.

## Load context first

For ANY writing, drafting, positioning, pitch, bio, or marketing task:
read `context/manifest.yaml`, then load the pack in its load order
(`VOICE.md`, `SYLTECH.md`, `PROJECTS.md`, `RECENT.md`). Do not ask the
user to re-explain who he is, what Syltech does, or what his projects are
— that is what the pack is for. Follow `VOICE.md` exactly; its banned list
is absolute.

## Ownership rules (do not violate)

- `context/RECENT.md` is machine-generated weekly. Never hand-edit it.
- `context/VOICE.md`, `SYLTECH.md`, `PROJECTS.md`, `PLAYBOOK.md` are
  human-owned. Edit them only when the user explicitly asks.
- `automation/**` and `.github/workflows/**` are load-bearing and run
  unattended. Change them only on explicit request, keep stdlib-only
  Python, keep every threshold explicit, and run the selftests
  (`python3 <script> --selftest`) before committing.

## The automation map

| Workflow | Schedule (UTC) | Script | Output |
|---|---|---|---|
| `scout.yml` | daily 09:30 | `automation/scout/scout.py` | issue `Scout · <date>` (`scout-brief`) |
| `context-pack.yml` | Sun 10:00 | `automation/pack/pack_refresh.py` | `context/RECENT.md` + `pack-stale` issues |
| `scorecard.yml` | Mon 11:00 | `automation/scorecard/scorecard.py` | issue `Scorecard · …` (`scorecard`) |

Failures arrive as issues labeled `automation-failure` with a JSON block.
Full specs and ops: `automation/README.md`.

## Behavior rules

- Never publish, post, email, or send content anywhere on the user's
  behalf. Drafts and issues only.
- Never put a number in a draft that is not verbatim from a source the
  user can open.
- Do not create pull requests unless explicitly asked.
