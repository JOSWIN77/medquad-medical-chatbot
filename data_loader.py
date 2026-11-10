"""
data_loader.py
Downloads and parses MedQuAD XML files from GitHub.
"""
import os
import requests
import xml.etree.ElementTree as ET
import json
import time

GITHUB_API = "https://api.github.com/repos/abachaa/MedQuAD/contents"
RAW_BASE   = "https://raw.githubusercontent.com/abachaa/MedQuAD/master"
CACHE_FILE = "medquad_cache.json"

# Top folders to fetch (keeping first 5 for speed)
FOLDERS = [
    "1_CancerGov_QA",
    "2_GARD_QA",
    "3_GHR_QA",
    "4_MedlinePlus_QA",
    "5_NIDDK_QA",
]


def _parse_xml(xml_text: str) -> list[dict]:
    """Extract Q&A pairs from a single MedQuAD XML string."""
    pairs = []
    try:
        root = ET.fromstring(xml_text)
        doc_name = root.attrib.get("url", "")
        focus = root.findtext("Focus") or ""
        for qa in root.iter("QAPair"):
            q = qa.findtext("Question") or ""
            a = qa.findtext("Answer") or ""
            qtype = qa.find("Question").attrib.get("qtype", "") if qa.find("Question") is not None else ""
            if q.strip() and a.strip():
                pairs.append({
                    "question": q.strip(),
                    "answer": a.strip(),
                    "focus": focus.strip(),
                    "type": qtype,
                    "source": doc_name,
                })
    except ET.ParseError:
        pass
    return pairs


def _list_xml_files(folder: str, session: requests.Session) -> list[str]:
    """Return list of raw URLs for XML files in a GitHub folder."""
    urls = []
    try:
        r = session.get(f"{GITHUB_API}/{folder}", timeout=15)
        if r.status_code == 200:
            for item in r.json():
                if item["name"].endswith(".xml"):
                    urls.append(f"{RAW_BASE}/{folder}/{item['name']}")
    except Exception:
        pass
    return urls


def download_medquad(max_per_folder: int = 20, status_callback=None) -> list[dict]:
    """Download MedQuAD data, cache locally, return list of Q&A dicts."""
    if os.path.exists(CACHE_FILE):
        if status_callback:
            status_callback("Loading from cache…")
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    all_pairs = []
    session = requests.Session()
    session.headers.update({"Accept": "application/vnd.github+json"})

    for folder in FOLDERS:
        if status_callback:
            status_callback(f"Fetching folder: {folder}")
        file_urls = _list_xml_files(folder, session)
        for url in file_urls[:max_per_folder]:
            try:
                r = session.get(url, timeout=15)
                if r.status_code == 200:
                    all_pairs.extend(_parse_xml(r.text))
                time.sleep(0.05)
            except Exception:
                pass

    # Save cache
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(all_pairs, f, ensure_ascii=False)

    return all_pairs
