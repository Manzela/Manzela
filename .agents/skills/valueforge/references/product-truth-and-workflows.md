# VALUEFORGE Product Truth & Slice 1 Workflows (`Cap 2`, `Cap 4`, `W2`, `W4`, `REV-008`)

> Load this reference on demand when executing product-state intake (`W2`), inspecting Git temporal divergence (`W4`), reading/updating `ai-memory` Product Truth (`REV-008`), or verifying Slice 1 workflow boundaries.

---

## 1. Capability 2 — Adaptive Product-State Intake & `W2` Brownfield POC

VALUEFORGE adapts intake to the actual starting state (raw idea, prototype, brownfield POC, or live product) without forcing a rigid linear 15-stage lifecycle sequence or an arbitrary composite readiness score.

### 1.1 `W2` Brownfield POC Intake Checklist (7 Required Behaviors)

When onboarding or assessing an existing brownfield repository/POC, execute all seven behaviors from observable evidence:

1. **Inspect Real Existing Assets:** Read actual source modules, tests, configs, docs, and `ai-memory` records as they exist—never rely on `README.md` or marketing copy alone.
2. **Inventory Implemented vs. Claimed Capability:** Classify each capability from observed execution/code:
   - **`Implemented + Tested`:** Real implementation backed by passing executable tests (record exact pass counts).
   - **`Stub / Partial`:** Placeholder, `NotImplementedError`, hardcoded shortcut, or untested path.
   - **`Claimed Only`:** Stated in README/docs/notes without supporting implementation or verification.
3. **Separate Technical Demonstration from Customer/Product Validation:** Passing unit tests or a working local demo proves technical execution only—never customer demand, willingness to pay, or product-market fit. Mark unvalidated user/market claims explicitly **`Unverified`**.
4. **Preserve Missing Rationale Without Invention:** When historical design rationale, decision context, or trade-offs are absent, label them **`Undocumented`** (and unverified assumptions **`Unverified`**). Never invent or fabricate historical founder intent.
5. **Detect Cross-Domain Dependencies & Contradictions:** Cross-check code against configs, compliance constraints, schemas, and confirmed decisions (e.g., hardcoded currency or rounding in code contradicting `compliance.json` or contract requirements). Cite exact file paths, keys, and symbols.
6. **Preserve & Reuse Valid Existing Work:** Identify verified working modules and tests that should be reused or extended rather than proposing a premature full rebuild.
7. **Recommend the Smallest Justified Next Commitment:** Propose the minimal next step (`PROCEED`, `INVESTIGATE`, `ITERATE`, `DEFER`, or `REJECT`) that resolves the highest-leverage risk or evidence gap before expanding build scope.

---

## 2. Capability 4 — Six Product Truth Responsibilities (`DEC-004`)

Reuse existing project-scoped `ai-memory` and the enrolled Git repository (never create a separate knowledge database, graph store, or automatic bidirectional `ai-memory` ↔ Git sync). Maintain six conceptual responsibilities:

| # | Responsibility | Required Content & Integrity Rules |
|---|---|---|
| 1 | **Product Context** | Problem, target users, scope, active constraints, and operational environment. |
| 2 | **Assertions & Evidence** | Claim, scope, supporting and contradicting evidence, provenance, uncertainty, and revisit triggers. Reject linear maturity ladders; evidence is multi-dimensional. |
| 3 | **Decisions & Approvals** | Approved choice, approver, rationale, rejected options, accepted risks, and revisit triggers (`HUMAN CONFIRMED` vs `LLM SUGGESTED — NOT HUMAN CONFIRMED`). |
| 4 | **Dependencies & Intended Behavior** | Cross-domain, interface, compliance, and architectural constraints that bind implementation. |
| 5 | **Implementation References** | Repo file paths, commit SHAs, and branch names—never duplicate source code or fabricate brownfield rationale. |
| 6 | **Verification & Outcomes** | Explicit status (`Verified`, `Failed`, `Partially achieved`, `Unverified`) anchored to real test/command/observation evidence. |

### Mechanism Neutrality (`REV-20261118-008`)
Do **not** impose a single Product Truth document/page, a fixed YAML/database schema, or a single mandatory patch tool (`memory_patch_page` vs `memory_write_page`). Evaluate required state and behavior using whichever valid project memory layout and authorized update mechanism fit the task, and record the mechanism used.

---

## 3. Minimal `W4` Git-Branch Temporal Truth (7 States)

Always distinguish implementation location in Git from human decision authority and runtime verification:

