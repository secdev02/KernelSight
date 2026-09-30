"""The MSRC watcher's filtering and report logic, with no network involved."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from watch_msrc import build_report, kernel_candidates, load_known  # noqa: E402


def vuln(cve, title, exploited=False, severity="Important"):
    return {
        "CVE": cve,
        "Title": {"Value": title},
        "Threats": [
            {"Type": 1, "Description": f"Publicly Disclosed:No;Exploited:{'Yes' if exploited else 'No'}"},
            {"Type": 3, "Description": {"Value": severity}},
        ],
    }


def test_kernel_candidates_keeps_core_and_driver_titles_and_drops_the_rest():
    candidates = kernel_candidates([
        vuln("CVE-2026-1", "Windows Kernel Elevation of Privilege Vulnerability"),
        vuln("CVE-2026-2", "Windows USB Driver Elevation of Privilege Vulnerability", severity="Low"),
        vuln("CVE-2026-3", "Microsoft Word Remote Code Execution Vulnerability"),
        vuln("CVE-2026-4", "Windows Ancillary Function Driver for WinSock Elevation of Privilege Vulnerability"),
    ])
    assert [c["cve"] for c in candidates] == ["CVE-2026-4", "CVE-2026-1", "CVE-2026-2"]
    tiers = {c["cve"]: c["tier"] for c in candidates}
    assert tiers["CVE-2026-1"] == "core" and tiers["CVE-2026-2"] == "drivers"


def test_kernel_candidates_sorts_exploited_first_then_severity():
    candidates = kernel_candidates([
        vuln("CVE-2026-A", "Windows Kernel Elevation of Privilege Vulnerability"),
        vuln("CVE-2026-B", "Windows Kernel Elevation of Privilege Vulnerability", severity="Critical"),
        vuln("CVE-2026-C", "Windows NTFS Elevation of Privilege Vulnerability", exploited=True, severity="Moderate"),
    ])
    assert [c["cve"] for c in candidates] == ["CVE-2026-C", "CVE-2026-B", "CVE-2026-A"]


def test_kernel_candidates_flags_exploited():
    candidates = kernel_candidates(
        [vuln("CVE-2026-C", "Windows Kernel Elevation of Privilege Vulnerability", exploited=True)])
    assert candidates[0]["exploited"] is True


def test_known_cves_are_excluded_from_the_report(monkeypatch):
    monkeypatch.setattr("watch_msrc.fetch_vulnerabilities", lambda rid: [
        vuln("CVE-2026-1", "Windows Kernel Elevation of Privilege Vulnerability"),
        vuln("CVE-2026-2", "Windows NTFS Elevation of Privilege Vulnerability", exploited=True),
    ])
    releases = [{"id": "2026-Sep", "title": "September 2026 Security Updates",
                 "released": __import__("datetime").datetime(2026, 9, 8)}]

    report_all_new = build_report(releases, known=set())
    assert report_all_new is not None
    assert "- [x] **CVE-2026-2**" in report_all_new
    assert "- [ ] **CVE-2026-1**" in report_all_new
    assert "## Exploited in the wild (1)" in report_all_new

    report_nothing_new = build_report(releases, known={"CVE-2026-1", "CVE-2026-2"})
    assert report_nothing_new is None


def test_the_real_index_loads_and_stays_populated():
    known = load_known()
    assert len(known) > 150
    # Most entries are CVEs; the rest are CVE-less driver slugs like
    # echo-driver-sys, which never match an MSRC CVE either way.
    cves = {k for k in known if k.startswith("CVE-")}
    assert len(cves) > 140
    assert all(k.startswith("CVE-") or k.endswith("-sys") or not k[:1].isdigit() for k in known)
