<div align="center">

# Daniel Manzela

**Builder of Autonomous AI Systems**

*Ten years, six systems shipped. Today: a fail-closed AI pipeline serving 11 enterprise clients across 5 countries.*

<br>

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat&logo=linkedin&logoColor=white)](https://linkedin.com/in/manzela)
[![Google Cloud Skills](https://img.shields.io/badge/Google_Cloud-32_Credentials-4285F4?style=flat&logo=google-cloud&logoColor=white)](https://partner.skills.google/public_profiles/69fa3af8-3032-4a04-a818-f7277009c3a9)
[![Pipeline Observatory](https://img.shields.io/badge/Live_Demo-Pipeline_Observatory-000?style=flat&logo=github-pages&logoColor=white)](https://manzela.github.io/pipeline-observatory/)

</div>

---

### What I Build

I design and operate **end-to-end autonomous AI systems** — from zero-to-one architecture through production. My work sits at the intersection of multi-agent orchestration, fail-closed safety, and LLM evaluation. The systems I build run with **zero human oversight** at enterprise scale.

**Current system in production (TNG Shopper, 2024 → present):**
- **11 enterprise clients** across **5 countries** (ES · PT · IL · US · MX) — **~10.5M product pages under autonomous management** at **$0.0006 / page**
- **7-node multi-agent directed acyclic graph** with **~73.5M sub-agent operations per run** · 234 managed websites
- **Gemma 4 26B-A4B Mixture-of-Experts** on self-hosted vLLM with PagedAttention inference. Multi-Low-Rank-Adaptation research documented in the [forensic runbook](https://github.com/Manzela/gemma4-vllm-deployment).
- **Originality, Relevance, Accuracy, Value** — four-axis multi-model evaluation with fail-closed policy at **68.9% pass rate by design** · Deterministic Evaluation and Monitoring Audit System enforcing every boundary

**Ten years to get here.** Six projects. The pattern: how to unblock human-dependencies. See the [profile time-spine →](https://manzela.github.io/Manzela/#arc).

---

### System Architecture

```mermaid
graph LR
  subgraph Inference["Inference Layer"]
    MoE["Gemma 4 26B MoE<br/>vLLM · PagedAttention"]
    L1["LoRA α"]
    L2["LoRA β"]
    L3["LoRA γ"]
    MoE --> L1 & L2 & L3
  end

  subgraph DAG["7-Node Autonomous Pipeline"]
    N1["City DNA<br/><sub>Context</sub>"] --> N2["Normalizer<br/><sub>4 sub-agents</sub>"]
    N2 --> N3["Synonyms<br/><sub>Expand</sub>"]
    N3 --> N4["SV Gate<br/><sub>Filter</sub>"]
    N4 --> N5["Writer<br/><sub>Generate</sub>"]
    N5 --> N6["Validator<br/><sub>O-R-A-V</sub>"]
    N6 --> N7["Features<br/><sub>Vectorize</sub>"]
  end

  subgraph Eval["Evaluation & Safety"]
    ORAV["O-R-A-V Judge<br/><sub>Multi-Model Scoring</sub>"]
    DEMAS["DEMAS Audit<br/><sub>JIT · Fail-Closed</sub>"]
  end

  L1 & L2 & L3 --> N1
  N6 --> ORAV
  DEMAS -.->|"intercept at<br/>every boundary"| N1 & N2 & N3 & N4 & N5 & N6 & N7
  ORAV -.->|"RL feedback<br/>prompt mutation"| N5

  style MoE fill:#1a1a2e,stroke:#0A84FF,color:#fff
  style ORAV fill:#1a1a2e,stroke:#30D158,color:#fff
  style DEMAS fill:#1a1a2e,stroke:#FFD60A,color:#fff
```

<details>
<summary><b>Node Anatomy — Each node contains multiple sub-agents</b></summary>

Every directed-acyclic-graph node is a bounded ecosystem, not a single LLM call:

| Layer | Role | Example |
|---|---|---|
| **Deterministic Gate** | Schema validation, type coercion, regex | Pydantic, Python AST |
| **Probabilistic Agent** | Semantic extraction, classification | Gemini Vision, SLM |
| **Autonomy Layer** | Originality-Relevance-Accuracy-Value scoring, confidence thresholds | Multi-model consensus |
| **Memory** | Long-term state, prompt cache mutation | Redis LTM, Firestore |

The deterministic gate always fires first. The LLM is invoked **only if the gate passes**.

</details>

---

### Technical Focus

<div align="center">

**AI & ML**

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Gemma](https://img.shields.io/badge/Gemma_4-8E75B2?style=flat-square&logo=google&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-4285F4?style=flat-square&logo=google&logoColor=white)
![vLLM](https://img.shields.io/badge/vLLM-000000?style=flat-square)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat-square)

**Infrastructure & MLOps**

![GCP](https://img.shields.io/badge/Google_Cloud-4285F4?style=flat-square&logo=google-cloud&logoColor=white)
![Vertex AI](https://img.shields.io/badge/Vertex_AI-4285F4?style=flat-square&logo=google-cloud&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis&logoColor=white)
![BigQuery](https://img.shields.io/badge/BigQuery-669DF6?style=flat-square&logo=google-cloud&logoColor=white)
![Firestore](https://img.shields.io/badge/Firestore-FFCA28?style=flat-square&logo=firebase&logoColor=black)

**Evaluation & Safety**

![Multi-Agent](https://img.shields.io/badge/Multi--Agent_DAGs-000?style=flat-square)
![vLLM](https://img.shields.io/badge/vLLM_PagedAttention-000?style=flat-square)
![Fail-Closed](https://img.shields.io/badge/Fail--Closed_Safety-000?style=flat-square)
![RLHF](https://img.shields.io/badge/Closed--Loop_RL-000?style=flat-square)

</div>

---

### Featured Work

#### The Arc — six case studies, in chronological order

| Year | Project | What it proved |
|---|---|---|
| 2016 | [**Asset**](https://manzela.github.io/Manzela/asset/) <sub>(Sept 2016 — 2019)</sub> | Three years of solo contractor work for new-stage startups: web setups, ERP→web ETL by hand, spreadsheet automation, business plans. *The data-transformation reps every later pipeline compounded on.* |
| 2019 | [**Data Mining**](https://manzela.github.io/Manzela/data-mining/) <sub>(Feb 2019 — Jul 2020)</sub> | Five-stage manually-orchestrated pipeline for an Israeli financial-services firm. ₪50M+ in new Assets Under Management. *A pipeline is a series of filters, not a series of steps.* |
| 2020 | [**Seller App**](https://manzela.github.io/Manzela/seller-app/) <sub>(Jan 2020 — Apr 2024)</sub> | Computer vision for retail digitization. 3 computer-vision generations · 60M+ canonical Stock-Keeping Units · $10K Monthly Recurring Revenue plateau. The architectural origin of retrieval-grounded computer vision. |
| 2020 | [**Tasko AI**](https://manzela.github.io/Manzela/tasko-ai/) <sub>(Oct 2020 — Dec 2023)</sub> | Production agentic system before the term existed. 21,102 labeled tasks · 153 clients · 1,561 intent patterns · 4-layer Classify / Retrieve / Execute / Verify. |
| 2024 | [**Elysium**](https://manzela.github.io/Manzela/elysium/) <sub>(2024 — 2025, paused-pending-Pipeline)</sub> | Physical-Context AI for Retail. 13 brands validated · 15,600+ store locations · 15 patent claims (3 independent + 12 dependent). |
| 2024 | [**Pipeline Observatory**](https://manzela.github.io/pipeline-observatory/) <sub>(2024 — present)</sub> | The synthesis. Seven-node directed acyclic graph, deterministic gates first, fail-closed by default. 10.5M product detail pages / cycle · 73.5M ops / run · $0.0006 / page · 68.9% pass rate across Originality, Relevance, Accuracy, Value. |

#### Open-source distillations (parallel track)

| Repository | Description |
|---|---|
| [**agent-dag-pipeline**](https://github.com/Manzela/agent-dag-pipeline) | Open-source distillation of the seven-node directed acyclic graph. Google Agent Development Kit + Vertex AI + four-axis Originality-Relevance-Accuracy-Value evaluation + Direct Preference Optimization data flywheel. |
| [**Antigravity-OS**](https://github.com/Manzela/Antigravity-OS) <sub>· `pip install ag-os`</sub> | AI governance kernel — cost enforcement, Open Policy Agent-style policy-as-code, deterministic state tracking, Model Context Protocol server, and self-healing continuous-integration for autonomous agent fleets. |
| [**gemma4-vllm-deployment**](https://github.com/Manzela/gemma4-vllm-deployment) | Forensic runbook documenting 20 failure modes across 30+ deployment versions of Gemma 4 Mixture-of-Experts on Vertex AI with vLLM. The community reference for production Mixture-of-Experts serving. |
| [**pipeline-observatory**](https://github.com/Manzela/pipeline-observatory) | Source of the live observability site at [manzela.github.io/pipeline-observatory](https://manzela.github.io/pipeline-observatory/). Architecture visualization — Mixture-of-Experts sparse routing, causal directed-acyclic-graph tracing, live execution telemetry. |

---

<div align="center">
<sub>Israel (Relocating) · <a href="mailto:danielq1603@gmail.com">danielq1603@gmail.com</a></sub>
</div>