| # | `W4` State | Meaning & Honest Reporting Rule |
|---|---|---|
| 1 | **`proposed`** | Unapproved suggestion or `LLM SUGGESTED` draft; confers zero execution or policy authority. |
| 2 | **`approved`** | Explicit `HUMAN CONFIRMED` founder intent; remains authoritative until explicitly revised by the founder. |
| 3 | **`working-branch`** | Unmerged code/commits on a feature branch (e.g., `feat/...`). **Never treat a branch diff as evidence that a founder decision changed.** If a branch contradicts an approved decision, flag the divergence explicitly. |
| 4 | **`merged`** | Code integrated into `main` (verified by Git ancestry/commit SHA, not branch name). Still does not imply release or deployment. |
| 5 | **`released`** | Versioned release artifact or Git tag (`git tag` / GitHub release). If zero tags/releases exist, report `released: absent`. |
| 6 | **`deployed` / `live`** | Running behavior in a live environment observed via real deployment/runtime evidence. If absent, report `deployed/live: absent` (**never invent a deployment to exercise `W4`**). |
| 7 | **`Verified` vs `Unverified`** | Orthogonally labels whether each state has matching executable/runtime evidence (`Verified`) or lacks verification (`Unverified`). |

---

## 4. `REV-008` Boundary Compare-Before-Write & `ai-memory` Usage

At meaningful work boundaries (intake completion, verified branch work, or session close), compare verified session outcomes against authoritative `ai-memory` + Git state:

1. **Read Current State First:** Retrieve relevant pages with `memory_read_page` / `memory_query` / `memory_briefing`. Static MCP clients must pass both `workspace` and `project` on every project-scoped call (never rely on last-active server state; omit `workspace`/`project` only for `global=true` / `scope:"global"`).
2. **Check Completeness:** Inspect `truncated` and `total_chars` on `memory_read_page` (raise `max_chars` up to `64000` when full text is needed; `memory_query` snippets alone are incomplete).
3. **Zero-Write No-Op:** If existing records already accurately reflect verified decisions, branch state, and outcomes, perform **zero writes (`0` mutations)**. Do not write redundant "session summaries."
4. **Minimal Authorized Update (Real Gap Only):** When a verified material gap exists:
   - Perform only the smallest authorized evidence-grounded update (preferring section-anchored `memory_patch_page` with `expected_page_id` and `section_sha256` when updating an existing page, or `memory_write_page` starting `body` with `# H1` and omitting the `title` argument when creating/writing).
   - Preserve all prior `HUMAN CONFIRMED` approvals, `LLM SUGGESTED` origin tags, `Verified`/`Unverified` labels, and unchanged sections—never silently rewrite a confirmed decision to match divergent branch code.
   - Confirm every write via authenticated read-back (`page_id`, section hashes/diff) and handle optimistic precondition mismatches by re-reading rather than forcing an overwrite.

---

## 5. Slice 1 Workflow Boundaries (`P4`, `REV-012`)

| Workflow | Slice 1 Status | Boundary Rule |
|---|---|---|
| **`W2` — Brownfield POC Intake** | **`REQUIRED`** | Fully exercised on independent disposable brownfield fixtures (never `Manzela/VALUEFORGE`). |
| **`W4` — Minimal Git Temporal Truth** | **`REQUIRED`** | Exercised via controlled branch divergence; absent tags/deployments reported honestly. |
| **`W1` — Pre-Repo Idea Fallback** | **`CONDITIONAL`** | Applies only when no Git repository exists; cannot independently verify Git execution boundaries. |
| **`W3` — Live Contradictory Evidence** | **`CONDITIONAL`** | Requires an authorized real live case; never enroll unrelated live products without founder authorization. |
| **`W5` — Repo-less / ChatGPT Remote** | **`DEFERRED`** | Conceptual obligations preserved; `DEFERRED` — never claimed implemented or tested in Slice 1. |
| **`W6` — Offline Development** | **`DEFERRED`** | Conceptual obligations preserved; `DEFERRED` — never claimed implemented or tested in Slice 1. |
| **`W7` — Concurrent Multi-IDE Writes** | **`DEFERRED`** | Conceptual obligations preserved; `DEFERRED` — never claimed implemented or tested in Slice 1. |
| **`W8` — Cross-Project Generalization** | **`DEFERRED`** | Conceptual obligations (and Tier A/B/C isolation) preserved; `DEFERRED` — never claimed implemented or tested in Slice 1. |
