<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:6366f1,50:06b6d4,100:22c55e&height=280&section=header&text=Sylvester%20Francis&fontSize=75&fontAlignY=32&desc=Principal%20Platform%20Engineer%20%E2%80%A2%20Infrastructure%20%E2%80%A2%20Open%20Source&descAlignY=52&descSize=18&fontColor=ffffff&animation=fadeIn" width="100%"/>

<br/>

<a href="https://sylvesterranjithfrancis.com"><img src="https://img.shields.io/badge/Portfolio-6366f1?style=for-the-badge&logo=googlechrome&logoColor=white"/></a>
<a href="https://www.linkedin.com/in/sylvesterranjith/"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white"/></a>
<a href="https://medium.com/@sylvesterranjithfrancis"><img src="https://img.shields.io/badge/Medium-000000?style=for-the-badge&logo=medium&logoColor=white"/></a>
<a href="https://techwithsyl.substack.com"><img src="https://img.shields.io/badge/Substack-FF6719?style=for-the-badge&logo=substack&logoColor=white"/></a>
<a href="https://www.youtube.com/@TechWithSyl"><img src="https://img.shields.io/badge/TechWithSyl-FF0000?style=for-the-badge&logo=youtube&logoColor=white"/></a>
<a href="https://topmate.io/sylvester_francis"><img src="https://img.shields.io/badge/Book%20a%20Call-22c55e?style=for-the-badge&logo=googlecalendar&logoColor=white"/></a>
<a href="mailto:sylvesterranjithfrancis@gmail.com"><img src="https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white"/></a>

<br/><br/>

<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=700&size=22&duration=3000&pause=1000&color=818CF8&center=true&vCenter=true&repeat=true&width=680&height=45&lines=8%2B+years+in+platform+and+infrastructure+engineering;Go+%7C+Python+%7C+Kubernetes+%7C+OpenStack+%7C+Ory;Self-service+platforms+and+golden-image+pipelines;Open-source+tooling+for+infra+and+agentic+AI" alt="Typing SVG" />

<br/>

<img src="https://komarev.com/ghpvc/?username=sylvester-francis&style=for-the-badge&color=6366f1&label=PROFILE+VIEWS"/>

</div>

<br/>

## `systemctl status sylvester.platform`

```ini
● sylvester.platform - Principal Platform Engineer
     Loaded: loaded (8+ years; platform and infrastructure engineering)
     Active: running
   Location: Waterloo, ON, Canada
    Primary: Go        Also: TypeScript, Python, Rust
       Owns: golden-image platform, authorization, orchestration
    Writing: open-source tooling and engineering deep dives
```

I am a Principal Platform Engineer with 8+ years in platform and infrastructure
engineering. I architected a self-service developer platform from the ground up to drive a
large-scale VMware vSphere to OpenStack migration, and I now lead an enterprise
golden-image platform and own its identity and authorization layer. I work primarily in Go,
build open-source tooling, and write for an expert engineering audience.

<details>
<summary><code>$ uname -a   # background, community, awards</code></summary>

<br/>

- Master's in CS from VIT
- Big Data and Security certifications from Conestoga (High Distinction)
- Published ML researcher (brain tumor prediction using FCNNs)
- Built ETL pipelines and data engineering systems at OpenText
- 4K+ LinkedIn followers, 500+ professional connections
- Outstanding Achievement Award (OpenText), High Distinction in Big Data and in Security, ML Engineer Nanodegree (Udacity)

</details>

<br/>

---

<br/>

<div align="center">

## Control Plane

</div>

<br/>

