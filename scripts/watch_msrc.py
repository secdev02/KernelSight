"""Watch MSRC for new Windows kernel-driver CVEs and emit a triage report.

The corpus stalled once because noticing new CVEs was a manual habit. This
turns Patch Tuesday into a checklist: one report per release, grouped by
priority, with the CVEs the index already covers filtered out. The scheduled
workflow opens it as a single issue per month so triage stays a review task
rather than a research one.

Stdlib plus PyYAML, both already CI dependencies. All network access lives in
fetch functions; everything downstream of them is pure so tests need no
network.
"""
import argparse
import json
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CVE_INDEX = ROOT / "index" / "cve_index.yaml"

UPDATES_URL = "https://api.msrc.microsoft.com/cvrf/v2.0/Updates"
CVRF_URL = "https://api.msrc.microsoft.com/cvrf/v3.0/cvrf/{}"
MSRC_LINK = "https://msrc.microsoft.com/update-guide/vulnerability/{}"

# Titles that name the components the corpus is built around. Anything with
# "Driver" in the title is kept as a second tier: in scope, rarely core.
CORE = re.compile(
    r"Windows Kernel|Win32k|Common Log|CLFS|Ancillary Function Driver|"
    r"Kernel Streaming|NTFS|Fast FAT|Cloud Filter|Bind Filter|Filter Manager|"
    r"Local Procedure Call",
    re.I)

SEVERITY_ORDER = {"Critical": 4, "Important": 3, "Moderate": 2, "Low": 1}


def fetch_json(url):
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read())


def recent_releases(days):
    """Security update releases whose initial release date falls in the window."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    entries = fetch_json(UPDATES_URL)["value"]
    releases = []
    for entry in entries:
        title = entry.get("DocumentTitle", "")
        if "Security Updates" not in title:
            continue
        released = datetime.fromisoformat(entry["InitialReleaseDate"].replace("Z", "+00:00"))
        if released >= cutoff:
            releases.append({
                "id": entry["ID"],
                "title": title,
                "released": released,
            })
    releases.sort(key=lambda r: r["released"])
    return releases


def fetch_vulnerabilities(release_id):
    return fetch_json(CVRF_URL.format(release_id))["Vulnerability"]


def _is_exploited(vuln):
    for threat in vuln.get("Threats", []):
        if threat.get("Type") == 1 and "Exploited:Yes" in str(threat.get("Description", "")):
            return True
    return False


def _max_severity(vuln):
    best = 0
    for threat in vuln.get("Threats", []):
        if threat.get("Type") == 3:
            value = threat.get("Description", "")
            if isinstance(value, dict):
                value = value.get("Value", "")
            best = max(best, SEVERITY_ORDER.get(str(value), 0))
    return best


def kernel_candidates(vulns):
    """Filter a CVRF Vulnerability array down to kernel-driver candidates.

    Returns dicts with cve, title, severity, exploited and tier, sorted worst
    first: exploited before not, Critical before Important, CVE descending.
    """
    out = []
    for vuln in vulns:
        title = (vuln.get("Title") or {}).get("Value") or ""
        if not title or "Windows" not in title:
            continue
        if CORE.search(title):
            tier = "core"
        elif "Driver" in title:
            tier = "drivers"
        else:
            continue
        out.append({
            "cve": vuln["CVE"],
            "title": title,
            "severity": _max_severity(vuln),
            "exploited": _is_exploited(vuln),
            "tier": tier,
        })
    out.sort(key=lambda c: c["cve"], reverse=True)
    out.sort(key=lambda c: (not c["exploited"], -c["severity"]))
    return out


def load_known():
    with CVE_INDEX.open(encoding="utf-8") as fh:
        return {entry["cve_id"] for entry in yaml.safe_load(fh)["cves"]}


def _line(candidate):
    severity = ["", "Low", "Moderate", "Important", "Critical"][candidate["severity"]]
    return (f"- [{'x' if candidate['exploited'] else ' '}] **{candidate['cve']}** "
            f"{severity} · {candidate['title']} · [MSRC]({MSRC_LINK.format(candidate['cve'])})")


def build_report(releases, known):
    """Markdown triage list for the releases, or None when nothing is new.

    Exploited-in-the-wild entries are checked and bolded even though they are
    unchecked work items, so a skimming maintainer cannot miss them.
    """
    sections = {"exploited": [], "core": [], "drivers": []}
    total_seen = 0
    for release in releases:
        for candidate in kernel_candidates(fetch_vulnerabilities(release["id"])):
            total_seen += 1
            if candidate["cve"] in known:
                continue
            if candidate["exploited"]:
                sections["exploited"].append(candidate)
            else:
                sections[candidate["tier"]].append(candidate)

    fresh = sum(len(v) for v in sections.values())
    if fresh == 0:
        return None

    latest = releases[-1]
    month = latest["released"].strftime("%B %Y")
    lines = [
        f"# MSRC {month}: kernel-driver triage",
        "",
        f"From {', '.join(r['title'] for r in releases)}. "
        f"{total_seen} candidates matched the kernel-driver filter, "
        f"{total_seen - fresh} are already in the corpus. "
        "Check an entry off once it is triaged: either a case study, or a reasoned skip.",
        "",
    ]
    headings = [
        ("exploited", "Exploited in the wild"),
        ("core", "Core kernel and filter components"),
        ("drivers", "Other Windows drivers"),
    ]
    for key, heading in headings:
        if not sections[key]:
            continue
        lines.append(f"## {heading} ({len(sections[key])})")
        lines.extend(_line(c) for c in sections[key])
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--days", type=int, default=10,
                        help="releases initially published in this window (default 10)")
    parser.add_argument("--out", type=Path, default=None,
                        help="write the markdown report here when there is anything to triage")
    parser.add_argument("--title-out", type=Path, default=None,
                        help="write the issue title here alongside --out")
    args = parser.parse_args()

    releases = recent_releases(args.days)
    if not releases:
        print(f"no MSRC security releases in the last {args.days} days")
        return 0

    report = build_report(releases, load_known())
    if report is None:
        print(f"{len(releases)} release(s) scanned, nothing new for the corpus")
        return 0

    if args.out:
        args.out.write_text(report + "\n", encoding="utf-8")
    if args.title_out:
        month = releases[-1]["released"].strftime("%B %Y")
        args.title_out.write_text(f"MSRC {month}: kernel-driver triage\n", encoding="utf-8")
    uncovered = report.count("- [")
    print(f"{len(releases)} release(s) scanned, {uncovered} uncovered kernel-driver CVEs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
