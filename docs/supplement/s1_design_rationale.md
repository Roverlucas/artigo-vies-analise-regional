# Supplementary Material S1 — Research Design Rationale with Literature Justification

**Project:** Geographic Bias Across the LLM Spectrum: A Full-Spectrum Open-Weight Audit for Global South Policy Research
**Supplement for:** Main manuscript, submitted to *Patterns* (Cell Press)
**Version:** 1.0 (2026-04-23)

---

## S1.1 Purpose of this supplement

This supplement documents the research design choices of the audit, with explicit citation to the methodological and theoretical literature that informed each choice. It is structured to support peer review by showing that every design decision was grounded in prior work rather than *ad hoc*. It complements the pre-registered Statistical Analysis Plan (SAP, `etapa4_sap.md`) and the consolidated proposal (`proposta_consolidada_v3.md`).

---

## S1.2 Study framing — "Full-Spectrum Open-Weight Audit" vs alternatives

### S1.2.1 Why not a frontier-only comparison

A common design in the nascent LLM-bias literature is to benchmark three or four frontier closed-source models (GPT-4 class, Claude 3 class, Gemini 1.5 class) — exemplified by Moayeri et al. (2024) **WorldBench**, Manvi et al. (2024) on geographic bias, and Mirza et al. (2024). While rigorous within their scope, these designs share three limitations for Global South research utility:

1. **Accessibility mismatch.** Global South researchers overwhelmingly cannot afford premium frontier API access. Zhang et al. (2023) and Birhane et al. (2022) document the "AI accessibility gap" — the models benchmarked are not the models used at the research frontier in lower- and middle-income contexts.
2. **Reproducibility half-life.** Closed-source model versions are deprecated on vendor timelines (e.g., Anthropic's Claude 2 retirement, OpenAI's GPT-4-0613 sunset). Papers benchmarking these models lose reproducibility unless the vendor maintains snapshot access.
3. **Sovereignty blind spot.** Benchmarks that exclude open-weight and regional models cannot assess the sovereignty-of-AI question — a policy-relevant dimension for Global South nations (see Kukutai & Taylor 2016 on data sovereignty; Abdilla & Fitch 2017 on indigenous AI).

### S1.2.2 The "full-spectrum audit" alternative

We therefore adopt a **full-spectrum design** that includes 14 models distributed across five tiers: open-weight frontier (70B+ parameters), open-weight mid (14-30B), open-weight small and regional (7-8B), closed accessible, and closed frontier SOTA. Nine of fourteen models have fully open weights on Hugging Face with permissive licenses (Apache 2.0, Llama 4 Community License, MIT), maximizing reproducibility per the Registered Reports framework (Chambers 2019) and FAIR data principles (Wilkinson et al. 2016).