```mermaid
flowchart LR
  dev([Developers]) --> idp["Self-service IDP"]
  authz["Authorization<br/>Ory Keto + Kratos"] -. guards .-> idp
  idp --> build["Build<br/>Dagger"]
  builders["Ephemeral builders<br/>OpenStack + AWS EC2"] --> build
  build --> scan["Scan<br/>Trivy, OpenSCAP"]
  scan --> gate{"Approval<br/>gate"}
  gate --> promote["Promote"]
  promote --> glance[("Glance<br/>multi-region")]
  dbos["DBOS<br/>durable workflows"] -. orchestrates .-> build
  otel["OpenTelemetry"] -. observes .-> idp

  classDef cp fill:#1e1b4b,stroke:#6366f1,color:#ffffff;
  classDef pipe fill:#0b3b44,stroke:#06b6d4,color:#ffffff;
  classDef side fill:#0d1117,stroke:#22c55e,color:#ffffff;
  class idp,authz cp;
  class build,scan,gate,promote,glance pipe;
  class dev,builders,dbos,otel side;
```

<br/>

| Component | State | What it does |
|---|:---:|---|
| **golden-image platform** | ![running](https://img.shields.io/badge/running-22c55e?style=flat-square) | Build, scan (Trivy, OpenSCAP), mandatory approval gate, promote, and multi-region OpenStack Glance distribution. Dual-cloud ephemeral builders (OpenStack and AWS EC2), Dagger-executed builds, DBOS durable workflows, and reliability hardening. |
| **authorization platform** | ![running](https://img.shields.io/badge/running-22c55e?style=flat-square) | Hierarchical RBAC on Ory Keto relation tuples, multi-tenant hierarchy, check-time inheritance via Ory Permission Language, a live single-writer topology sync from OpenStack, identity and OIDC SSO on Ory Kratos, and audit logging. |
| **platform orchestration** | ![running](https://img.shields.io/badge/running-22c55e?style=flat-square) | A self-service internal developer platform, a Go OpenStack gateway (gophercloud), OpenTofu IaC on Kubernetes, and OpenTelemetry observability. |

<br/>

---

<br/>

<div align="center">

## Runtime

</div>

<br/>

<table align="center">
<tr>
<td align="center" width="25%">

<h4>Languages</h4>

<img src="https://skillicons.dev/icons?i=go,typescript,python,rust&perline=4&theme=dark" />

</td>
<td align="center" width="25%">

<h4>Cloud & Infrastructure</h4>

<img src="https://skillicons.dev/icons?i=kubernetes,aws,azure,docker&perline=4&theme=dark" />

<br/><br/>

![OpenStack](https://img.shields.io/badge/OpenStack-ED1944?style=flat-square&logo=openstack&logoColor=white)
![OpenTofu](https://img.shields.io/badge/OpenTofu-FFDA18?style=flat-square&logo=opentofu&logoColor=black)
![Vault](https://img.shields.io/badge/Vault-000?style=flat-square&logo=vault&logoColor=white)

</td>
<td align="center" width="25%">

<h4>Platform Tooling</h4>

![Dagger](https://img.shields.io/badge/Dagger-131226?style=flat-square&logo=dagger&logoColor=white)
![gophercloud](https://img.shields.io/badge/gophercloud-00ADD8?style=flat-square&logo=go&logoColor=white)
![Ory](https://img.shields.io/badge/Ory-000?style=flat-square&logo=ory&logoColor=white)
![Trivy](https://img.shields.io/badge/Trivy-1904DA?style=flat-square&logo=aqua&logoColor=white)

</td>
<td align="center" width="25%">

<h4>Backend & AI</h4>

<img src="https://skillicons.dev/icons?i=nestjs,react,nodejs,postgres&perline=4&theme=dark" />

<br/><br/>

![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-000?style=flat-square&logo=opentelemetry&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat-square&logo=langchain&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=flat-square&logo=langchain&logoColor=white)
![Claude](https://img.shields.io/badge/Claude_API-191919?style=flat-square&logo=anthropic&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI_API-412991?style=flat-square&logo=openai&logoColor=white)

</td>
</tr>
</table>

<br/>

---

<br/>

<div align="center">

## Open Source

</div>

<br/>

<table>
<tr>
<td width="33%" valign="top">

<h3 align="center"><a href="https://usewatchdog.dev">WatchDog</a></h3>

<div align="center">

![Stars](https://img.shields.io/github/stars/sylvester-francis/Watchdog?style=for-the-badge&color=f59e0b&label=Stars&logo=github)

![Go](https://img.shields.io/badge/Go-00ADD8?style=flat-square&logo=go&logoColor=white)
![AGPL-3.0](https://img.shields.io/badge/AGPL--3.0-3DA639?style=flat-square&logo=gnu&logoColor=white)
![WebSocket](https://img.shields.io/badge/WebSocket-010101?style=flat-square&logo=socketdotio&logoColor=white)

</div>

Infrastructure monitoring with a hub-and-spoke WebSocket architecture. A central hub serves
the dashboard, and lightweight agents report from private networks over outbound-only
connections.

<div align="center">

<a href="https://usewatchdog.dev">usewatchdog.dev</a> &middot; <a href="https://github.com/sylvester-francis/Watchdog">GitHub</a>

</div>

</td>
<td width="33%" valign="top">

<h3 align="center"><a href="https://github.com/sylvester-francis/Sentry">Sentry</a></h3>

<div align="center">

![Stars](https://img.shields.io/github/stars/sylvester-francis/Sentry?style=for-the-badge&color=f59e0b&label=Stars&logo=github)

![Go](https://img.shields.io/badge/Go-00ADD8?style=flat-square&logo=go&logoColor=white)
![Dagger](https://img.shields.io/badge/Dagger-131226?style=flat-square&logo=dagger&logoColor=white)

</div>

Container-security Dagger module that integrates Trivy, Grype, and Snyk to run vulnerability
scans inside CI/CD pipelines and report findings.

<div align="center">

<a href="https://github.com/sylvester-francis/Sentry">GitHub</a>

</div>

</td>
<td width="33%" valign="top">

<h3 align="center"><a href="https://github.com/sylvester-francis/ctxforge">ctxforge</a></h3>

<div align="center">

![Stars](https://img.shields.io/github/stars/sylvester-francis/ctxforge?style=for-the-badge&color=f59e0b&label=Stars&logo=github)

![Rust](https://img.shields.io/badge/Rust-000?style=flat-square&logo=rust&logoColor=white)

</div>

CLI for manifest-driven LLM context bundles for agentic AI. Assembles reproducible context
from a declarative manifest.

<div align="center">

<a href="https://github.com/sylvester-francis/ctxforge">GitHub</a>

</div>

</td>
</tr>
</table>

<br/>

<br/>

---

<br/>

<div align="center">

## More Projects

</div>

<br/>

<table>
<tr>
<td width="50%" valign="top">

<h3 align="center"><a href="https://github.com/sylvester-francis/Automated-Document-Compliance-Auditor">Compliance Auditor</a></h3>

<div align="center">

![Stars](https://img.shields.io/github/stars/sylvester-francis/Automated-Document-Compliance-Auditor?style=for-the-badge&color=f59e0b&label=Stars&logo=github)

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000?style=flat-square&logo=flask&logoColor=white)
![Claude](https://img.shields.io/badge/Claude_API-191919?style=flat-square&logo=anthropic&logoColor=white)

</div>

Audits documents for GDPR and HIPAA compliance. Identifies violations through pattern
matching and LLM analysis, then suggests remediations.

</td>
<td width="50%" valign="top">

<h3 align="center"><a href="https://github.com/sylvester-francis/DocumentationGenerator">Documentation Generator</a></h3>

<div align="center">

![Stars](https://img.shields.io/github/stars/sylvester-francis/DocumentationGenerator?style=for-the-badge&color=f59e0b&label=Stars&logo=github)

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=flat-square&logo=langchain&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)

</div>

Multi-agent system on LangGraph that fetches code from GitHub, analyzes structure, generates
technical docs, and syncs them to Confluence.

</td>
</tr>
<tr>
<td width="50%" valign="top">

<h3 align="center"><a href="https://github.com/sylvester-francis/n8n-selfhoster">n8n Self-Hoster</a></h3>

<div align="center">

![Stars](https://img.shields.io/github/stars/sylvester-francis/n8n-selfhoster?style=for-the-badge&color=f59e0b&label=Stars&logo=github)

![Shell](https://img.shields.io/badge/Shell-4EAA25?style=flat-square&logo=gnubash&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)

</div>

Ubuntu installer for n8n with Docker, PostgreSQL, HTTPS, security hardening, progress
tracking, and error recovery.

</td>
<td width="50%" valign="top">

<h3 align="center"><a href="https://github.com/sylvester-francis/slm-typescript-model">SLM TypeScript Model</a></h3>

<div align="center">

![Stars](https://img.shields.io/github/stars/sylvester-francis/slm-typescript-model?style=for-the-badge&color=f59e0b&label=Stars&logo=github)

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![HuggingFace](https://img.shields.io/badge/HuggingFace-FFD21E?style=flat-square&logo=huggingface&logoColor=black)
![LoRA](https://img.shields.io/badge/LoRA-FF6F00?style=flat-square&logo=pytorch&logoColor=white)

</div>

Small language models (1.5B to 7B) with LoRA fine-tuning for TypeScript code generation
across React, Next.js, Angular, and Node.js.

</td>
</tr>
<tr>
<td width="50%" valign="top">

<h3 align="center"><a href="https://github.com/sylvester-francis/ota-deploy-tracker">OTA Deploy Tracker</a></h3>

<div align="center">

![Stars](https://img.shields.io/github/stars/sylvester-francis/ota-deploy-tracker?style=for-the-badge&color=f59e0b&label=Stars&logo=github)

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=flat-square&logo=prometheus&logoColor=white)

</div>

Kubernetes deployment manager with a FastAPI backend, Streamlit dashboard, and Prometheus
monitoring for tracking progressive rollouts.

</td>
<td width="50%" valign="top">

<h3 align="center"><a href="https://github.com/sylvester-francis/Lintelligence">Lintelligence</a></h3>

<div align="center">

![Stars](https://img.shields.io/github/stars/sylvester-francis/Lintelligence?style=for-the-badge&color=f59e0b&label=Stars&logo=github)

![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![NestJS](https://img.shields.io/badge/NestJS-E0234E?style=flat-square&logo=nestjs&logoColor=white)
![GPT4](https://img.shields.io/badge/GPT--4-412991?style=flat-square&logo=openai&logoColor=white)

</div>

Reviews GitHub pull requests with GPT-4. Detects code smells, security issues, and
anti-patterns, then posts inline feedback.

</td>
</tr>
<tr>
<td width="50%" valign="top">

<h3 align="center"><a href="https://github.com/sylvester-francis/Resource-Reserver">Resource Reserver</a></h3>

<div align="center">

![Stars](https://img.shields.io/github/stars/sylvester-francis/Resource-Reserver?style=for-the-badge&color=f59e0b&label=Stars&logo=github)

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Typer](https://img.shields.io/badge/Typer-009688?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)

</div>

CLI booking system with JWT auth, conflict resolution, and reservation management. Built with
Python Typer and a FastAPI backend.

</td>
<td width="50%" valign="top">

<h3 align="center"><a href="https://github.com/sylvester-francis/taskflow">TaskFlow</a></h3>

<div align="center">

![Stars](https://img.shields.io/github/stars/sylvester-francis/taskflow?style=for-the-badge&color=f59e0b&label=Stars&logo=github)

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=flat-square&logo=kubernetes&logoColor=white)

</div>

Task tracking with JWT authentication, role-based access control, and Kubernetes manifests.
Built with FastAPI and PostgreSQL.

</td>
</tr>
</table>

<br/>

---

<br/>

<div align="center">

## Telemetry

<br/>

<img src="https://github-readme-stats-sigma-five.vercel.app/api?username=sylvester-francis&show_icons=true&theme=tokyonight&hide_border=true&bg_color=0d1117&title_color=818cf8&icon_color=22c55e&text_color=c9d1d9&count_private=true&include_all_commits=true&ring_color=6366f1" width="49%"/>
<img src="https://github-readme-stats-sigma-five.vercel.app/api/top-langs/?username=sylvester-francis&layout=compact&theme=tokyonight&hide_border=true&bg_color=0d1117&title_color=818cf8&text_color=c9d1d9&langs_count=8" width="42%"/>

<br/><br/>

<img src="https://streak-stats.demolab.com/?user=sylvester-francis&theme=tokyonight&hide_border=true&background=0d1117&ring=6366f1&fire=f59e0b&currStreakLabel=818cf8&sideLabels=c9d1d9&dates=555555&stroke=222222" width="55%"/>

<br/><br/>

<img src="https://github-readme-activity-graph.vercel.app/graph?username=sylvester-francis&bg_color=0d1117&color=818cf8&line=6366f1&point=22c55e&area=true&area_color=6366f1&hide_border=true&custom_title=Contribution%20Activity" width="92%"/>

</div>

<br/>

---

<br/>

<div align="center">

## Writing & Content

</div>

<br/>

<div align="center">

| Platform | What I write about |
|:---:|:---|
| <a href="https://medium.com/@sylvesterranjithfrancis"><img src="https://img.shields.io/badge/Medium-000000?style=for-the-badge&logo=medium&logoColor=white" height="28"/></a> | Platform engineering, infrastructure, and agent design for an expert audience |
| <a href="https://techwithsyl.substack.com"><img src="https://img.shields.io/badge/Substack-FF6719?style=for-the-badge&logo=substack&logoColor=white" height="28"/></a> | DevOps tooling, container security, and Dagger deep dives |
| <a href="https://www.linkedin.com/in/sylvesterranjith/"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" height="28"/></a> | Engineering notes, industry trends, and developer mentoring |
| <a href="https://www.youtube.com/@TechWithSyl"><img src="https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white" height="28"/></a> | Tutorials, project walkthroughs, and coding sessions |

</div>

<br/>

---

<br/>

<div align="center">

## Services & Mentoring

</div>

<br/>

<div align="center">

```
+---------------------------+---------------------------+---------------------------+
|     PLATFORM & INFRA      |   CLOUD ARCHITECTURE      |    DEVOPS & SECURITY      |
|                           |                           |                           |
|  Self-service platforms,  |  OpenStack, AWS, Azure    |  CI/CD, container         |
|  golden-image pipelines,  |  infrastructure and IaC   |  security, monitoring,    |
|  and developer tooling    |  on Kubernetes            |  and deploy automation    |
+---------------------------+---------------------------+---------------------------+
|    CAREER MENTORING       |      CODE REVIEW          |  TECHNICAL CONSULTING     |
|                           |                           |                           |
|  1:1 sessions for         |  Reviews, best            |  System architecture      |
|  career transitions,      |  practices, and           |  and technology           |
|  interview prep, resume   |  technical mentorship     |  strategy for teams       |
+---------------------------+---------------------------+---------------------------+
```

<br/>

<a href="https://topmate.io/sylvester_francis"><img src="https://img.shields.io/badge/Schedule%20on%20Topmate-22c55e?style=for-the-badge&logo=googlecalendar&logoColor=white&labelColor=16a34a" height="40"/></a>

</div>

<br/>

---

<br/>

<div align="center">

### Let's connect

<br/>

<a href="mailto:sylvesterranjithfrancis@gmail.com"><img src="https://img.shields.io/badge/Email_Me-D14836?style=for-the-badge&logo=gmail&logoColor=white"/></a>
<a href="https://www.linkedin.com/in/sylvesterranjith/"><img src="https://img.shields.io/badge/Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white"/></a>
<a href="https://topmate.io/sylvester_francis"><img src="https://img.shields.io/badge/Book_a_Call-22c55e?style=for-the-badge&logo=googlecalendar&logoColor=white"/></a>
<a href="https://github.com/sylvester-francis"><img src="https://img.shields.io/badge/Follow-181717?style=for-the-badge&logo=github&logoColor=white"/></a>
<a href="https://instagram.com/techwithsyl"><img src="https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white"/></a>

<br/><br/>

**Based in Waterloo, ON, Canada**

<br/>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:6366f1,50:06b6d4,100:22c55e&height=130&section=footer" width="100%"/>

</div>
