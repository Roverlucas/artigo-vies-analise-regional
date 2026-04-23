# Execution Guide — Starting Real Work on the Benchmark

This guide picks up where the specification pipeline ended. At this point you
have a complete pre-specified research project waiting for empirical execution.
The steps below are ordered by dependency; parallelize where noted.

---

## Phase 0 — Local setup (30 minutes)

```bash
# Clone your repo
git clone https://github.com/Roverlucas/artigo-vies-analise-regional
cd artigo-vies-analise-regional

# Create isolated environment
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r code/requirements.txt

# Verify everything runs on synthetic data
cd code
python run_all.py
```

Expected: `Pipeline complete.` with 5 OK checks at the bottom.

---

## Phase 1 — Institutional prerequisites (4–6 weeks, mostly waiting)

These run in parallel with Phase 2. Start them **first** because they block.

### 1.1 Research ethics (CEP via Plataforma Brasil)

- Submit project protocol via UTFPR's CEP.
- Include: expert-panel protocol, consent form, co-authorship agreement.
- Expected duration: 30-60 days.
- Use `docs/etapa5_proposta_execucao.md` §4 as the project basis.

### 1.2 API research credits

Apply in parallel:

- **OpenAI Researcher Access Program:** https://openai.com/form/researcher-access-program
- **Anthropic Academic API Access:** via support channel, cite Lucas's institutional affiliation
- **Google for Researchers:** https://research.google/outreach/
- **Maritaca AI researcher program:** contact via site (usually favorable for Brazilian universities)

Total expected cost if fully self-funded: ~R$ 2,100-2,800 (see
`docs/etapa5_proposta_execucao.md` §3.3 for breakdown).

### 1.3 OSF pre-registration account

- Create account at https://osf.io
- Initialize a new registration using the "AsPredicted" template
- Fill with content from `docs/etapa4_sap.md`
- Do **NOT** commit to final lock yet — wait until Phase 2 prompts are finalized

---

## Phase 2 — Expert panel and prompt authoring (8 weeks)

### 2.1 Recruit experts (weeks 1-2)

Target: 2-3 per region. Contacts by region:

**Latin America:**
- CLACSO network via UTFPR contacts
- Specific areas: public policy, socioeconomic, environmental

**Africa:**
- CODESRIA network
- Consider partner universities: Witwatersrand (ZA), Nairobi (KE)

**Asia:**
- Regional NLP researchers via ACL affinity groups (SIGCLII, SEAMLESS)
- Specific contacts: IIT Delhi (IN), BPSMR (BD)

**Template email** to adapt:

> Subject: Invitation: co-authorship on LLM bias benchmark for Global South
> policy research
>
> Dear [Name],
>
> I am conducting a pre-registered benchmark study on geographic bias in
> Large Language Models, specifically evaluating their reliability when used
> for applied policy research in the Global South. The study covers 15
> countries stratified along UNCTAD, Joshi linguistic-resource, and World
> Bank income axes, with six frontier and regionally-trained LLMs.
>
> I would like to invite you to join as an expert panelist for [region/country].
> Your role would involve: (1) authoring ~30 research-grade prompts on public
> policy, socioeconomic, or environmental questions relevant to your country;
> (2) participating in a rubric-calibration pilot; (3) receiving co-authorship
> on the resulting manuscript (targeted at Patterns, Cell Press).
>
> Time commitment: estimated 15-20 hours over 6 weeks.
>
> The pre-registration, ethics approval (Plataforma Brasil), and complete
> project documentation are openly available at:
> https://github.com/Roverlucas/artigo-vies-analise-regional
>
> Would you be interested in participating? I am happy to discuss further.
>
> Best regards,
> Lucas [Surname]

### 2.2 Prompt authoring (weeks 3-5)

- Share `docs/etapa3_metodologia.md` §5.1 and the template structure in
  `code/benchmark/prompts.py`.
- Each expert produces ~30 prompts covering their country across 3 domains
  × 5 task types.
- Use a shared Airtable or Google Sheets for collection; final export
  as CSV, then convert to JSONL via `code/benchmark/prompts.py`.

### 2.3 Back-translation and quality checks (week 6)

- Professional translators for EN → PT, ES, HI, SW, BN, ID, etc.
- Back-translate; reject prompts with semantic shift.
- Hire via UTFPR institutional procurement.

### 2.4 Pilot study (weeks 7-8)

- Select 50 representative prompts.
- Run on 2 LLMs (GPT-5 and Claude Opus).
- Two expert raters apply rubric.
- Compute Krippendorff's α.
- **If α < 0.70**: revise rubric + re-train raters + re-pilot. Do not proceed.
- **If α ≥ 0.70**: proceed to Phase 3.

---

## Phase 3 — OSF lock and ground truth collection (2 weeks)

### 3.1 Ground truth download (weeks 9-10)

Use `data/ground_truth/SOURCES_CATALOG.md` as checklist. For each country:

- Download/scrape relevant documents from the listed official sources.
- Store in `data/raw/ground_truth/{country_iso3}/` with version metadata.
- Compute SHA-256 hashes into `data/_provenance.json`.

For documents in non-Latin scripts (AR, HI, BN, JA), use OCR with
`pytesseract` where needed; verify manually.

### 3.2 OSF pre-registration lock

At the end of week 10, before any LLM calls:

- Commit final prompts to `data/raw/prompts/v1_final.jsonl`
- Compute SHA-256 of the prompts file
- Upload to OSF; mark registration as "locked"
- Record OSF DOI in `docs/progress.md` and `latex/main.tex`

**From this point forward, no changes to prompts, rubric, or primary
analysis specifications are allowed without documentation in the Deviation
Protocol.**

---

## Phase 4 — API execution (2-3 weeks)

### 4.1 Configure keys

```bash
# Create .env in repo root (gitignored)
cat > .env <<EOF
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AI...
MARITACA_API_KEY=...
TOGETHER_API_KEY=...   # for Llama/Qwen via Together.ai
EOF
```

### 4.2 Implement real API dispatch

In `code/benchmark/llm_clients.py`, fill in the six `_call_*` functions that
are currently `NotImplementedError` stubs. Each provider's SDK documentation
is authoritative; expected implementation is ~15 lines per provider.

### 4.3 Run pilot batch

Before full execution, run 5% random sample as smoke test:

```bash
export BENCHMARK_SYNTHETIC=0
python -m benchmark.run_experiment \
    --prompts ../data/raw/prompts/v1_final.jsonl \
    --output ../data/raw/llm_responses/pilot_5pct.jsonl \
    --subset 0.05
```

(You may need to add `--subset` flag to `run_experiment.py` — a small
extension.)

Verify:
- Responses look sane
- Quality gates trigger appropriately
- Cost tracking matches estimate

### 4.4 Full execution

```bash
python -m benchmark.run_experiment \
    --prompts ../data/raw/prompts/v1_final.jsonl \
    --output ../data/raw/llm_responses/run_$(date +%Y%m%d).jsonl
```

Runner is resumable. Expect 24-72h wall-clock depending on rate limits.

---

## Phase 5 — Rubric evaluation (3-4 weeks)

### 5.1 Export responses for raters

Two raters per response (blinded to model identity). Use Airtable base
configured with:
- Fields per rubric subcomponent (binary, Likert 0-5, Brier, etc.)
- Model ID hidden
- Random assignment of raters to balance load

### 5.2 Adjudication round

- Any disagreement > 2 points on 0-5 scales: adjudicate by senior rater.
- Log disagreement patterns for methodological supplement.

### 5.3 Compute final Krippendorff's α

Required report: `results/rater_reliability.md` with α per rubric item.

---

## Phase 6 — Analysis and writing (4-6 weeks)

### 6.1 Replace synthetic data with real

```bash
# Analytic dataset construction from raw responses + rubric ratings
python -m benchmark.build_analytic_dataset  # (write this script; follows SAP §5 pipeline)

# Freeze and hash
python -m benchmark.freeze_dataset  # (write this; generates hash to OSF)
```

### 6.2 Run primary analyses

```bash
cd code
python analysis/04_inference.py  # Now reads real data, not synthetic
python analysis/05_robustness.py  # Write this; implements SAP §7
python analysis/06_mediation.py   # Write this; semopy for H4
```

### 6.3 Power analysis cross-validation

```bash
python -m benchmark.power.power_simulation --grid --n_iter 2000
```

Report in Supplementary §S4.

### 6.4 Fill in results in `latex/sections/04_results.tex`

Replace every `[PLACEHOLDER]` and `\simvalue{...}` with real observed values.
The narrative structure stays; only numbers change.

### 6.5 Update discussion

Review `latex/sections/05_discussion.tex` for conditional phrases ("if
confirmed...", "expected direction") and finalize based on real findings.

---

## Phase 7 — Pre-submission (2-3 weeks)

Return to the pipeline skills for remaining stages:

- **Stage 7:** `journal-publication-strategist` for cover letter, highlights,
  graphical abstract brief, anti-rejection checklist.
- **Stage 8:** `academic-article-reviser` to polish English prose, remove
  AI-generated writing patterns, fact-check.
- **Stage 9:** `formatador-cientifico` to adapt template to Cell Press
  Patterns conventions, LaTeX formatting, reference validation.
- **Stage 10:** `banca-revisores-cientificos` for internal peer review
  simulation before submission.

Execute in Claude with the artifacts from this repo.

---

## Estimated full timeline

| Phase | Duration | Can parallelize with |
|---|---|---|
| 0. Setup | 30 min | — |
| 1. Institutional (CEP, credits, OSF) | 4-6 weeks | 2 |
| 2. Panel + prompts | 8 weeks | 1 |
| 3. OSF lock + ground truth | 2 weeks | Start of 4 |
| 4. API execution | 2-3 weeks | Start of 5 |
| 5. Rubric evaluation | 3-4 weeks | 6.1 |
| 6. Analysis + writing | 4-6 weeks | — |
| 7. Pre-submission | 2-3 weeks | — |
| **Total** | **~6 months** | |

---

## Checkpoints for progress tracking

Maintain `docs/progress.md` updated. Key gates:

- [ ] Phase 1 complete: CEP approval + API credits secured
- [ ] Phase 2 complete: N prompts = 450 authored, α ≥ 0.70
- [ ] Phase 3 complete: OSF locked with DOI
- [ ] Phase 4 complete: All API responses collected, quality gates passed
- [ ] Phase 5 complete: Rubric evaluation with α reported
- [ ] Phase 6 complete: All `[PLACEHOLDER]` and `\simvalue{}` replaced
- [ ] Phase 7 complete: Ready for submission

Good luck.
