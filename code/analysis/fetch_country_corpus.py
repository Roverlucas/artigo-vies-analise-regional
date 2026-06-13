"""
fetch_country_corpus.py — COUNTRY-corpus measures (geo-entity coverage).

For each of the 25 countries, fetch reproducible, official Wikimedia measures of
how much the encyclopedic corpus is ABOUT the country (language-independent):
  - en_wiki_bytes : byte length of the English Wikipedia article on the country
  - wd_sitelinks  : number of Wikipedia language editions with an article on the
                    country (Wikidata sitelink count) — a breadth-of-coverage proxy
  - wd_statements : number of Wikidata statements on the country entity

These address H1/H4 measured IN ENGLISH: a residual North/South gap cannot be a
language-corpus effect (all queried in English), so the candidate mechanism is
country representation. Source: Wikimedia/Wikidata public APIs (read 2026-06).

Output: data/confirmatory_PRIVATE/analysis/country_corpus_measures.json
"""
from __future__ import annotations
import json, urllib.request, urllib.parse, time
from pathlib import Path

OUT = Path(__file__).parent.parent.parent / "data" / "confirmatory_PRIVATE" / "analysis" / "country_corpus_measures.json"

# ISO3 -> English Wikipedia article title
TITLE = {
    "AGO": "Angola", "ARG": "Argentina", "AUS": "Australia", "BGD": "Bangladesh",
    "BRA": "Brazil", "CAN": "Canada", "CHL": "Chile", "COL": "Colombia",
    "DEU": "Germany", "EGY": "Egypt", "FRA": "France", "IDN": "Indonesia",
    "IND": "India", "ITA": "Italy", "JPN": "Japan", "KEN": "Kenya",
    "KOR": "South Korea", "MEX": "Mexico", "NGA": "Nigeria", "PER": "Peru",
    "PHL": "Philippines", "PRT": "Portugal", "UK": "United Kingdom",
    "USA": "United States", "ZAF": "South Africa",
}
UA = {"User-Agent": "air-policy-bias-research/1.0 (academic; contact via OSF)"}


def _get(url, retries=4):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                time.sleep(2.0 * (attempt + 1) + 1.0)  # backoff
                continue
            raise


def en_wiki_info(title):
    """Return (bytes, wikidata_qid) for the English article."""
    q = urllib.parse.urlencode({"action": "query", "titles": title,
        "prop": "info|pageprops", "ppprop": "wikibase_item", "format": "json"})
    d = _get("https://en.wikipedia.org/w/api.php?" + q)
    pages = d["query"]["pages"]
    pg = next(iter(pages.values()))
    return pg.get("length"), pg.get("pageprops", {}).get("wikibase_item")


def wikidata_info(qid):
    """Return (sitelink_count, statement_count) for the Wikidata entity."""
    q = urllib.parse.urlencode({"action": "wbgetentities", "ids": qid,
        "props": "sitelinks|claims", "format": "json"})
    d = _get("https://www.wikidata.org/w/api.php?" + q)
    ent = d["entities"][qid]
    sitelinks = len(ent.get("sitelinks", {}))
    statements = sum(len(v) for v in ent.get("claims", {}).values())
    return sitelinks, statements


def main():
    # resume: keep countries already fetched OK, only retry the rest
    out = {}
    if OUT.exists():
        out = {k: v for k, v in json.loads(OUT.read_text()).items()
               if v.get("en_wiki_bytes")}
    todo = {iso: t for iso, t in TITLE.items() if iso not in out}
    print(f"  already OK: {len(out)} | to fetch: {len(todo)}")
    for iso, title in todo.items():
        try:
            byts, qid = en_wiki_info(title)
            sl, st = (None, None)
            if qid:
                sl, st = wikidata_info(qid)
            out[iso] = {"title": title, "qid": qid, "en_wiki_bytes": byts,
                        "wd_sitelinks": sl, "wd_statements": st}
            print(f"  {iso:4s} {title:18s} bytes={byts} sitelinks={sl} statements={st}")
        except Exception as e:
            out[iso] = {"title": title, "error": str(e)}
            print(f"  {iso:4s} {title:18s} ERROR {e}")
        time.sleep(1.5)  # be polite to the API
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    ok = sum(1 for v in out.values() if v.get("en_wiki_bytes"))
    print(f"DONE. {ok}/{len(out)} countries -> {OUT.name}")


if __name__ == "__main__":
    main()
