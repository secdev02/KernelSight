---
hide:
  - toc
description: "The map: KernelSight answers one question, what a kernel read/write primitive buys an attacker on a given Windows build and CPU, and which defenses still stop them. Two halves, one hinge."
---

<div class="ks-hero-title" markdown>One question</div>

<p class="ks-hero-subtitle">
When an attacker holds a kernel read or write primitive on a <em>specific</em> Windows build and
CPU, which defenses still hold? Every page on this site answers one half of that question
or the other. The halves are called <strong>Getting in</strong> and <strong>What stops them</strong>,
and the hinge between them is the primitive itself.
</p>

<div class="ks-figure" markdown>
  <span class="ks-figure-label">FIG_001: The two halves, and the hinge</span>
  <svg viewBox="0 0 900 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Means feeds a kernel read, write or execute primitive, which then feeds Targets. Means covers driver types, attack surfaces, vulnerability classes and case studies. Targets covers kernel-layer and user-layer defenses.">

    <!-- MEANS -->
    <text class="ks-label" x="30" y="34">GETTING IN &#183; HOW THE ACCESS IS OBTAINED</text>
    <rect class="ks-box" x="30" y="48" width="300" height="34"/>
    <text class="ks-annotation" x="45" y="69">Driver types &#183; 12 families</text>
    <rect class="ks-box" x="30" y="92" width="300" height="34"/>
    <text class="ks-annotation" x="45" y="113">Attack surfaces &#183; 9 entry points</text>
    <rect class="ks-box" x="30" y="136" width="300" height="34"/>
    <text class="ks-annotation" x="45" y="157">Vulnerability classes &#183; 10</text>
    <rect class="ks-box" x="30" y="180" width="300" height="34"/>
    <text class="ks-annotation" x="45" y="201">Case studies &#183; 157 CVEs, 64 drivers</text>

    <!-- feed into the hinge -->
    <path class="ks-arrow" d="M330 65 C 372 65 372 150 400 150"/>
    <path class="ks-arrow" d="M330 109 C 372 109 372 150 400 150"/>
    <path class="ks-arrow" d="M330 153 L400 150"/>
    <path class="ks-arrow" d="M330 197 C 372 197 372 150 400 150"/>
    <path class="ks-arrow" d="M394 145 L404 150 L394 155 Z" fill="currentColor"/>

    <!-- the hinge -->
    <rect class="ks-box" x="404" y="118" width="122" height="64" stroke-width="2"/>
    <text class="ks-label" x="465" y="142" text-anchor="middle">KERNEL</text>
    <text class="ks-label" x="465" y="156" text-anchor="middle">READ / WRITE</text>
    <text class="ks-annotation" x="465" y="172" text-anchor="middle">21 primitives</text>

    <!-- hinge feeds targets -->
    <path class="ks-arrow" d="M526 150 L566 150"/>
    <path class="ks-arrow" d="M560 145 L570 150 L560 155 Z" fill="currentColor"/>

    <!-- TARGETS -->
    <text class="ks-label" x="570" y="34">WHAT STOPS THEM &#183; WHAT IT DEFEATS</text>
    <rect class="ks-box" x="570" y="92" width="300" height="52"/>
    <text class="ks-annotation" x="585" y="112">Kernel layer &#183; 19 defenses</text>
    <text class="ks-annotation" x="585" y="130">DSE, HVCI, kCET, KDP, HLAT, KASLR</text>
    <rect class="ks-box" x="570" y="156" width="300" height="52"/>
    <text class="ks-annotation" x="585" y="176">User layer &#183; 11 defenses</text>
    <text class="ks-annotation" x="585" y="194">PPL, LSA, ETW-Ti, EDR, WDAC, SAC, UAC</text>

    <!-- out of reach -->
    <rect class="ks-box" x="570" y="230" width="300" height="34" stroke-dasharray="4 3"/>
    <text class="ks-annotation" x="585" y="251">VTL1 &#183; Credential Guard, HyperGuard: out of reach</text>
    <line class="ks-line" x1="465" y1="182" x2="465" y2="247" stroke-dasharray="3 3"/>
    <line class="ks-line" x1="465" y1="247" x2="564" y2="247" stroke-dasharray="3 3"/>
    <text class="ks-annotation" x="470" y="240">no path</text>
  </svg>
</div>


## One real example, start to finish

