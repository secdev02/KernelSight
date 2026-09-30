"""Generate docs/assets/bypasses.json, the machine-readable bypass registry.

Reads the same __ksnav configs the navigator and the aggregate matrix render,
so the export cannot disagree with the pages: it is generated from them, and
check_verdicts.scan() cross-checks the technique set before anything is
written. A consumer can cite a verdict from this file knowing it is the same
one the site renders.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = sorted((ROOT / "docs" / "mitigations").glob("*.md"))
OUT = ROOT / "docs" / "assets" / "bypasses.json"

sys.path.insert(0, str(ROOT / "scripts"))
from check_roster import load_roster  # noqa: E402
from check_verdicts import TECHNIQUE, _field, scan  # noqa: E402

TITLE = re.compile(r"\btitle\s*:\s*(['\"])(?P<title>.*?)\1", re.S)

VALID_LAYERS = {"kernel", "user"}
VALID_BASIS = {"tested", "cited", "inferred"}


def site_url(page):
    """docs/mitigations/vbs-hvci.md becomes mitigations/vbs-hvci/."""
    trimmed = str(page.relative_to(ROOT / "docs"))
    stem = trimmed[:-3] if trimmed.endswith(".md") else trimmed
    return stem + "/"


def collect():
    by_page = {d["page"]: d["id"] for d in load_roster() if d.get("page")}
    defenses = []
    for page in PAGES:
        text = page.read_text(encoding="utf-8")
        if "__ksnav" not in text:
            continue
        rel = str(page.relative_to(ROOT))
        title = TITLE.search(text)
        techniques = []
        for match in TECHNIQUE.finditer(text):
            body = match.group("body")
            techniques.append({
                "name": match.group("name"),
                "cat": _field(body, "cat"),
                "layer": _field(body, "layer"),
                "asOf": _field(body, "asOf"),
                "basis": _field(body, "basis"),
            })
        defenses.append({
            "title": title.group("title") if title else page.stem,
            "page": rel,
            "url": site_url(page),
            "roster_ids": [by_page[rel]] if rel in by_page else [],
            "techniques": techniques,
        })
    return defenses


def check(defenses):
    errors = []
    for defense in defenses:
        where = defense["page"]
        if not defense["techniques"]:
            errors.append(f"{where}: config has no techniques")
        for t in defense["techniques"]:
            spot = f"{where}: {t['name']}"
            for field in ("name", "cat", "layer", "asOf", "basis"):
                if not t[field]:
                    errors.append(f"{spot}: missing {field}")
            if t["layer"] not in VALID_LAYERS:
                errors.append(f"{spot}: bad layer {t['layer']!r}")
            if t["basis"] not in VALID_BASIS:
                errors.append(f"{spot}: bad basis {t['basis']!r}")
    # The export must carry exactly the techniques check_verdicts enforces,
    # or the site and the JSON disagree about what is registered.
    exported = {(d["page"].split("/")[-1], t["name"]) for d in defenses for t in d["techniques"]}
    enforced = {(r["file"], r["name"]) for r in scan()}
    for extra in sorted(exported - enforced):
        errors.append(f"export has a technique the verdict check does not: {extra}")
    for missing in sorted(enforced - exported):
        errors.append(f"verdict check has a technique the export dropped: {missing}")
    return errors


def main():
    defenses = collect()
    errors = check(defenses)
    for error in errors:
        print(f"ERROR {error}", file=sys.stderr)
    if errors:
        return 1
    total = sum(len(d["techniques"]) for d in defenses)
    data = {
        "version": 1,
        "counts": {"defenses": len(defenses), "techniques": total},
        "defenses": defenses,
    }
    OUT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"bypass export: {len(defenses)} defenses, {total} techniques, all verdict fields present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
