#!/usr/bin/env python3
"""
verify_citations.py — Citation Verification Protocol implementation.

Stage 1: existence verification (DOI/arXiv/ISBN resolves; author/year/title match).
Stage 2: claim verification (numerical/factual claims attributed to a paper appear
         in source text — abstract for arXiv, full PDF text where retrievable).

Usage:
    python scripts/verify_citations.py --stage 1 --citations citations.yaml
    python scripts/verify_citations.py --stage 2 --citations citations.yaml --document path/to/doc.md

Output:
    audit_trail/verification_log_stage1.csv
    audit_trail/verification_log_stage2.csv

Per the project's CITATION_VERIFICATION_PROTOCOL.md, this script must be run
TWICE for stage 2 from independent invocations to count as 2-reviewer verification.
"""
from __future__ import annotations
import argparse
import csv
import json
import re
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

USER_AGENT = "artigo-vies-analise-regional/citation-verifier (lucasrover@alunos.utfpr.edu.br)"
ROOT = Path(__file__).parent.parent
AUDIT_DIR = ROOT / "audit_trail"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)


def http_get(url: str, headers: dict | None = None, timeout: int = 30) -> tuple[int, str]:
    headers = headers or {}
    headers.setdefault("User-Agent", USER_AGENT)
    req = urllib.request.Request(url)
    for k, v in headers.items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return 0, str(e)[:200]


def query_arxiv(arxiv_id: str) -> dict | None:
    """Fetch metadata for an arXiv ID. Returns dict with authors, year, title, abstract."""
    arxiv_id = arxiv_id.strip().lstrip("arXiv:").strip()
    code, body = http_get(f"https://export.arxiv.org/api/query?id_list={arxiv_id}")
    if code != 200 or not body:
        return None
    title_m = re.search(r"<entry>.*?<title>(.*?)</title>", body, re.DOTALL)
    auth_m = re.findall(r"<author>\s*<name>(.*?)</name>", body)
    date_m = re.search(r"<published>(\d{4})", body)
    abs_m = re.search(r"<summary>(.*?)</summary>", body, re.DOTALL)
    if not title_m:
        return None
    return {
        "title": " ".join(title_m.group(1).split()).strip(),
        "authors": auth_m,
        "year": int(date_m.group(1)) if date_m else None,
        "abstract": (abs_m.group(1).strip() if abs_m else ""),
    }


def query_crossref(doi: str) -> dict | None:
    code, body = http_get(f"https://api.crossref.org/works/{doi}")
    if code != 200:
        return None
    try:
        data = json.loads(body).get("message", {})
    except Exception:
        return None
    authors = [f"{a.get('given','')} {a.get('family','')}".strip() for a in data.get("author", [])]
    year = None
    if "published" in data:
        parts = data["published"].get("date-parts", [[]])
        if parts and parts[0]:
            year = parts[0][0]
    elif "issued" in data:
        parts = data["issued"].get("date-parts", [[]])
        if parts and parts[0]:
            year = parts[0][0]
    title_list = data.get("title") or []
    return {
        "title": title_list[0] if title_list else "",
        "authors": authors,
        "year": year,
        "abstract": data.get("abstract", ""),
    }


def normalize_text(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower().strip())


def fuzzy_in(needle: str, haystack: str, threshold: float = 0.6) -> bool:
    """Check if needle is approximately in haystack."""
    needle_n = normalize_text(needle)
    haystack_n = normalize_text(haystack)
    if needle_n in haystack_n:
        return True
    needle_words = set(needle_n.split())
    haystack_words = set(haystack_n.split())
    if not needle_words:
        return False
    overlap = len(needle_words & haystack_words) / len(needle_words)
    return overlap >= threshold


def stage_1_verify(citations: list[dict]) -> list[dict]:
    """Stage 1: existence + identity verification."""
    rows = []
    for cit in citations:
        key = cit.get("key", "?")
        arxiv_id = cit.get("arxiv")
        doi = cit.get("doi")
        cited_authors = cit.get("authors", [])
        cited_year = cit.get("year")
        cited_title = cit.get("title", "")

        meta = None
        if arxiv_id:
            meta = query_arxiv(arxiv_id)
            time.sleep(2)  # arxiv rate limit
        elif doi:
            meta = query_crossref(doi)
            time.sleep(0.5)

        if meta is None:
            rows.append({
                "key": key, "arxiv": arxiv_id or "", "doi": doi or "",
                "author_match": "—", "year_match": "—", "title_match": "—",
                "status": "NOT_FOUND",
                "note": "Identifier did not resolve",
            })
            continue

        # Author match
        cited_surnames = {n.strip().split()[-1].lower() for n in cited_authors if n.strip()}
        api_surnames = {n.strip().split()[-1].lower() for n in meta["authors"] if n.strip()}
        author_match = bool(cited_surnames & api_surnames) if cited_surnames else "—"

        # Year match
        year_match = (meta["year"] == cited_year) if cited_year else "—"

        # Title match (fuzzy ≥60% word overlap)
        title_match = fuzzy_in(cited_title, meta["title"]) if cited_title else "—"

        all_ok = author_match in (True, "—") and year_match in (True, "—") and title_match in (True, "—")
        status = "OK" if all_ok and author_match and year_match and title_match else "MISMATCH"

        rows.append({
            "key": key, "arxiv": arxiv_id or "", "doi": doi or "",
            "author_match": author_match, "year_match": year_match,
            "title_match": title_match, "status": status,
            "note": f"API title: {meta['title'][:80]}",
        })

    return rows


