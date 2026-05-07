<div align="center">

# Daniel Manzela

**Autonomous AI Systems Engineer**

*From architecture to execution — building reliable, steerable, and safe autonomous AI at enterprise scale*

<br>

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat&logo=linkedin&logoColor=white)](https://linkedin.com/in/manzela)
[![Google Cloud Skills](https://img.shields.io/badge/Google_Cloud-32_Credentials-4285F4?style=flat&logo=google-cloud&logoColor=white)](https://partner.skills.google/public_profiles/69fa3af8-3032-4a04-a818-f7277009c3a9)
[![Pipeline Observatory](https://img.shields.io/badge/Live_Demo-Pipeline_Observatory-000?style=flat&logo=github-pages&logoColor=white)](https://manzela.github.io/pipeline-observatory/)

</div>

---

### What I Build

I design and operate **end-to-end autonomous AI systems** — from 0→1 architecture through production optimization. My work sits at the intersection of multi-agent orchestration, fail-closed safety, and LLM evaluation, with a focus on systems that run with **zero human oversight** at enterprise scale.

**Current system in production:**
- **11 enterprise clients** across 4 countries, **~7.9M product data points** processed per cycle
- **7-node multi-agent DAG** with ~116M sub-agent executions per cycle
- **Gemma 4 MoE** on vLLM with tenant-isolated Multi-LoRA serving (<50ms adapter swap)
- **O-R-A-V** multi-model evaluation with fail-closed policy (68.9% pass rate by design)

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

Every DAG node is a bounded ecosystem, not a single LLM call:

| Layer | Role | Example |
|---|---|---|
| **Deterministic Gate** | Schema validation, type coercion, regex | Pydantic, Python AST |
| **Probabilistic Agent** | Semantic extraction, classification | Gemini Vision, SLM |
| **Autonomy Layer** | O-R-A-V scoring, confidence thresholds | Multi-model consensus |
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
![LoRA](https://img.shields.io/badge/Multi--LoRA_Serving-000?style=flat-square)
![Fail-Closed](https://img.shields.io/badge/Fail--Closed_Safety-000?style=flat-square)
![RLHF](https://img.shields.io/badge/Closed--Loop_RL-000?style=flat-square)

</div>

---

### Featured Work

| Repository | Description |
|---|---|
| [**pipeline-observatory**](https://github.com/Manzela/pipeline-observatory) | Interactive architecture visualization of the autonomous pipeline — MoE sparse routing, causal DAG tracing, and live execution telemetry. [Live Demo →](https://manzela.github.io/pipeline-observatory/) |
| [**gemma4-vllm-deployment**](https://github.com/Manzela/gemma4-vllm-deployment) | Forensic runbook documenting 20 failure modes across 30+ deployment versions of Gemma 4 MoE on Vertex AI with vLLM. The community reference for production MoE serving. |
| [**Antigravity-OS**](https://github.com/Manzela/Antigravity-OS) | AI governance kernel — cost enforcement, policy-as-code (OPA), deterministic state tracking, and self-healing CI for autonomous agent fleets. |

---

<div align="center">
<sub>Israel (Relocating) · <a href="mailto:manzela@gmail.com">manzela@gmail.com</a></sub>
</div>