<div style="background:#1c2026;border:1px solid rgba(69,70,76,0.3);border-radius:1rem;padding:2rem 2.25rem 1.75rem">

    <h2 style="font-family:'Space Grotesk';font-size:1.3rem;font-weight:700;color:#e0e2eb;margin:0 0 0.5rem 0;letter-spacing:-0.01em">One real example, start to finish</h2>
    <p style="font-family:'Inter';font-size:0.86rem;color:#9ca3af;margin:0 0 2rem 0;line-height:1.7">
      In 2024 the Lazarus Group did not bring a vulnerable driver with them. They used one that
      was already on every Windows machine: the kernel driver behind AppLocker, a security
      feature.
    </p>

    <div class="wx-chain" style="display:grid;grid-template-columns:150px 1fr;gap:0 1.5rem;align-items:start">

      <div class="wx-step" style="font-family:'JetBrains Mono';font-size:0.62rem;color:#6b7280;text-transform:uppercase;letter-spacing:0.1em;padding-top:0.15rem">The bug</div>
      <div style="padding-bottom:1.5rem;border-left:1px solid rgba(69,70,76,0.4);padding-left:1.5rem;margin-left:-1.5rem;position:relative">
        <span style="position:absolute;left:-4.5px;top:6px;width:8px;height:8px;border-radius:50%;background:#adc6ff"></span>
        <div style="font-family:'Inter';font-size:0.88rem;color:#e0e2eb;margin-bottom:0.3rem">One control code had no permission check</div>
        <div style="font-family:'Inter';font-size:0.8rem;color:#9ca3af;line-height:1.65">Any process could open the device and send it. The handler then trusted a pointer the caller supplied, without checking it pointed anywhere sane.</div>
      </div>

      <div class="wx-step" style="font-family:'JetBrains Mono';font-size:0.62rem;color:#6b7280;text-transform:uppercase;letter-spacing:0.1em;padding-top:0.15rem">What it gave</div>
      <div style="padding-bottom:1.5rem;border-left:1px solid rgba(69,70,76,0.4);padding-left:1.5rem;margin-left:-1.5rem;position:relative">
        <span style="position:absolute;left:-4.5px;top:6px;width:8px;height:8px;border-radius:50%;background:#adc6ff"></span>
        <div style="font-family:'Inter';font-size:0.88rem;color:#e0e2eb;margin-bottom:0.3rem">Read and write anywhere in kernel memory</div>
        <div style="font-family:'Inter';font-size:0.8rem;color:#9ca3af;line-height:1.65">No race to win, no memory to groom, no address to leak first. Send the request, choose the address.</div>
      </div>

      <div class="wx-step" style="font-family:'JetBrains Mono';font-size:0.62rem;color:#3fb950;text-transform:uppercase;letter-spacing:0.1em;padding-top:0.15rem">What that beat</div>
      <div style="padding-bottom:1.5rem;border-left:1px solid rgba(69,70,76,0.4);padding-left:1.5rem;margin-left:-1.5rem;position:relative">
        <span style="position:absolute;left:-4.5px;top:6px;width:8px;height:8px;border-radius:50%;background:#3fb950"></span>
        <div style="font-family:'Inter';font-size:0.88rem;color:#e0e2eb;margin-bottom:0.3rem">The antivirus, the credential store, the audit trail</div>
        <div style="font-family:'Inter';font-size:0.8rem;color:#9ca3af;line-height:1.65">Each of those is guarded by a decision recorded in kernel memory. Once you can edit that memory, you are editing the decision itself rather than defeating it.</div>
      </div>

      <div class="wx-step" style="font-family:'JetBrains Mono';font-size:0.62rem;color:#d29922;text-transform:uppercase;letter-spacing:0.1em;padding-top:0.15rem">What it did not</div>
      <div style="border-left:1px solid transparent;padding-left:1.5rem;margin-left:-1.5rem;position:relative">
        <span style="position:absolute;left:-4.5px;top:6px;width:8px;height:8px;border-radius:50%;background:#d29922"></span>
        <div style="font-family:'Inter';font-size:0.88rem;color:#e0e2eb;margin-bottom:0.3rem">Credential Guard, on the same machine, untouched</div>
        <div style="font-family:'Inter';font-size:0.8rem;color:#9ca3af;line-height:1.65">Windows keeps those secrets somewhere the kernel itself cannot reach. Total control of the kernel buys nothing there.</div>
      </div>

    </div>

    <p style="font-family:'Inter';font-size:0.84rem;color:#8b919b;margin:1.9rem 0 0;padding-top:1.2rem;border-top:1px solid rgba(69,70,76,0.28);line-height:1.7">
      Bug, then capability, then what the capability is worth. That shape repeats across
      <a href="../case-studies/" style="color:#adc6ff;text-decoration:none;border-bottom:1px solid rgba(173,198,255,0.3)">157 real cases</a>,
      and learning to read it is what the <a href="../start-here/" style="color:#adc6ff;text-decoration:none;border-bottom:1px solid rgba(173,198,255,0.3)">path</a> teaches.
      Read this one in full: <a href="../case-studies/CVE-2024-21338/" style="color:#adc6ff;text-decoration:none;border-bottom:1px solid rgba(173,198,255,0.3)">CVE-2024-21338</a>.
    </p>
  </div>

