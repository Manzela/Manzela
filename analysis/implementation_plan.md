# Seller App — Apple-Lens Audit v3 · Implementation Plan

**Target file:** `Manzela/seller-app/index.html` (live: https://manzela.github.io/Manzela/seller-app/)
**Branch:** `polish/seller-app-applelens-v3`
**Worktree:** `Manzela/.worktrees/seller-app-applelens-v3/`
**Lens:** Apple-grade portfolio-asset, NOT marketing/sales. Audience = recruiters / hiring managers / investors / partners. Purpose = illustrate Daniel's 0→1 work.
**Phase:** 1 — Planning (per `planning.md`). NO file edits to `seller-app/index.html` until explicit approval.

---

## 0. Method

Section-by-section adversarial audit using four mandatory questions per element:
1. What value does this bring the viewer?
2. Why is it important?
3. Is the underlying intent fully addressed?
4. What would Apple do — without going marketing?

Findings are graded **P0 (blocker / correctness / accessibility)**, **P1 (substantive content/UX)**, **P2 (polish / Apple-lens refinement)**.

I am refusing to be diplomatic. The page is good. It is not yet at the bar Daniel sets across the rest of the portfolio.

---

## 1. Section-by-section findings

### 1.1 `<head>` and global setup

| # | Finding | Grade | Why it matters |
|---|---|---|---|
| H1 | **No `<noscript>` fallback for `.fade-in`** — `opacity:0` is the default; if JS is blocked or fails, the entire page below the hero is invisible. | **P0** | Recruiters in locked-down corporate browsers, accessibility tools, or any JS failure see a blank page. Total content invisibility. |
| H2 | **No JSON-LD / Schema.org markup** (`CreativeWork`, `Article`, `Person`, optional `SoftwareApplication`). | P1 | LinkedIn, Google, and richer surfaces use schema to render cards. Apple uses schema on every product page. |
| H3 | **Inter loaded from Google Fonts** — system stack already lists `-apple-system`, `BlinkMacSystemFont`. Loading Inter from Google adds 1 round-trip + privacy footprint for a font that *contradicts* `ClaudeOpusBestPractices.md §4.4`. | P1 | The faithful Apple aesthetic is SF Pro via `-apple-system` on Apple devices and Inter as fallback only. Currently Google-loaded Inter overrides SF Pro on macOS. Backwards. |
| H4 | **Material Symbols at `wght 300`** on a dark surface — strokes optically thin against `#000`; reads gray-on-gray. Apple's icons render at heavier optical weight on dark UIs. | P2 | Visual heft mismatch. |
| H5 | **No `prefers-reduced-data`** handling for the 36 MB of inline video. Cellular visitors auto-fetch metadata even when they can't watch. | P1 | Mobile-first hostile. Page weight is dominated by video that most viewers won't play. |
| H6 | Description meta says "*Bootstrapped to $10K MRR*" — fine for SEO, but it sets revenue as the headline result before the page can frame it. See §1.3 hero finding HE2. | P2 | Snippet framing ≠ page framing. Reconcile both. |

### 1.2 Navigation

| # | Finding | Grade | Why |
|---|---|---|---|
| N1 | **#gpd is not in the nav** — the entire Global Product Database section (one of the strongest technical pieces) is unreachable via the nav. Visitors who skim via nav skip it entirely. | **P0** | Broken information architecture. The most original technical insight on the page is hidden from the table of contents. |
| N2 | Nav label "Decision" anchors to `#pivot`. Section heading reads "Why We Pivoted." Internally consistent enough, but a mismatched name breaks the mental model someone scanning the nav builds. | P2 | Either rename nav item to "Pivot" (matches section verb) or rename section heading to "The Decision" (matches nav noun). Pick one frame. |
| N3 | Mobile hamburger doesn't morph into an X when open. Apple's mobile hamburgers always animate. | P2 | Polish. Easy. |

### 1.3 Hero

| # | Finding | Grade | Why |
|---|---|---|---|
| HE1 | **No hero visual.** The page is text-only above the fold. Apple product pages always lead with a single hero image/video of the product itself. The two videos that EXIST on the page are buried 6 sections deep. | **P1** | This is a vision/CV product. Showing the product visually above the fold = the single highest-leverage Apple-grade move available here. |
| HE2 | **`$10K MRR` as a hero metric is wrong-framed for the audience.** It reads as a *result* — small for an investor, fine for a recruiter, ambiguous for both. The page's whole arc explains *why* MRR plateaued (incentive friction → enterprise pivot). Leading with the number first creates a "this didn't scale" first impression that the next 1,000px of scroll then has to *undo*. | **P1** | Apple never leads a product page with a revenue number. Apple leads with capability. The truthful, impressive framing is "Bootstrapped 4 years to $10K MRR with no external capital" — independence + endurance, not ceiling. Or replace with a capability metric: throughput, scope, scale. |
| HE3 | "3 Computer Vision versions shipped" is solid. "4 yrs Bootstrapped" is solid. The MRR cell is the weak one. | P1 | See HE2 — replace OR re-caption. |
| HE4 | Subhead is good but `text-lead` is `font-weight: 300`. Apple's lead text is 400. 300 is editorial-magazine; 400 is product page. | P2 | Tighten. |
| HE5 | No co-founder credibility above the fold. The "co-founded with a senior Amazon Applied Scientist" line is the strongest credibility signal on the page and it's hidden in section 2. | P1 | Apple would surface technical credibility briefly in the hero meta line — *not* as name-drop, but as proof-of-bar. |

### 1.4 Problem ("The Onboarding Bottleneck")

| # | Finding | Grade | Why |
|---|---|---|---|
| P1 | **"Manual Upload Cost" card lacks any number.** "A 50-product catalog takes hours" is unverifiable hand-wave. Apple framing quantifies: "3 minutes per product × 50 products = 2.5 hours per store." | P1 | Concrete > vague. Recruiters grade for quantified thinking. |
| P2 | **Co-founder note placement is structurally wrong.** It sits inside the Problem section. Reader narrative: "the problem is X, by the way I co-founded with an Amazon scientist" is a non-sequitur. Co-founder credibility belongs either in the hero meta, as its own short "team / technical bar" beat, or anchored to the Architecture section as the source of the technical bar. | P1 | Information architecture. The credibility is too important to be a footer to a problem statement. |
| P3 | Three card icons (storefront, inventory_2, block) — adequate. `block` feels generic for "no frictionless path." Could be something like `route` or `alt_route`. | P2 | Minor. |

### 1.5 Product Evolution ("Three Generations of Vision")

| # | Finding | Grade | Why |
|---|---|---|---|
| PE1 | **V1 has 8 feature pills; 4 of them describe the platform, not V1 specifically** (Sign-up, Inventory, Orders, Marketing, Settings, Integration). These existed across V2/V3 too. Putting them under V1 dilutes the *evolutionary* narrative — V1 reads as "everything ever built." V2 and V3 then look like minor updates. | **P1** | Each version card must isolate what is *new in that version* — that's the definition of an evolution. Move platform features to Architecture; V1's pills should be barcode + GPD lookup + auto-fill workflow only. |
| PE2 | All three version cards look stylistically identical. There's no visual sense of *progress* across the generations. | P2 | Apple would escalate visually — V1 modest, V2 introduces an image, V3 introduces a visual of the video pan-and-recognize gesture. Even a subtle gradient-band per version would communicate trajectory. |
| PE3 | `.version-period` displays "Barcode + Database" / "Image + OCR" / "Video + Retrieval" — but the CSS class name and text styling read as a *date*. The semantic mismatches the visual. | P2 | Either rename the slot to `.version-tagline` and restyle, or move taglines into the title row, or replace with actual date ranges per version (which Daniel may not want to disclose precisely). |
| PE4 | V3 says "RAG model over the Global Product Database" — gold. But the GPD section that follows immediately doesn't reinforce this. Cross-section reinforcement is missing. | P1 | See GPD findings. |

### 1.6 Global Product Database (#gpd)

| # | Finding | Grade | Why |
|---|---|---|---|
| GPD1 | **The strongest technical insight on the entire page** — *"the model was conditioned on real product data instead of hallucinating attributes from raw pixels"* — is buried in a tertiary callout footnote at the bottom of the section. | **P1** | This is RAG-as-grounding-for-CV, which is the bridge between the Seller App and the Autonomous Pipeline that came after. Apple framing: this becomes the *thesis sentence of the section*, not its footnote. |
| GPD2 | "Roadmap" card label is wrong. The three bullets are: WebScraping (shipped), Bright Data (shipped/integrated), Multilingual (planned). Two of three are past, one is future. Calling the whole thing "Roadmap" misleads. | P1 | Rename to "Ingestion stack" with each item tagged `shipped` / `planned`. Or split into "Built" + "Planned." |
| GPD3 | Section is invisible from nav — see N1. | P0 | Nav fix needed. |
| GPD4 | "One catalog, every retailer" is poetic but vague. A number would harden it: "X SKUs canonicalized" or "Y vendors sharing a single record per UPC." If those numbers can't be shared, say *"exact figures held under prior NDA"* — honesty beats vagueness. | P1 | Apple shows numbers when it can and is silent (not vague) when it can't. |

### 1.7 Architecture

| # | Finding | Grade | Why |
|---|---|---|---|
| A1 | **The flow diagram is text-pills-with-arrows.** Apple does not ship that on a portfolio asset. It needs to be a real SVG diagram (boxes, lines, labels) or replaced with annotated app screenshots showing the actual workflow. | **P1** | This is the most embarrassing element on the page when judged by an Apple-aesthetic bar. It looks like a draft. |
| A2 | **The flow diagram only describes V1.** V2 (image-OCR-CV) and V3 (video-RAG) had different flows and aren't diagrammed at all. The product evolves; the architecture freezes. | P1 | Either three small flow diagrams (V1/V2/V3) stacked, or one consolidated multi-stage diagram with branches. |
| A3 | **6 shallow architecture cards** of equal weight. PWA, Integration, Two DBs, Localization, Notifications, Analytics. Equal sizing implies equal importance — false. The Two DBs card is the architectural backbone; Notifications is plumbing. Apple would use 2 deep cards + a stat row, not 6 shallow cards. | P1 | Hierarchy of emphasis. |
| A4 | **No throughput / scale numbers anywhere in Architecture.** "How many scans/sec? GPD record count? GPD query latency? On-device vs cloud inference for ML Kit?" — the kind of detail engineers grade architecture by. | P1 | Architecture without numbers is generic architecture. If exact numbers are NDA, say so. |
| A5 | Infrastructure callout (AWS, MongoDB, CI/CD) is buried at the bottom. Should be a stat row at the top of Architecture (as a tech-stack chip strip). | P1 | Visibility. |
| A6 | Co-founder-style `cofounder-note` callout #3 — same template, third time on the page. Reads like a CMS pattern. | P2 | Vary emphasis: a callout, a quote, a stat strip — not all the same component. |

### 1.8 Field Evidence

| # | Finding | Grade | Why |
|---|---|---|---|
| FE1 | **Videos have no `poster=` attribute.** Until clicked they're black 4:3 boxes. On any first-impression scroll, this section looks broken. | **P0** | Apple's media is *always* poster'd. This is the most visible Apple-bar miss on the page. |
| FE2 | **Two videos = ~36 MB inline.** `preload="metadata"` still pulls a few hundred KB per video on every page load. No bandwidth gating. | P1 | See H5. Replace `preload="metadata"` with `preload="none"` + click-to-play, OR add `prefers-reduced-data` handling. |
| FE3 | **No transcripts, no captions, no descriptions of what's *in* the video.** Deaf users get nothing. Search engines index nothing. Recruiters who won't click a 30-second video get nothing. | **P0** for accessibility | WCAG 2.1 AA requires captions/transcript for prerecorded video. Currently zero compliance. |
| FE4 | Field photo captions are excellent ("watching a real seller perform their first scan…"). Keep. | — | Bright spot. |
| FE5 | Click-to-expand / lightbox is missing. Videos play inline at small size. | P2 | Apple polish. |

### 1.9 Metrics

| # | Finding | Grade | Why |
|---|---|---|---|
| M1 | **KPI bar repeats the hero metrics verbatim** ($10K MRR / ~50 prods/hr / 3 versions). Redundant. | P1 | Either drop the redundant cells, or replace with *new* metrics that the hero didn't have room for: cohort retention, products onboarded total, stores onboarded total, GPD record count, etc. |
| M2 | **HEART card lists the framework but not a single number.** "Happiness — in-app survey + NPS" — what *was* the NPS? "Retention — week-2/4/month-3 cohorts" — what *were* the rates? The list reads as "we instrumented these axes" (process), not "we achieved these results" (outcome). | **P1** | Either add real numbers OR explicitly state the omission ("cohort numbers held under prior NDA — instrumentation was production-grade Mixpanel + GA4"). Apple is silent or specific, never vague. |
| M3 | **"Iteration Drivers" card is a backlog of features that never shipped** (online payments, last-mile delivery, POS sync, weight-based products). The label "Iteration Drivers" is a euphemism. Either rename to *"Backlog at deprecation"* or *"What customer pain told us next"* — and then make explicit that the pivot decision shipped *instead* of these features. | P1 | Truthful naming. The current frame implies ongoing work; it was actually a parked backlog. |

### 1.10 Pivot

| # | Finding | Grade | Why |
|---|---|---|---|
| PV1 | **Date inconsistency.** Hero / desc / footer say "Jan 2020 – Apr 2024." Pivot deprecation callout says "January 2025." A reader will read this as a typo. The truth is two-stage: Apr 2024 = active product end, Jan 2025 = full migration to WordPress multisite / formal deprecation. Make the two-stage timeline explicit. | **P0** | Inconsistent dates on a portfolio asset = competence signal failure. |
| PV2 | "The Friction We Couldn't Code Away" — this title is *the* line of the page. Strong. Keep. | — | Bright spot. |
| PV3 | "Outcome" card: links to pipeline-observatory. Good. Could also link to the agent-dag-pipeline repo (open-source spinout) for technical recruiters. | P2 | Cross-portfolio reinforcement. |
| PV4 | The pivot story is at the strategic level. There is no equivalent at the **technical** level — what *technically* was hard, what would I redo. For recruiters this is the missing reflection signal. | P1 | See cross-cutting finding §1.13. |

### 1.11 Footer

| # | Finding | Grade | Why |
|---|---|---|---|
| F1 | **Cross-portfolio links: only 2 of 6 public showcases** (Elysium + Pipeline Observatory). Missing: agent-dag-pipeline repo, Antigravity-OS repo, gemma4-vllm-deployment runbook. Cross-portfolio parity matters per CLAUDE.md. | P1 | A recruiter who lands here should be able to reach every other public asset Daniel ships. |
| F2 | Date footer "© 2020–2026 · Seller App was an active product Jan 2020 – Apr 2024" — see PV1 reconciliation. | P0 | Already covered. |
| F3 | No "back to top" anchor. Long page on mobile = lots of scroll to nav. | P2 | Tiny. Apple-grade footer always offers it. |

### 1.12 Parent profile linkage (CRITICAL — not part of the page itself but a precondition for it to deliver any value)

| # | Finding | Grade | Why |
|---|---|---|---|
| L1 | **`Manzela/profile.html` does not link to `seller-app/` anywhere.** The seller-app case study is *orphaned* from the discoverable surface of Daniel's profile site. A visitor landing on `manzela.github.io/Manzela/` cannot reach this page from the canonical profile. | **P0** | The page can be perfect and it does not matter if no one finds it. The whole point of building the case study was to surface 0→1 product work to recruiters; the recruiter starts at the profile, not at a deep-linked URL. |
| L2 | `Manzela/index.html` (the GitHub profile README copy) likely also lacks the link. To verify before edit. | P0 | Same reason. |

### 1.13 Cross-cutting / structural

| # | Finding | Grade | Why |
|---|---|---|---|
| X1 | **The page tells the story but doesn't show reflection.** No "What I'd do differently / Lessons" section. For a senior-IC / founder recruiter, the absence of reflection is the absence of senior judgment signal. | **P1** | Add a short "Lessons" beat after Pivot — 3-4 bullets, technical not strategic, e.g. "Should have hired a field-ops person sooner; the seller-incentive problem was a sales/ops issue we mistook for a UX issue." Apple-honest. |
| X2 | No clear "next" CTA. Page ends at the deprecation callout; reader is left at a dead end. | P2 | Apple ends every product page with a "what next" — for a portfolio it's "see the live pipeline," "view the open-source spinout," or "get in touch." |
| X3 | **Many inline `style="..."` attributes** scattered across the page when `class=` utilities exist. Inconsistent with the otherwise-clean token system. | P2 | Refactor inline styles into utility classes (`.mt-16`, `.mb-12`, etc.) for maintainability. Not visible to viewer. |
| X4 | **Three identical `cofounder-note` callouts.** Same component, three places, three different purposes. Reads templated, not curated. Apple varies emphasis. | P2 | Replace one or two with a different visual treatment (a stat strip, a quote block) so the cadence varies. |
| X5 | **No print stylesheet.** Recruiters PDF-print portfolio pages. Currently it would print as black-on-black. | P2 | Add a `@media print` override (white background, dark text, hide nav/footer). |
| X6 | No `theme-color` for `light` color scheme; the site is dark-only. Acceptable Apple commit. | — | Fine. |

---

## 2. Prioritized fix list (the BUILD-mode ledger)

Grouped by grade. Every item has a precise change description. **No edits to `seller-app/index.html` until Daniel approves this plan.**

### P0 — must fix (blocker / correctness / accessibility / discoverability)

1. **`<noscript>` fallback** — add a `<noscript><style>.fade-in{opacity:1;transform:none}</style></noscript>` in `<head>` so JS-disabled browsers see all content. *(H1)*
2. **Add `#gpd` to nav** as "Database" or "GPD." *(N1)*
3. **Reconcile dates** — change every "Jan 2020 – Apr 2024" reference to a two-stage timeline: "Active: Jan 2020 – Apr 2024 · Migrated to WordPress multisite: Jan 2025." Update hero meta line, OG description, footer copy, and pivot callout to read consistently. *(PV1, F2)*
4. **Add video posters** — generate two static poster frames from the videos themselves (ffmpeg, frame at 00:01 or chosen visual high point) and add `poster="assets/media/<name>.jpg"` to both `<video>` tags. Ship as ≤80 KB JPEGs. *(FE1)*
5. **Video accessibility** — add a 1-2 sentence inline transcript-summary directly under each video caption (visible text — what happens in the video, in plain language). Target WCAG 2.1 AA prerecorded-video equivalent. Mark videos `preload="none"`. *(FE3, FE2)*
6. **Link seller-app from parent profile** — verify and add a link in both `Manzela/profile.html` and `Manzela/index.html` (whichever surfaces are publicly indexed). Place the link in the existing case-study / projects section if one exists; if not, add a one-line "Past work" reference in the natural narrative. *(L1, L2)* **This is a separate-file fix; called out so it's not forgotten.**

### P1 — high (substantive content / UX / Apple-bar)

7. **Reframe hero metrics** — replace `$10K MRR achieved` cell with a capability-first metric (proposed: "**~50 products / hour** target onboarding throughput"). Add a *small* line under the hero metrics row: "*4 years bootstrapped, no external capital · co-founded with Dr. Eli Osherovich (Amazon Alexa Shopping / Amazon Go)*." This relocates the credibility AND retains MRR context as a one-liner — without leading with a small number. *(HE2, HE3, HE5)*
8. **Add a hero visual** — use the new Field-Evidence video poster (or one of the in-store photos) as a single 16:9 hero image immediately below the hero metrics. Apple-style: wide, edge-to-edge, no card chrome. Caption-free. *(HE1)*
9. **Promote GPD-as-grounding to section thesis** — pull the "the model was conditioned on real product data instead of hallucinating attributes" sentence out of the footnote callout and rewrite the GPD section's lead paragraph around it. The footnote callout becomes redundant and is removed. *(GPD1)*
10. **Restructure V1 feature pills** — keep only the version-specific CV-workflow features (Scanner, Auto-fill, Inventory bulk-upload). Move the platform-foundations features (Sign-up, Orders, Marketing, Settings, Integration) into a new compact "Platform foundations" card inside Architecture. *(PE1)*
11. **Replace V1-only flow diagram with three small SVG flow diagrams** — V1 (Camera → ML Kit → GPD → Auto-fill → WC), V2 (Camera → OCR + CV-cleanup → GPD-enrich → WC), V3 (Video stream → frame extraction → RAG over GPD → WC). Stack vertically or use a single tabbed/segmented view. SVG, no images. *(A1, A2)*
12. **Architecture: collapse 6 cards → 3 deep cards + 1 stat strip.** Stat strip = AWS · MongoDB · WCMp REST API · Mixpanel · GA4 · CI/CD. Three deep cards = (1) PWA Topology, (2) Two-Database Model (GPD + Store DB), (3) Vision Stack (ML Kit + foundation-model OCR + RAG). Localization + Notifications become bullets inside the PWA Topology card. *(A3, A5)*
13. **Quantify Architecture** — add 2-3 throughput / scale numbers as inline mono-spaced badges within the relevant card (e.g., "GPD: ~X SKUs canonicalized" / "ML Kit inference: on-device, ~Y ms / scan"). If exact numbers are NDA, replace with "details under prior NDA." *(A4)*
14. **Quantify Problem** — add the cost number to the Manual Upload Cost card: "~3 min/product × 50 products = 2.5 hrs/store, before photos." *(P1)*
15. **Move co-founder note out of Problem** — relocate the credibility line to the new hero meta sub-line (per #7). The Problem section ends cleanly on the three pain cards. *(P2)*
16. **Rename "Roadmap" card in GPD** to "Ingestion stack" with `shipped`/`planned` tags per item. *(GPD2)*
17. **HEART numbers OR explicit NDA disclosure** — if any cohort/retention/NPS number is shareable, add it. Otherwise add the line: "*Cohort and NPS figures held under prior NDA. Instrumentation was production-grade Mixpanel + GA4.*" *(M2)*
18. **Rename "Iteration Drivers" card** to "Backlog at deprecation — what customer pain told us next" and add a closing sentence: "We shipped the pivot instead of these." *(M3)*
19. **Drop hero-metric duplication in KPI bar** — replace the redundant cells with: (a) total products onboarded / total stores onboarded if shareable, else (b) "*Vintage 2020–2024 · 4-yr bootstrap*", "*HEART instrumentation: live from week 1*". *(M1)*
20. **Add a "Lessons" beat after Pivot** — 3 short technical-honest bullets. Examples: "Confused a sales/ops problem (seller incentives) for a UX problem for too long." / "GPD-as-retrieval-layer was the right architectural choice — it's why the IP carried forward." / "PWA was right for a B2B SMB tool; would not pick it for a consumer launch in the same market." *(X1, PV4)*
21. **Footer cross-portfolio parity** — add links to all 6 public showcases per CLAUDE.md: Antigravity-OS (PyPI/repo), agent-dag-pipeline (repo), gemma4-vllm-deployment (runbook). Plus existing Profile / Elysium / Pipeline Observatory / GitHub / LinkedIn. *(F1)*

### P2 — polish (Apple-lens refinement)

22. **JSON-LD schema.org** — add `<script type="application/ld+json">` with `Article` (or `CreativeWork`) markup naming Daniel as `author` (Person, sameAs LinkedIn + GitHub). *(H2)*
23. **`prefers-reduced-data`** — wrap the `<video>` elements in a `<picture>` / poster-only fallback when the user's connection is metered. Combined with `preload="none"` from #5. *(H5)*
24. **Material Symbols weight** → bump from 300 to 400 for dark-surface contrast. *(H4)*
25. **`text-lead` weight** → 300 → 400 for Apple-product-page voice. *(HE4)*
26. **Mobile hamburger animation** → bars morph to X via CSS transform. *(N3)*
27. **Print stylesheet** — `@media print { body { background:#fff; color:#000; } nav, footer, video { display:none; } }` plus poster-image fallback for the video sections. *(X5)*
28. **Vary `cofounder-note` instances** — replace the GPD instance with a small inline pull-quote treatment, replace the Architecture instance with the new infrastructure stat strip. Keep one canonical callout for the team line if relocated per #7 logic. *(X4, A6)*
29. **Convert remaining inline `style="…"`** to utility classes (`.mt-16`, `.mb-12`, `.mt-24`). *(X3)*
30. **Sticky "back to top" anchor** in the footer for mobile. *(F3)*
31. **Light-version of the icon set** — investigate whether `Material Symbols` can be swapped for an icon set closer to SF Symbols (e.g., `phosphor-icons`) without breaking parity with Elysium/profile. *Defer if Elysium uses Material Symbols too — cross-portfolio parity beats individual-page perfection.* *(H4 follow-up)*
32. **Nav rename consistency** — "Decision" or "Pivot" — pick one and align section heading. Recommend: nav stays "Pivot" (verb form, matches scrollable section heading change). *(N2)*

### Non-changes (explicit no-ops — flagged so they don't get touched)

- Do **not** add a light-mode toggle. Apple commits to a single mode per surface; this page commits to dark. The playbook mentions toggles but Apple itself doesn't ship them on product pages. Don't generate work for the sake of a checklist.
- Do **not** reframe the page in marketing voice. Daniel's bar is "system-design-literate, no marketing fluff." Every fix above has been chosen to *strengthen capability signal*, not to sell.
- Do **not** delete the videos. Heavy as they are, raw field footage is the single most original asset on the page; we make them lighter (#4, #5, #23), not absent.
- Do **not** introduce a build step / framework / dependency. Per CLAUDE.md the showcase HTML sites use zero JS dependencies. Stay vanilla.

---

## 3. Adversarial review of THIS plan ("What did I miss? Where will this break?")

Per `planning.md` §2: the planner must ask the adversarial question before submitting.

**Q1: Am I imposing my taste on Daniel's taste?**
Risk: real. Several findings (e.g., HE2 reframe of `$10K MRR`, A3 collapse of 6→3 architecture cards) are matters of editorial preference, not bugs. Mitigation: every P1 is reversible, every change ships behind explicit Daniel approval, and the plan is offered as a *menu* — Daniel may decline any P1/P2 item and the rest still ship.

**Q2: Will the V1-feature redistribution (#10) break the page narrative?**
The Sign-up/Orders/Marketing/Settings features being *on V1* is technically correct — they were built during V1's era. Moving them to "Platform foundations" inside Architecture is a re-categorization, not a removal. Risk: a reader who knows the original chronology may notice. Mitigation: add a sentence to V1 saying "*V1 also shipped the platform foundations the later versions inherited — see Architecture.*" Bridges the categorization.

**Q3: Will the hero metric reframe (#7) lose the honest "we hit $10K MRR" signal?**
No — the relocated context line preserves "*4 years bootstrapped, no external capital*" which IS the achievement. The MRR figure remains in the page meta description for SEO and in the pivot section for narrative truth. Removing it from the hero doesn't hide it; it stops *front-loading* it.

**Q4: Will adding video posters break the existing layout?**
No — `poster=` is purely visual; the video element retains its frame.

**Q5: What about Schema.org type — `Article` vs `CreativeWork` vs `SoftwareApplication`?**
Closest real-world fit is `Article` with `about` referencing a `SoftwareApplication`. `Article` is what LinkedIn / Google News parse cleanly. Use `Article` with nested `mainEntity` of type `SoftwareApplication`.

**Q6: HEART numbers — is Daniel free to share any actual figure?**
Unknown. Plan defaults to the explicit-NDA-disclosure pattern, which is the safe default and is itself an Apple-grade move (silence + provenance > vagueness). If Daniel wants to share specific numbers in the approval message, they get added.

**Q7: The flow-diagram SVG (#11) is the most labor-intensive item — is it worth it?**
Yes. A1 was the single most "embarrassing" finding. Three small inline SVG flow diagrams (no library, no build, ~150 lines of SVG total) is a one-shot job. Not worth deferring.

**Q8: The parent-profile linkage fix (#6) edits a different file in a different commit — will that pollute the seller-app branch?**
Yes — and that's correct. The branch is `polish/seller-app-applelens-v3`; the seller-app being orphaned is part of the seller-app-audit work. Single feature branch, two file scopes (`profile.html`/`index.html` + `seller-app/index.html`). Daniel can split into separate commits at PR-time.

**Q9: Anything missed?**
The audit did NOT cover: (a) actual page-load performance (Lighthouse), (b) live screenshot comparisons across browsers, (c) Hebrew/RTL rendering verification (mentioned in Architecture but not tested). These are post-build verification items; surfacing them now to track in §4.

**Q10: Cost/risk of the full P0+P1+P2 set?**
P0 = ~30 min (additive, low-risk). P1 = ~3 hrs (substantive content rewrites + SVG diagrams + hero restructure). P2 = ~1.5 hrs (incremental polish). Total ~5 hrs of focused execution. Worth it.

---

## 4. Build-mode plan (sequenced)

After approval — phase 3 of `planning.md`:

1. **Set up working state** (DONE) — worktree at `.worktrees/seller-app-applelens-v3/` on branch `polish/seller-app-applelens-v3`.
2. **Generate poster frames** — `ffmpeg -ss 00:01 -i 1000067651.mp4 -vframes 1 -q:v 4 1000067651.poster.jpg`, repeat for the second video. Commit posters to `seller-app/assets/media/`. *(P0 #4)*
3. **Apply P0 fixes in one commit** — noscript, nav `#gpd`, video posters/preload/transcript-lines, date reconciliation, parent-profile linkage edit. *(P0 #1, #2, #3, #4, #5, #6)*
4. **Apply P1 fixes in two commits**:
   - Commit A — content/IA changes: hero metric reframe, hero visual, GPD thesis, V1 feature redistribution, architecture restructure (cards), Problem quantification, GPD ingestion-stack rename, HEART NDA disclosure, Iteration Drivers rename, KPI dedup, Lessons section, footer cross-portfolio links. *(P1 #7, #8, #9, #10, #12, #13, #14, #15, #16, #17, #18, #19, #20, #21)*
   - Commit B — diagram work: three SVG flow diagrams replacing the text-pill flow. *(P1 #11)*
5. **Apply P2 fixes in one commit** — JSON-LD, reduced-data video, Symbol/text weights, mobile-menu animation, print stylesheet, callout variation, inline-style cleanup, back-to-top, nav rename. *(P2 #22-#32)*
6. **Verification (per `planning.md` §4)**:
   - Open the local file in a browser; visual diff against current live page.
   - Open `https://manzela.github.io/Manzela/seller-app/` in another tab to compare narrative arc.
   - Test hash-link nav for all sections including new GPD entry.
   - Test mobile viewport (responsive devtools at 375 / 414 / 768 / 1024).
   - Test JS-disabled view (DevTools → Settings → Disable JavaScript) → verify no blank-page regression.
   - Test print preview.
   - Run Lighthouse on the local file: confirm no score regression vs current page.
   - Verify new poster JPEGs are <80 KB each.
   - Verify Schema.org via Google's Rich Results test.
7. **Open PR from `polish/seller-app-applelens-v3` → `main`** with the audit document + the change summary.

---

## 5. Approval gate

Per `planning.md` §3: *"ONLY DANIEL CAN APPROVE."*

This plan is now submitted for review. **No edits to `seller-app/index.html` or `Manzela/profile.html` will be made** until Daniel responds with:

- **"Approved"** / **"Execute"** — full plan ships as ordered.
- **"Approve P0+P1, defer P2"** — partial scope; clarify which.
- **Edits / objections** — refine plan, re-submit.

Specifically — Daniel should weigh in on these decision points the planner cannot make alone:

| Decision | Default if unanswered |
|---|---|
| Replace `$10K MRR` in hero with throughput metric? *(HE2)* | Yes — replace, relocate MRR to descriptive meta + pivot narrative |
| Real HEART/NPS/cohort numbers shareable? *(M2)* | Default to explicit NDA-disclosure line |
| Real GPD-size / scan-throughput numbers shareable? *(A4, GPD4)* | Default to NDA-disclosure |
| Date reconciliation phrasing — "Active: Jan 2020–Apr 2024 · Migrated: Jan 2025"? | Use as written |
| Nav: rename "Decision" → "Pivot"? *(N2)* | Yes — "Pivot" |
| Replace Material Symbols with closer-to-SF set across this page only? *(H4 / P2 #31)* | **No** — keep Material for cross-portfolio parity |
| Inter via Google Fonts vs system stack only? *(H3)* | Move to system-stack only on this page; keep Google Fonts as fallback if Daniel wants Inter on Linux/Windows visitors |
| Lessons section content — strategic-honest vs strictly-technical? *(P1 #20)* | Default: technical-honest, 3 bullets, ≤180 chars each |

---

*End of plan. Awaiting Daniel's review.*
