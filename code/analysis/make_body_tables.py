#!/usr/bin/env python3
"""make_body_tables.py — as tabelas do CORPO que carregam números do congelamento
são geradas daqui, nunca editadas à mão.

Por que: em 2026-09-21 a Tabela 2 (acurácia por modelo) foi atualizada à mão a
partir de um congelamento e o pipeline rodou de novo depois (correção da chave de
Bangladesh); a tabela ficou com 0,690 para o DeepSeek onde o congelamento dizia
0,687. O suplemento, gerado por script, estava certo; o corpo, editado à mão,
não. Tabela editada à mão é tabela que diverge.

Gera (EN e PT):
  latex/sections/tables/tab_conf_model.tex / tab_conf_model_PT.tex
  latex/sections/tables/tab_conf_task.tex  / tab_conf_task_PT.tex
"""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
c = json.loads((ROOT / "data/processed/freeze_all_effects.json").read_text())["corrigido"]
OUT = ROOT / "latex/sections/tables"; OUT.mkdir(parents=True, exist_ok=True)
NAMES = {'deepseek_v3':'DeepSeek-V3','gpt5':'GPT-5','gemini_flash':'Gemini~2.5~Flash','gpt5_mini':'GPT-5-mini',
         'claude_haiku':'Claude Haiku~4.5','qwen3_32b':'Qwen3 32B','command_rp':'Command~R+','llama33_70b':'Llama~3.3 70B',
         'llama4_scout':'Llama~4 Scout','qwen3_14b':'Qwen3 14B','phi4_14b':'Phi-4 14B','gpt_oss_120b':'GPT-OSS 120B',
         'llama31_8b':'Llama~3.1 8B','cabra_mistral_7b':'Cabra-Mistral~7B'}
TASK_EN = {'T5':'T5 (applied recommendation)','T3':'T3 (health-evidence synth.)','T4':'T4 (policy instruments)',
           'T2':'T2 (local factual datum)','T1':'T1 (technical standard)'}
TASK_PT = {'T5':'T5 (recomendação aplicada)','T3':'T3 (síntese de evid.\\ em saúde)','T4':'T4 (instrumentos de política)',
           'T2':'T2 (dado factual local)','T1':'T1 (padrão técnico)'}
hdr = "% AUTO-GERADO por code/analysis/make_body_tables.py a partir de freeze_all_effects.json - NAO EDITAR"
models = sorted(c["por_modelo"].items(), key=lambda x: -x[1][0])
for lang, fn, head in (("en", "tab_conf_model.tex", "Model & $N$ & Mean \\\\"), ("pt", "tab_conf_model_PT.tex", "Modelo & $N$ & Média \\\\")):
    lines = ["\\begin{tabular}{lrr}", "\\toprule", head, "\\midrule"]
    for k, (m, n) in models:
        lines.append(f"{NAMES[k]:16s} & {n} & {m:.3f} \\\\")
    lines += ["\\bottomrule", "\\end{tabular}"]
    (OUT / fn).write_text(hdr + "\n" + "\n".join(lines) + "\n", encoding="utf-8")
tasks = sorted(c["por_task"].items(), key=lambda x: -x[1][0])
for lang, fn, T, head in (("en", "tab_conf_task.tex", TASK_EN, "Task & $N$ & Mean \\\\"), ("pt", "tab_conf_task_PT.tex", TASK_PT, "Tarefa & $N$ & Média \\\\")):
    lines = ["\\begin{tabular}{lrr}", "\\toprule", head, "\\midrule"]
    for k, (m, n) in tasks:
        nn = f"{n:,}".replace(",", "{,}") if lang == "en" else f"{n:,}".replace(",", ".")
        lines.append(f"{T[k]:30s} & {nn} & {m:.3f} \\\\")
    lines += ["\\bottomrule", "\\end{tabular}"]
    (OUT / fn).write_text(hdr + "\n" + "\n".join(lines) + "\n", encoding="utf-8")
print("tabelas do corpo geradas de", ROOT / "data/processed/freeze_all_effects.json")