## Getting in: the means

How a standard-user foothold becomes a kernel read/write primitive. Read in order, each stage
narrows from landscape to capability.

<ol class="ks-pipeline-list" markdown>
<li markdown>
<strong><a href="driver-types/">Driver Types</a></strong>
<p>Identify the kernel component, whether file system, network stack, Win32k, core kernel, vendor utility or GPU, then understand its role, IRP patterns and historical vulnerability profile. 12 categories covering 64 unique drivers.</p>
</li>
<li markdown>
<strong><a href="attack-surfaces/">Attack Surfaces</a></strong>
<p>Map how user-mode code reaches the driver: IOCTL handlers, filesystem IRPs, ALPC, shared memory. This determines what an attacker can control.</p>
</li>
<li markdown>
<strong><a href="vuln-classes/">Vulnerability Classes</a></strong>
<p>Classify the bug as buffer overflow, type confusion, TOCTOU or use-after-free, then understand the corruption it enables. 10 classes with typical primitives gained.</p>
</li>
<li markdown>
<strong><a href="primitives/">Primitives</a></strong>
<p>Convert the bug into a capability: arbitrary read/write, pool spray, token swap. 21 technique pages split between arb R/W primitives and exploitation building blocks.</p>
</li>
<li markdown>
<strong><a href="case-studies/">Case Studies</a></strong>
<p>Walk the full chain for 157 real CVEs: root cause, exploitation path, patch analysis, detection rules. 58 exploited in the wild. The <a href="notable-exploits/">Notable Exploits</a> profiles regroup these by developer and chain rather than by bug.</p>
</li>
</ol>

## What stops them: the targets

The other half starts where the primitive exists. For every defense on the [roster](mitigations/),
a maintained inventory of what a kernel primitive does and does not defeat against it.

<ol class="ks-pipeline-list" markdown>
<li markdown>
<strong><a href="mitigations/">The defense roster</a></strong>
<p>30 defenses, split by the layer of the asset protected: 19 kernel layer, 11 user layer. 17 have a reviewed bypass inventory today; the rest are tracked as planned, so coverage is a number that moves rather than a claim.</p>
</li>
<li markdown>
<strong><a href="bypasses/">The bypass matrix</a></strong>
<p>Every registered inventory re-evaluated against one platform selector: same Windows version, same HVCI checkbox, different silicon, different answers. Each verdict carries <code>layer</code>, <code>asOf</code> and a basis tier: tested, cited, or inferred.</p>
</li>
</ol>


## What still works, as the platform hardens

<div style="background:#1c2026;border:1px solid rgba(69,70,76,0.28);border-radius:1rem;padding:1.6rem 1.75rem 1.4rem">
    <div style="display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:0.5rem">
      <div style="font-family:'Space Grotesk';font-size:1rem;font-weight:700;color:#e0e2eb">What still works, as the platform hardens</div>
      <div id="curve-total" style="font-family:'JetBrains Mono';font-size:0.65rem;color:#6b7280"></div>
    </div>
    <div id="curve-rows" style="display:flex;flex-direction:column;gap:0.9rem;margin-top:1.3rem"></div>
    <p id="curve-note" style="font-family:'Inter';font-size:0.75rem;color:#8b919b;line-height:1.6;margin:1.1rem 0 0;padding-top:0.95rem;border-top:1px solid rgba(69,70,76,0.25)"></p>
  </div>
  <div id="coverage-line" style="display:flex;flex-wrap:wrap;gap:2rem;align-items:baseline;margin-top:1rem;padding:1rem 1.25rem;background:#1c2026;border:1px solid rgba(69,70,76,0.22);border-radius:0.625rem"></div>