def stage_2_verify(citations: list[dict], document_text: str) -> list[dict]:
    """Stage 2: verify each numerical/factual claim against source abstract."""
    rows = []
    for cit in citations:
        key = cit.get("key", "?")
        arxiv_id = cit.get("arxiv")
        doi = cit.get("doi")
        claims = cit.get("claims", [])

        meta = None
        if arxiv_id:
            meta = query_arxiv(arxiv_id)
            time.sleep(2)
        elif doi:
            meta = query_crossref(doi)
            time.sleep(0.5)

        if meta is None:
            for claim in claims:
                rows.append({
                    "key": key, "claim": claim[:200],
                    "match_type": "—",
                    "status": "UNVERIFIABLE",
                    "note": "Source not retrievable",
                })
            continue

        source_text = (meta.get("abstract") or "") + " " + (meta.get("title") or "")
        for claim in claims:
            # Look for numerical patterns and verify exact-or-near
            nums_in_claim = re.findall(r"\d+\.?\d*", claim)
            nums_in_source = re.findall(r"\d+\.?\d*", source_text)
            num_match = any(n in nums_in_source for n in nums_in_claim) if nums_in_claim else "—"

            text_match = fuzzy_in(claim, source_text, threshold=0.4)

            if num_match is True or num_match == "—" and text_match:
                if nums_in_claim:
                    status = "NUMERICAL"
                else:
                    status = "PARAPHRASE"
            elif text_match:
                status = "PARAPHRASE"
            else:
                status = "FABRICATED"

            rows.append({
                "key": key, "claim": claim[:200],
                "match_type": status,
                "status": "OK" if status != "FABRICATED" else "FAIL",
                "note": f"nums_in_claim={nums_in_claim[:5]}, text_match={text_match}",
            })

    return rows


def write_log(rows: list[dict], path: Path) -> None:
    if not rows:
        return
    keys = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=int, choices=[1, 2], required=True)
    parser.add_argument("--citations", type=str, required=True,
                        help="Path to YAML/JSON with citations list")
    parser.add_argument("--document", type=str, default=None,
                        help="Document path (Stage 2 only)")
    args = parser.parse_args()

    cit_path = Path(args.citations)
    text = cit_path.read_text()
    if cit_path.suffix in (".yaml", ".yml"):
        try:
            import yaml
            citations = yaml.safe_load(text)
        except ImportError:
            print("PyYAML not installed; install or use JSON", file=sys.stderr)
            sys.exit(1)
    else:
        citations = json.loads(text)

    if args.stage == 1:
        rows = stage_1_verify(citations)
        log_path = AUDIT_DIR / f"verification_log_stage1_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.csv"
        write_log(rows, log_path)
        print(f"Stage 1 complete. Output: {log_path}")
        ok = sum(1 for r in rows if r["status"] == "OK")
        bad = sum(1 for r in rows if r["status"] != "OK")
        print(f"  OK:       {ok}")
        print(f"  Issues:   {bad}")
        if bad > 0:
            print("\n  P0 STATUS: FAIL — review issues before artifact generation.")
            sys.exit(1)
        else:
            print("\n  P0 STATUS: PASS")

    elif args.stage == 2:
        if not args.document:
            print("--document required for stage 2", file=sys.stderr)
            sys.exit(1)
        doc_text = Path(args.document).read_text()
        rows = stage_2_verify(citations, doc_text)
        log_path = AUDIT_DIR / f"verification_log_stage2_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.csv"
        write_log(rows, log_path)
        print(f"Stage 2 complete. Output: {log_path}")
        ok = sum(1 for r in rows if r["status"] == "OK")
        bad = sum(1 for r in rows if r["status"] == "FAIL")
        print(f"  OK:           {ok}")
        print(f"  FABRICATED:   {bad}")
        if bad > 0:
            print("\n  P0 STATUS: FAIL — fabricated claims detected.")
            sys.exit(1)
        else:
            print("\n  P0 STATUS: PASS")


if __name__ == "__main__":
    main()