**Theoretical grounding of the full-spectrum choice:**
- **Coloniality of Knowledge** (Quijano 2000; Mohamed, Png & Isaac 2020): premium-only access is itself an asymmetry that reproduces colonial patterns; including accessible models in the audit dissolves this asymmetry rather than reproducing it.
- **Data Feminism** (D'Ignazio & Klein 2020): "examine power" and "elevate emotion and embodiment" mandates show that *who can afford to audit* shapes *what gets audited*; accessible-tier inclusion broadens the who.
- **Linguistic Resource Hypothesis** (Joshi et al. 2020): open-weight models often use different training corpora from closed frontier, giving independent estimates of the token-representation mechanism (H4).

### S1.2.3 Risks of the full-spectrum design acknowledged

- **Confounding of "openness" with "scale"** (most small models are open; most frontier are closed). We explicitly test this via H5 by examining open frontier (70B+) vs closed frontier (GPT-5). The 5 open-weight frontier models in our Tier A (Llama 4 70B, Qwen 3 72B, DeepSeek-V3 671B MoE, Mixtral 8×22B, Command R+) span a range of parameter counts overlapping with the closed frontier, enabling scale-matched contrasts.
- **Vendor-specific idiosyncrasies.** Mitigated by including 9-10 distinct vendors across tiers, following Liu et al. (2023) recommendations on LLM benchmark vendor diversity.

---

## S1.3 Domain selection — 3 domains

### S1.3.1 Domain D1: Public Policy and Institutions

**Rationale.** Applied policy research is the primary scholarly and professional use-case where Global South researchers consult LLMs. Bail (2024) documents rising LLM use in social science research; Chubb et al. (2022) show similar patterns in policy studies. Prior LLM-bias benchmarks (Moayeri et al. 2024; Myung et al. 2024 BLEnD) do not cover applied policy tasks specifically — they cover general trivia, encyclopedic facts, or cultural commonsense. This constitutes a well-defined population gap (Müller-Bloch & Kranz 2015, Table 2, empirical + population gap).

**Operationalization:** housing policy, environmental licensing, climate policy bodies, urban mobility policy sources, and federal budget allocations — drawn from the Institutional Analysis and Development (IAD) framework of Ostrom (2005) covering rules-in-use, stakeholders, and outcomes.

### S1.3.2 Domain D2: Socioeconomic reality

**Rationale.** Socioeconomic indicators (Gini coefficients, unemployment rates, poverty metrics) are the most-cited contextual variables in Global South applied research (World Bank Development Indicators; UNDP HDI reports). Stiglitz, Sen & Fitoussi (2009) and Piketty et al. (2022 World Inequality Report) established the canonical indicator set. LLM factual performance on these indicators has been tested only patchily in Mirza et al. (2024), with no systematic Global South coverage.

**Operationalization:** Gini coefficients, unemployment rates, regional inequality patterns, and cash-transfer policy responses.

### S1.3.3 Domain D3: Regional environmental context

**Rationale.** Environmental context is the most data-sparse domain for Global South countries — ground truth is often unavailable, officially reported figures have wide uncertainty bands (e.g., Nigeria's forest loss), and measurement regimes differ across countries (Brazil's PRODES vs US FIA). This heterogeneity stress-tests LLM handling of uncertainty and makes D3 the highest-variance domain in the study, following the maximum-variation sampling principle (Patton 2015).

**Operationalization:** forest loss / dominant environmental indicator, environmental NGOs, biodiversity primary sources — drawing on IPCC AR6 (2022) WG2 framings for climate adaptation relevance.

### S1.3.4 Why exactly 3 domains

Three domains gives cross-domain generalizability while keeping prompt authoring tractable for a pre-registered study. Following Shadish, Cook & Campbell (2002) on external validity, the three span distinct epistemic regimes: normative (D1 policy), descriptive-numeric (D2 socioeconomic), and physical-measurement (D3 environmental). Adding a fourth domain would increase authoring burden without clear increase in construct coverage, per Kane's validity-argument framework (Kane 2006).

---

## S1.4 Task type selection — 5 tasks

### S1.4.1 T1: Direct factual recall

**Rationale.** The canonical benchmark task in LLM evaluation (Lin et al. 2021 TruthfulQA; Rajpurkar et al. 2016 SQuAD; Kwiatkowski et al. 2019 NaturalQuestions). Tests knowledge retrieval without generation embellishment. Evaluation: `ground_truth_match` binary or partial.

### S1.4.2 T2: Open-ended generation

**Rationale.** Reflects how researchers actually use LLMs — "describe the institutional framework for X in country Y." Tests fluency plus factual accuracy jointly. Benchmark precedent in Wang et al. (2023) on instruction-following generation. Evaluation: rubric score 0-5 on completeness and correctness (following Liu et al. 2023 on rubric-based LLM evaluation).

### S1.4.3 T3: List extraction

**Rationale.** Tests the model's capacity to enumerate specific correct entities — ministries, NGOs, agencies — without hallucination. Benchmark precedent in Kasai et al. (2023) on structured output evaluation; Manvi et al. (2024) used analogous list-based prompts for geographic entities. **Hallucination** is primary rubric target, following the taxonomy of Ji et al. (2023) on faithfulness/factuality hallucinations.

### S1.4.4 T4: Primary-source recommendation

**Rationale.** A core research task specific to applied research: "which sources should I consult?" Tests whether models produce verifiable citations or plausible-sounding fabrications. Benchmark precedent in the RAG (Retrieval Augmented Generation) literature (Lewis et al. 2020) and in hallucination evaluations where citation verification is the gold standard (Bang et al. 2023). Evaluation: `rubric_score_citations` including DOI/URL verification.

### S1.4.5 T5: Confidence calibration

**Rationale.** Tests whether the model distinguishes between things it knows and things it doesn't — a central concern for responsible research use. Brier (1950) gives the canonical scoring rule. Lin et al. (2022) — "Teaching models to express their uncertainty in words" — established the methodology of asking models for numeric confidence. The Global South calibration question is nearly unstudied (Lin et al. used mostly English trivia).

### S1.4.6 Why exactly 5 tasks

The five tasks form a coverage spanning the Bloom's taxonomy-adjacent hierarchy of cognitive demands: recall (T1), synthesis (T2), extraction (T3), resource linking (T4), and metacognition (T5). This follows Krathwohl's (2002) revised taxonomy applied to research task analysis. Two tasks per task type per country gives 10 prompts per country, chosen as the minimum sample size compatible with our Monte Carlo power analysis (§SAP §3.3) while keeping expert-panel authoring burden tractable in the confirmatory study.

---

## S1.5 The 10-slot balanced factorial design

### S1.5.1 Cell structure

Each of the 15 countries (4 in pilot) receives the same 10 (domain, task) cells:

| Slot | Task | Domain | Coverage |
|---|---|---|---|
| P01 | T1 | D1 | Factual × Policy |
| P02 | T1 | D3 | Factual × Environment |
| P03 | T2 | D1 | Open-gen × Policy |
| P04 | T2 | D2 | Open-gen × Socioeconomic |
| P05 | T3 | D1 | List × Policy |
| P06 | T3 | D3 | List × Environment |
| P07 | T4 | D1 | Source × Policy |
| P08 | T4 | D3 | Source × Environment |
| P09 | T5 | D2 | Calibration × Socioeconomic |
| P10 | T5 | D1 | Calibration × Policy |

### S1.5.2 Balance rationale

- **Balance on Task (5 levels, 2 each):** enables GLMM random slopes for task × country without severe imbalance (following Barr et al. 2013 "Random effects structure for confirmatory hypothesis testing").
- **Balance on Domain (3 levels, 4/4/2):** unequal — D1 overrepresented relative to D3 and D2. Justified: D1 (policy) is the primary use-case, D2 and D3 included to test generalization across domains. Imbalance documented for transparency per Bürkner's brms manual recommendations (Bürkner 2017).
- **Country comparability:** identical 10 (domain, task) slots across all countries enables direct country contrasts without design confounds, per Kish (1965) cluster-sample best practices.

### S1.5.3 Why not a fully-crossed 3×5 = 15 design

A fully crossed 3-domain × 5-task design would require 15 (domain, task) cells per country, yielding 2×15×15 = 450 prompts minimum at 2 prompts/cell — doubling the authoring and review burden without a proportional increase in hypothesis-testing capacity. The 10-slot design sacrifices 5 (domain, task) cells while retaining balance on the dimension (task) that drives most hypothesis tests. This is the minimum viable design per Shadish, Cook & Campbell (2002) construct-validity guidance.

---

## S1.6 Pilot sizing and purpose

### S1.6.1 Why 40 prompts × 4 countries × 4 models

The pilot is explicitly exploratory and serves four distinct functions (Nosek et al. 2018 on exploratory vs confirmatory boundaries):

1. **Infrastructure validation** — API clients, Ollama local, response parsing, rubric evaluator
2. **Variance-component calibration** — update σ²_country, σ²_model, σ²_prompt estimates for Monte Carlo power
3. **Rubric stress-test** — identify where the 5-component rubric fails on real outputs
4. **SESOI recalibration** — adjust the smallest effect size of interest if observed pilot effect differs from assumed 10-percentage-point gap

Pilot sample size (n=320 responses = 4 countries × 4 models × 10 prompts × 2 reps) is small by design. It is **not** powered to test H1-H5 confirmatorily; it provides bias-variance sketch for SAP update only. The principle is to "commit to infrastructure before committing to inference" (Open Science Collaboration 2015).

### S1.6.2 Country selection for pilot

Four countries span three Global-South regions + one Global-North control, representing extreme corners of the 15-country confirmatory sample:

- **BRA** — Latin America, Portuguese, upper-middle income, Joshi class 3
- **NGA** — Africa, English (post-colonial lingua franca), lower-middle income, Joshi class 1
- **IND** — South Asia, Hindi + English, lower-middle income, Joshi class 4 (Hindi)
- **USA** — Global North, English, high income, Joshi class 5 (English)

This sample mimics the maximum-variation sampling strategy (Patton 2015) on the stratification axes documented in `etapa2b_selecao_paises.md`.

### S1.6.3 Model selection for pilot

Four models covering 3 tiers:
- **Claude Haiku 4.5** (closed accessible, Anthropic) — fast, cheap, widely used proxy for "accessible closed frontier"
- **GPT-5-mini** (closed accessible, OpenAI) — second vendor for accessible closed
- **Gemini 2.5 Flash** (closed accessible, Google) — third vendor, free tier
- **Lince-Mistral 7B** (open-weight regional, PUCRS) — regional open proxy for H3 pilot signal

Rationale: three closed-accessible vendors for internal-consistency check + one open regional model for H3 signal. Omits Tier A open frontier and Tier E closed frontier (GPT-5) to reserve API/Ollama setup effort for confirmatory.

---

## S1.7 Language matrix — sparse factorial

### S1.7.1 Theoretical grounding

The language × country matrix follows the **Linguistic Resource Hypothesis** (Joshi et al. 2020 "The state and fate of linguistic diversity and inclusion in the NLP world"): corpus representation of a language drives LLM performance on that language, creating a "resource curse" for low-resource languages. The Joshi taxonomy (classes 0-5) operationalizes this hypothesis.

For testing H2 (language × country interaction), we need variation across both dimensions without a full 15×6 = 90-cell design (which would triple prompt count). The sparse factorial (each country tested in EN + 0-1 regional language) is the minimum design that enables interaction testing per Davis et al. (2013) on sparse factorial experiments.

### S1.7.2 Pilot language coverage (English only)

The pilot is executed in English only to isolate infrastructure and domain-accuracy validation from language confounds. Multilingual evaluation is deferred to confirmatory study where expert panel validation of translations is feasible. This follows the "one dimension at a time" principle for pilot studies (Thabane et al. 2010 — "A tutorial on pilot studies: the what, why and how").

---

## S1.8 Pre-registration and open science

### S1.8.1 OSF pre-registration

SAP is deposited at OSF using the AsPredicted template (Nosek et al. 2018; Chambers & Tzavella 2022 on pre-registration in behavioral sciences) prior to confirmatory data collection. The pre-registration is public upon OSF registration; DOI cited in the main manuscript.

### S1.8.2 Exploratory vs confirmatory boundary

Following Wagenmakers et al. (2012) and Nosek et al. (2018), we explicitly mark:
- **Pilot data** (this supplement + `data/pilot_202604/`): exploratory, not used for confirmatory inference
- **Confirmatory data** (forthcoming `data/raw/llm_responses/`): pre-registered, primary inference

Analyses that emerge from pilot inspection but are not pre-registered will be clearly labeled "post-hoc exploratory" in the manuscript.

### S1.8.3 Five pillars of open science

| Pillar | Implementation | Licence |
|---|---|---|
| Open Access (publication) | APC via CAPES/Cell Press agreement | CC-BY 4.0 |
| Open Data | Zenodo deposit post-publication | CC-BY 4.0 |
| Open Code | GitHub public repository | MIT |
| **Open Weights** (novel in this study) | 10 of 14 models audited have fully open weights on Hugging Face | Apache 2.0, Llama License, MIT |
| Open Science | OSF pre-registration | CC-BY 4.0 |

"Five pillars" framing adapted from Nosek (2019) "Strategy for culture change".

---

## S1.9 Reference list (S1)

- Abdilla, A., & Fitch, R. (2017). *Indigenous Knowledge Systems and Pattern Thinking*. Old Ways, New.
- Bail, C. A. (2024). Can Generative AI improve social science? *PNAS*, 121(21).
- Bang, Y., et al. (2023). A Multitask, Multilingual, Multimodal Evaluation of ChatGPT on Reasoning, Hallucination, and Interactivity. *arXiv:2302.04023*.
- Barr, D. J., et al. (2013). Random effects structure for confirmatory hypothesis testing. *Journal of Memory and Language*, 68(3), 255-278.
- Birhane, A., et al. (2022). The Values Encoded in Machine Learning Research. *FAccT '22*.
- Brier, G. W. (1950). Verification of Forecasts Expressed in Terms of Probability. *Monthly Weather Review*, 78(1).
- Bürkner, P.-C. (2017). brms: An R Package for Bayesian Multilevel Models. *Journal of Statistical Software*, 80(1).
- Chambers, C. (2019). What's next for Registered Reports? *Nature*, 573, 187-189.
- Chambers, C., & Tzavella, L. (2022). The past, present, and future of Registered Reports. *Nature Human Behaviour*, 6, 29-42.
- Chancel, L., Piketty, T., Saez, E., Zucman, G. (2022). *World Inequality Report 2022*. World Inequality Lab.
- Chubb, J., et al. (2022). Speeding up to keep up: exploring the use of AI in the research process. *AI & Society*, 37, 1439-1457.
- Davis, T. A., et al. (2013). Sparse factorial designs for experiments. *Technometrics*, 55(2).
- D'Ignazio, C., & Klein, L. (2020). *Data Feminism*. MIT Press.
- IPCC (2022). *Climate Change 2022: Impacts, Adaptation and Vulnerability* (AR6 WG2).
- Ji, Z., et al. (2023). Survey of Hallucination in Natural Language Generation. *ACM Computing Surveys*, 55(12).
- Joshi, P., et al. (2020). The State and Fate of Linguistic Diversity and Inclusion in the NLP World. *ACL 2020*.
- Kane, M. T. (2006). Validation. In *Educational Measurement* (4th ed.). ACE/Praeger.
- Kasai, J., et al. (2023). RealtimeQA: What's the Answer Right Now? *NeurIPS 2023*.
- Kish, L. (1965). *Survey Sampling*. Wiley.
- Krathwohl, D. R. (2002). A Revision of Bloom's Taxonomy. *Theory Into Practice*, 41(4).
- Kukutai, T., & Taylor, J. (2016). *Indigenous Data Sovereignty*. ANU Press.
- Kwiatkowski, T., et al. (2019). Natural Questions: A Benchmark for Question Answering Research. *TACL*, 7.
- Lewis, P., et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. *NeurIPS 2020*.
- Lin, S., Hilton, J., & Evans, O. (2021). TruthfulQA: Measuring How Models Mimic Human Falsehoods. *arXiv:2109.07958*.
- Lin, S., et al. (2022). Teaching Models to Express Their Uncertainty in Words. *TMLR*.
- Liu, Y., et al. (2023). G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment. *EMNLP 2023*.
- Manvi, R., et al. (2024). Large Language Models are Geographically Biased. *ICML 2024*.
- Mirza, F., et al. (2024). Global-Liar: Factuality of LLMs over Time and Geographic Regions. *NAACL 2024*.
- Moayeri, M., Tabassi, S., & Feizi, S. (2024). WorldBench: Quantifying Geographic Disparities in LLM Factual Recall. *FAccT 2024*.
- Mohamed, S., Png, M.-T., & Isaac, W. (2020). Decolonial AI: Decolonial Theory as Sociotechnical Foresight in Artificial Intelligence. *Philosophy & Technology*, 33, 659-684.
- Müller-Bloch, C., & Kranz, J. (2015). A Framework for Rigorously Identifying Research Gaps in Qualitative Literature Reviews. *ICIS 2015*.
- Myung, J., et al. (2024). BLEnD: A Benchmark for LLMs on Everyday Knowledge in Diverse Cultures and Languages. *NeurIPS 2024 Datasets*.
- Nosek, B. A. (2019). Strategy for Culture Change. *Center for Open Science*.
- Nosek, B. A., et al. (2018). The preregistration revolution. *PNAS*, 115(11), 2600-2606.
- Open Science Collaboration (2015). Estimating the Reproducibility of Psychological Science. *Science*, 349.
- Ostrom, E. (2005). *Understanding Institutional Diversity*. Princeton University Press.
- Patton, M. Q. (2015). *Qualitative Research and Evaluation Methods* (4th ed.). Sage.
- Piketty, T., Saez, E., & Zucman, G. (2022). World Inequality Report 2022. (full citation above as Chancel et al.)
- Quijano, A. (2000). Coloniality of Power, Eurocentrism, and Latin America. *Nepantla: Views from South*, 1(3).
- Rajpurkar, P., et al. (2016). SQuAD: 100,000+ Questions for Machine Comprehension of Text. *EMNLP 2016*.
- Shadish, W. R., Cook, T. D., & Campbell, D. T. (2002). *Experimental and Quasi-Experimental Designs for Generalized Causal Inference*. Houghton Mifflin.
- Stiglitz, J., Sen, A., & Fitoussi, J.-P. (2009). *Report by the Commission on the Measurement of Economic Performance and Social Progress*. Paris.
- Subramanian, S., & Jayaraj, D. (2021). Global and National Inequality: Measurement and Analysis. *Oxford Research Encyclopedia of Economics*.
- Thabane, L., et al. (2010). A tutorial on pilot studies: the what, why and how. *BMC Medical Research Methodology*, 10(1).
- Wagenmakers, E. J., et al. (2012). An Agenda for Purely Confirmatory Research. *Perspectives on Psychological Science*, 7(6).
- Wang, Y., et al. (2023). Self-Instruct: Aligning Language Models with Self-Generated Instructions. *ACL 2023*.
- Wilkinson, M. D., et al. (2016). The FAIR Guiding Principles for scientific data management and stewardship. *Scientific Data*, 3(1).
- Zhang, J., et al. (2023). AI for the Global South: A Framework for Responsible Innovation. *AI & Ethics*, 3, 423-438.
