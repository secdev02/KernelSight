"""The Atom feed must parse and carry real, dated entries."""
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "feed.xml"
NS = "{http://www.w3.org/2005/Atom}"


def build():
    subprocess.run([sys.executable, "scripts/build_page_dates.py"], cwd=ROOT,
                   check=True, stdout=subprocess.DEVNULL)
    subprocess.run([sys.executable, "scripts/build_feed.py"], cwd=ROOT,
                   check=True, stdout=subprocess.DEVNULL)
    return ET.parse(OUT).getroot()


def test_feed_parses_with_dated_entries():
    root = build()
    entries = root.findall(f"{NS}entry")
    assert len(entries) >= 10
    dates = [e.find(f"{NS}updated").text for e in entries]
    assert dates == sorted(dates, reverse=True)


def test_every_entry_links_absolutely_and_names_itself():
    root = build()
    for entry in root.findall(f"{NS}entry"):
        href = entry.find(f"{NS}link").get("href")
        assert href.startswith("https://splintersfury.github.io/KernelSight/"), href
        assert entry.find(f"{NS}title").text
        assert entry.find(f"{NS}id").text == href


def test_feed_dates_match_the_page_dates_data():
    root = build()
    dates = {e.find(f"{NS}updated").text[:10]
             for e in root.findall(f"{NS}entry")}
    source = json.loads((ROOT / "docs" / "assets" / "page-dates.json").read_text(encoding="utf-8"))
    assert dates.issubset(set(source["pages"].values()))
