"""Inject tags into case-study pages from index/cve_index.yaml.

Tags are what Simon Willison's blog proves out: the cheapest discoverability
a corpus can buy. Driver, vulnerability class and in-the-wild status are
already recorded per CVE in the index, so this script makes the markdown
agree with the data instead of hand-tagging 157 files. Rerunning rewrites
the tags block, so the index stays the single source of truth.
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index" / "cve_index.yaml"
CASE_DIR = ROOT / "docs" / "case-studies"

FM = re.compile(r"^---\n(.*?)\n---\n", re.S)


def tags_for(entry):
    tags = [entry["driver"]]
    if entry.get("vuln_class"):
        tags.append(entry["vuln_class"])
    if entry.get("itw"):
        tags.append("ITW")
    return tags


def write_tags(text, tags):
    """Rewrite frontmatter with exactly one tags block, keeping description.

    The tags block is matched with an optional trailing newline on its last
    line: frontmatter captured from a file ends without one, and a pattern
    that demands it silently fails to remove the old block, duplicating the
    key into invalid YAML on the second run.
    """
    block = "tags:\n" + "".join(f"  - {t}\n" for t in tags)
    match = FM.match(text)
    if match:
        front = match.group(1)
        desc = re.search(r"description: .*(?:\n(?!\w).*)?", front)
        kept = (desc.group(0).rstrip() + "\n\n") if desc else ""
        return f"---\n{kept}{block}---\n" + text[match.end():]
    return f"---\n{block}---\n" + text


def main():
    with INDEX.open(encoding="utf-8") as fh:
        entries = yaml.safe_load(fh)["cves"]
    tagged = missing = 0
    for entry in entries:
        page = entry.get("case_study")
        if not page:
            missing += 1
            continue
        path = ROOT / page
        if not path.exists():
            print(f"ERROR index names a missing page: {page}", file=sys.stderr)
            return 1
        path.write_text(write_tags(path.read_text(encoding="utf-8"), tags_for(entry)),
                        encoding="utf-8")
        tagged += 1
    print(f"tags: {tagged} case studies tagged from the index, {missing} index entries without a page")
    return 0


if __name__ == "__main__":
    sys.exit(main())
