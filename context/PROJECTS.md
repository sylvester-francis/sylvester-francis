# PROJECTS — what the projects are and why a buyer should care

Human-owned. Machines quote this file; they never edit it. Live numbers
(stars, last push) are NOT kept here — `RECENT.md` carries those weekly so
this file never rots on facts. This file carries meaning.

## Flagships

### WatchDog — infrastructure monitoring · Go · AGPL-3.0
Hub-and-spoke WebSocket monitoring: a central hub serves the dashboard;
lightweight agents report from private networks over outbound-only
connections.
**Buyer line:** monitor fleets behind firewalls without opening a single
inbound port.
Links: https://usewatchdog.dev · https://github.com/sylvester-francis/Watchdog

### Sentry — container security in CI · Go · Dagger
A Dagger module integrating Trivy, Grype, and Snyk to run vulnerability
scans inside any CI/CD pipeline and report findings.
**Buyer line:** a container-security gate added to an existing pipeline in
minutes, not a platform migration.
Links: https://github.com/sylvester-francis/Sentry

### ctxforge — reproducible LLM context · Rust
CLI for manifest-driven LLM context bundles: assembles reproducible context
for agentic AI from a declarative manifest.
**Buyer line:** repeatable context makes agent behavior predictable — the
same philosophy that runs this repo's own `context/` pack.
Links: https://github.com/sylvester-francis/ctxforge

## Supporting cast (one line each)

- **Compliance Auditor** — GDPR/HIPAA document auditing with LLM analysis.
- **Documentation Generator** — LangGraph multi-agent docs synced to Confluence.
- **n8n Self-Hoster** — Ubuntu installer for n8n with Docker, PostgreSQL, HTTPS.
- **SLM TypeScript Model** — LoRA fine-tuned small models for TypeScript codegen.
- **OTA Deploy Tracker** — progressive Kubernetes rollouts, FastAPI + Prometheus.
- **Lintelligence** — GitHub PR review with GPT-4.
- **Resource Reserver** — CLI booking system (JWT, Typer, FastAPI).
- **TaskFlow** — task tracking (JWT, FastAPI, Kubernetes manifests).

## Standard explanations (paste, do not re-derive)

**"What is the golden-image platform?"** — Build, scan (Trivy, OpenSCAP),
mandatory approval gate, promote, multi-region OpenStack Glance
distribution. Dual-cloud ephemeral builders on OpenStack and AWS EC2,
Dagger-executed builds, DBOS durable workflows.

**"What is the authorization platform?"** — Hierarchical RBAC on Ory Keto
relation tuples, multi-tenant hierarchy, check-time inheritance via Ory
Permission Language, live single-writer topology sync from OpenStack,
identity and OIDC SSO on Ory Kratos, audit logging.