<script>
(function () {
  var rows = document.getElementById('curve-rows');
  if (!rows) return;
  fetch('../assets/hero-curve.json').then(function (r) { return r.json(); }).then(function (d) {
    var total = d.techniques;
    document.getElementById('curve-total').textContent = total + ' techniques, re-evaluated per configuration';
    var flat = d.configs.filter(function (c, i, a) { return i > 0 && c.open === a[i - 1].open; }).length;
    rows.innerHTML = d.configs.map(function (c) {
      function w(n) { return (n / total * 100).toFixed(1) + '%'; }
      return '<div>'
        + '<div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:0.35rem">'
        + '<span style="font-family:\'JetBrains Mono\';font-size:0.68rem;color:#c3c8d2">' + c.label + '</span>'
        + '<span style="font-family:\'Space Grotesk\';font-size:0.9rem;font-weight:700;color:#3fb950">' + c.open + ' open</span>'
        + '</div>'
        + '<div style="display:flex;overflow:hidden;border-radius:3px;height:22px">'
        + '<div style="width:' + w(c.open) + ';background:#3fb950" title="open: ' + c.open + '"></div>'
        + '<div style="width:' + w(c.gated) + ';background:#d29922" title="gated: ' + c.gated + '"></div>'
        + '<div style="width:' + w(c.closed) + ';background:#3a4150" title="closed: ' + c.closed + '"></div>'
        + '</div></div>';
    }).join('');
    document.getElementById('curve-note').textContent = flat
      ? 'The flat tail is a gap in this reference, not in Windows: no inventory here models HLAT yet. Closing that is the next increment.'
      : 'Same Windows version, different silicon, different answers.';
    var r = d.roster;
    document.getElementById('coverage-line').innerHTML = [
      [r.total, 'defenses in the roster'],
      [r.with_inventory, 'have a reviewed inventory'],
      [total, 'techniques carry a dated verdict']
    ].map(function (p) {
      return '<div><span style="font-family:\'Space Grotesk\';font-size:1.3rem;font-weight:700;color:#e0e2eb">' + p[0]
           + '</span> <span style="font-family:\'Inter\';font-size:0.8rem;color:#9ca3af\'">' + p[1] + '</span></div>';
    }).join('');
  }).catch(function () {
    rows.innerHTML = '<div style="font-family:\'Inter\';font-size:0.8rem;color:#9ca3af">Curve unavailable.</div>';
  });
})();
</script>

<!-- Footer -->
<footer style="border-top:1px solid rgba(69,70,76,0.15);padding:3rem 1.5rem;background:#10131a;margin-top:3rem">
  <div style="max-width:1440px;margin:0 auto;display:flex;justify-content:space-between;align-items:center">
    <div>
      <span style="font-family:'Space Grotesk';font-weight:700;color:#adc6ff;font-size:1.25rem;display:block;margin-bottom:0.5rem">KernelSight</span>
      <span style="font-family:'JetBrains Mono';font-size:0.65rem;text-transform:uppercase;letter-spacing:0.1em;color:#9ca3af">&copy; 2026 KernelSight</span>
    </div>
    <div style="display:flex;gap:2rem">
      <a href="https://github.com/splintersfury/KernelSight" style="font-family:'JetBrains Mono';font-size:0.65rem;text-transform:uppercase;letter-spacing:0.1em;color:#9ca3af;text-decoration:none">GitHub</a>
      <a href="{{ config.site_url }}about/" style="font-family:'JetBrains Mono';font-size:0.65rem;text-transform:uppercase;letter-spacing:0.1em;color:#9ca3af;text-decoration:none">About</a>
    </div>
  </div>
