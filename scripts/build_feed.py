"""Generate docs/feed.xml, the site's Atom feed.

Every developer blog worth reading ships a feed; this corpus is a log of
substantive changes, so it gets one too. Entries come from the same
substance-only dates the pages display, which means formatting sweeps
never appear here. Stdlib only: no plugin, no new CI dependency.
"""
import html
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATES = ROOT / "docs" / "assets" / "page-dates.json"
OUT = ROOT / "docs" / "feed.xml"
SITE = "https://splintersfury.github.io/KernelSight/"
TITLE = "KernelSight"


def main():
    if not DATES.exists():
        print("ERROR run scripts/build_page_dates.py first", file=sys.stderr)
        return 1
    data = json.loads(DATES.read_text(encoding="utf-8"))
    entries = data.get("recent", [])

    feed = ET.Element("feed", {"xmlns": "http://www.w3.org/2005/Atom"})
    ET.SubElement(feed, "title").text = TITLE
    ET.SubElement(feed, "link", {"href": SITE})
    ET.SubElement(feed, "link", {"rel": "self", "href": SITE + "feed.xml"})
    ET.SubElement(feed, "id").text = SITE
    ET.SubElement(feed, "updated").text = data.get("newest_page", "1970-01-01") + "T00:00:00Z"
    author = ET.SubElement(feed, "author")
    ET.SubElement(author, "name").text = "Ahmad Abdillah Bin Zaini"

    for entry in entries:
        url = SITE + entry["url"]
        item = ET.SubElement(feed, "entry")
        ET.SubElement(item, "title").text = entry["title"]
        ET.SubElement(item, "link", {"href": url})
        ET.SubElement(item, "id").text = url
        ET.SubElement(item, "updated").text = entry["date"] + "T00:00:00Z"
        ET.SubElement(item, "summary").text = f"{entry['section']}: {entry['title']}"

    ET.indent(feed)
    body = ET.tostring(feed, encoding="unicode")
    OUT.write_text('<?xml version="1.0" encoding="utf-8"?>\n' + body + "\n", encoding="utf-8")
    print(f"feed: {len(entries)} entries, newest {data.get('newest_page')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
