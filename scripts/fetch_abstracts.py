#!/usr/bin/env python3
"""
Fetch raw abstracts for papers listed in _data/papers.yml and write them to
_data/paper_abstracts.yml. Intended to run in GitHub Actions where outbound
network is available (the Jekyll sandbox locally/on-web is network-blocked).

For each paper with a `fetch_url` field, the script picks a strategy:
  * arXiv URLs        -> arXiv API (XML)
  * doi.org URLs      -> Crossref API (JSON abstract field, when publisher
                        has deposited one). Falls back to metadata only.
  * PDFs              -> download and run `pdftotext` (requires poppler-utils)
  * other HTML pages  -> GET and extract <meta name="description"> / first
                        paragraph text as a best effort

The output is keyed by paper `id` and is safe to re-run. Missing or failed
fetches are written with a `status` of `error` so humans can see what still
needs manual entry.
"""

from __future__ import annotations

import html
import json
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
PAPERS_PATH = REPO_ROOT / "_data" / "papers.yml"
OUT_PATH = REPO_ROOT / "_data" / "paper_abstracts.yml"

UA = "mikeion-homepage-abstract-fetcher/1.0 (+https://mikeion.com)"
TIMEOUT = 30
PDF_MAX_CHARS = 4000
HTML_MAX_CHARS = 3000


def http_get(url: str, accept: str | None = None) -> tuple[int, bytes, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    if accept:
        req.add_header("Accept", accept)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.status, r.read(), r.headers.get("Content-Type", "")


def fetch_arxiv(url: str) -> dict[str, Any]:
    m = re.search(r"arxiv\.org/(?:abs|pdf)/([^?#/]+?)(?:\.pdf)?$", url)
    if not m:
        return {"status": "error", "error": f"could not parse arXiv id from {url}"}
    arxiv_id = m.group(1)
    api = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    _, body, _ = http_get(api, accept="application/atom+xml")
    text = body.decode("utf-8", errors="replace")
    summary = re.search(r"<summary>(.*?)</summary>", text, re.DOTALL)
    title = re.search(r"<entry>.*?<title>(.*?)</title>", text, re.DOTALL)
    if not summary:
        return {"status": "error", "error": "no <summary> in arXiv response"}
    return {
        "status": "ok",
        "source": "arxiv",
        "arxiv_id": arxiv_id,
        "title": html.unescape(title.group(1).strip()) if title else None,
        "abstract": re.sub(r"\s+", " ", html.unescape(summary.group(1))).strip(),
    }


def fetch_crossref(url: str) -> dict[str, Any]:
    m = re.search(r"doi\.org/(.+)$", url)
    if not m:
        return {"status": "error", "error": f"could not parse DOI from {url}"}
    doi = urllib.parse.unquote(m.group(1)).strip("/")
    api = f"https://api.crossref.org/works/{urllib.parse.quote(doi, safe='/')}"
    _, body, _ = http_get(api, accept="application/json")
    data = json.loads(body).get("message", {})
    abstract = data.get("abstract")
    if abstract:
        abstract = re.sub(r"<[^>]+>", " ", abstract)
        abstract = re.sub(r"\s+", " ", html.unescape(abstract)).strip()
    return {
        "status": "ok" if abstract else "partial",
        "source": "crossref",
        "doi": doi,
        "title": (data.get("title") or [None])[0],
        "container": (data.get("container-title") or [None])[0],
        "abstract": abstract,
        "note": None if abstract else "Crossref has no abstract for this DOI.",
    }


def fetch_pdf(url: str) -> dict[str, Any]:
    _, body, ctype = http_get(url)
    if "pdf" not in ctype.lower() and not body.startswith(b"%PDF"):
        return {"status": "error", "error": f"not a PDF (content-type={ctype})"}
    tmp = REPO_ROOT / ".fetch.tmp.pdf"
    tmp.write_bytes(body)
    try:
        out = subprocess.run(
            ["pdftotext", "-layout", "-enc", "UTF-8", str(tmp), "-"],
            check=True,
            capture_output=True,
            text=True,
            timeout=60,
        ).stdout
    except FileNotFoundError:
        return {"status": "error", "error": "pdftotext not installed"}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "error": f"pdftotext failed: {e.stderr[:200]}"}
    finally:
        tmp.unlink(missing_ok=True)
    text = re.sub(r"[ \t]+", " ", out)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return {
        "status": "ok",
        "source": "pdf",
        "text": text[:PDF_MAX_CHARS],
        "truncated": len(text) > PDF_MAX_CHARS,
    }


def fetch_html(url: str) -> dict[str, Any]:
    _, body, ctype = http_get(url, accept="text/html,application/xhtml+xml")
    text = body.decode("utf-8", errors="replace")
    desc = re.search(
        r'<meta[^>]+name=["\'](?:description|citation_abstract)["\'][^>]+content=["\']([^"\']+)',
        text,
        re.IGNORECASE,
    )
    og = re.search(
        r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)',
        text,
        re.IGNORECASE,
    )
    title = re.search(r"<title>(.*?)</title>", text, re.DOTALL | re.IGNORECASE)
    first_p = re.search(r"<p[^>]*>(.*?)</p>", text, re.DOTALL | re.IGNORECASE)
    parts = []
    if desc:
        parts.append(("description", desc.group(1)))
    if og:
        parts.append(("og:description", og.group(1)))
    if first_p:
        parts.append(("first_paragraph", re.sub(r"<[^>]+>", " ", first_p.group(1))))
    parts = [(k, re.sub(r"\s+", " ", html.unescape(v)).strip()) for k, v in parts]
    return {
        "status": "ok" if parts else "partial",
        "source": "html",
        "title": html.unescape(title.group(1)).strip() if title else None,
        "snippets": [{"kind": k, "text": v[:HTML_MAX_CHARS]} for k, v in parts],
    }


def dispatch(url: str) -> dict[str, Any]:
    host = urllib.parse.urlparse(url).hostname or ""
    if "arxiv.org" in host:
        return fetch_arxiv(url)
    if "doi.org" in host:
        return fetch_crossref(url)
    if url.lower().endswith(".pdf"):
        return fetch_pdf(url)
    return fetch_html(url)


def main() -> int:
    papers = yaml.safe_load(PAPERS_PATH.read_text())
    existing = {}
    if OUT_PATH.exists():
        existing = yaml.safe_load(OUT_PATH.read_text()) or {}

    results: dict[str, Any] = dict(existing)
    fetched = skipped = errored = 0

    for group in papers:
        for paper in group["items"]:
            pid = paper["id"]
            url = paper.get("fetch_url")
            if not url:
                continue
            if pid in existing and existing[pid].get("status") == "ok" and not RERUN:
                skipped += 1
                continue
            print(f"  -> {pid}  ({url})", flush=True)
            try:
                r = dispatch(url)
            except Exception as e:  # network, parse, whatever
                r = {"status": "error", "error": f"{type(e).__name__}: {e}"}
            r["fetched_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            r["url"] = url
            results[pid] = r
            if r["status"] == "error":
                errored += 1
            else:
                fetched += 1
            time.sleep(1)  # be polite to arXiv/Crossref

    OUT_PATH.write_text(
        yaml.safe_dump(results, sort_keys=True, allow_unicode=True, width=100)
    )
    print(f"\ndone: fetched={fetched} skipped={skipped} errored={errored}")
    return 0 if errored == 0 else 0  # don't fail CI on single-URL errors


RERUN = "--rerun" in sys.argv

if __name__ == "__main__":
    sys.exit(main())