</footer>
{% end
</script>

## How to read the two page types

**A case study** runs bug, then capability, then what the capability is worth: the root cause with
build numbers, the primitive it converts into, the defenses it walked past, the patch, and
detection. Start with [CVE-2024-21338](case-studies/CVE-2024-21338.md), the cleanest example in the
corpus.

**A bypass verdict** is never a bare yes or no. It is dated, it names its basis, and it is tied to
a build and a CPU feature set. An `inferred` verdict is a research lead, not a finding. The whole
inventory is also published as machine-readable data,
[JSON](assets/bypasses.json) regenerated on every deploy.

<hr class="ks-divider--dots">

## The corpus

<div class="ks-stats-box" markdown>
<span class="ks-stat-num">157</span> CVE case studies &nbsp;&middot;&nbsp;
<span class="ks-stat-num">64</span> unique drivers &nbsp;&middot;&nbsp;
<span class="ks-stat-num">58</span> exploited in the wild &nbsp;&middot;&nbsp;
<span class="ks-stat-num">2</span> remotely exploitable<br>
<span class="ks-stat-num">12</span> driver type categories &nbsp;&middot;&nbsp;
<span class="ks-stat-num">21</span> technique pages &nbsp;&middot;&nbsp;
<span class="ks-stat-num">30</span> defenses on the roster &nbsp;&middot;&nbsp;
<span class="ks-stat-num">49</span> dated bypass verdicts<br>
<span class="ks-stat-num">1,775</span> LOLDrivers analyzed &nbsp;&middot;&nbsp;
<span class="ks-stat-num">354</span> Tier 2 Ghidra confirmed &nbsp;&middot;&nbsp;
<span class="ks-stat-num">80+</span> AutoPiff detection rules
</div>

## Where to go next

<div class="ks-paths" markdown>

<a class="ks-path-card" href="start-here/">
  <strong>New here</strong>
  <span>The 7-stage reading path. Each stage ends with a check question, so you can tell whether to move on or reread.</span>
</a>

<a class="ks-path-card" href="../">
  <strong>Explore the corpus</strong>
  <span>Interactive dashboard. Search, filter and visualize all 157 CVEs. The heat matrix shows where the bugs cluster.</span>
</a>

<a class="ks-path-card" href="case-studies/">
  <strong>Researching a specific driver</strong>
  <span>Case studies grouped by driver family, from CLFS through afd.sys to the BYOVD catalogue.</span>
</a>

<a class="ks-path-card" href="bypasses/">
  <strong>Defending endpoints</strong>
  <span>The bypass matrix answers which controls still bite, per build and per CPU, once an attacker holds a primitive.</span>
</a>

<a class="ks-path-card" href="guides/secure-driver-anatomy/">
  <strong>Writing or auditing a driver</strong>
  <span>The 6 anti-patterns behind most kernel driver CVEs, with fixes, a checklist, and real CVE citations.</span>
</a>

</div>

## Reference

[Tooling](tooling/) for the workflow (static analysis, fuzzing, debugging, patch diffing, AutoPiff),
the [driver library](reference/) for BYOVD, LOLDrivers deep analysis and KDU compatibility, and
[guides](guides/) for cross-cutting synthesis.

## Recent Updates

| Date | What's New |
|------|------------|
| **2026-09-30** | Site-wide redesign around the one-question model: a spine bar on every page names which half you are in, the palette toggle is back, and color in the UI now means status rather than section. Notable Exploits section ships Nightmare-Eclipse and Lazarus/FudModule profiles. The bypass registry is published as machine-readable JSON. |
| **2026-09-04** | Every page now shows when it last changed, measured from git rather than asserted. Corpus totals are generated from the data and guarded by a test, after three different figures were live at once. |
| **2026-09-03** | Repositioned around the one-question thesis. Navigation regrouped into [Getting in](driver-types/index.md) and [What stops them](mitigations/index.md); new [bypass matrix](bypasses/index.md) evaluating every inventory against one platform selection; first user-layer defense page, [Protected Process Light](mitigations/protected-process.md). Every technique now carries a dated verdict and a basis tier. |
| **2026-03-12** | [KDU Provider Compatibility](reference/kdu-compatibility.md) and [LOLDrivers Deep Analysis](reference/loldrivers-analysis.md) updated with full 1,775-driver Tier 2 Ghidra results. 1,404 KDU-compatible (79%), 354 Tier 2 confirmed, 122 confirmed MapDriver candidates with physical + virtual memory primitives reachable from IOCTL handlers. All mitigations, ROP gadgets, and I/O methods scored. |
| **2026-03-01** | Backfill: 13 case studies added for 2022--2024 CVEs with published exploit research. CLFS ransomware chain (CVE-2022-24521, CVE-2022-35803, CVE-2023-23376), Project Zero registry audit (CVE-2022-34707, CVE-2023-23420), DEVCORE kernel streaming (CVE-2024-30090, CVE-2024-30084, CVE-2024-38144), activation context bugs (CVE-2022-22047, CVE-2022-41073). Corpus now at 157 CVEs, 58 exploited ITW. |
| **2026-02-28** | 58 new case studies across afd.sys, clfs.sys, win32k, dwmcore.dll, ntfs.sys, ntoskrnl, plus new deep dives: [afd.sys](case-studies/afd-deep-dive.md), [win32k](case-studies/win32k-deep-dive.md), [ntfs.sys](case-studies/ntfs-deep-dive.md), and new guides: [Corpus Analytics](guides/corpus-analytics.md), [Exploit Chain Patterns](guides/exploit-chain-patterns.md), [Patch Patterns](guides/patch-patterns.md), [Mitigation Timeline](guides/mitigation-timeline.md). |
