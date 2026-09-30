---
hide:
  - toc
description: "The map: KernelSight answers one question, what a kernel read/write primitive buys an attacker on a given Windows build and CPU, and which defenses still stop them. Two halves, one hinge."
---

<div class="ks-hero-title" markdown>One question</div>

<p class="ks-hero-subtitle">
What does a kernel read or write primitive buy an attacker on a <em>specific</em> Windows build and
CPU, and which defenses still stop them? Every page on this site answers one half of that question
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
| **2026-09-03** | Repositioned around what kernel access buys you. Navigation regrouped into [Getting in](driver-types/index.md) and [What stops them](mitigations/index.md); new [bypass matrix](bypasses/index.md) evaluating every inventory against one platform selection; first user-layer defense page, [Protected Process Light](mitigations/protected-process.md). Every technique now carries a dated verdict and a basis tier. |
| **2026-03-12** | [KDU Provider Compatibility](reference/kdu-compatibility.md) and [LOLDrivers Deep Analysis](reference/loldrivers-analysis.md) updated with full 1,775-driver Tier 2 Ghidra results. 1,404 KDU-compatible (79%), 354 Tier 2 confirmed, 122 confirmed MapDriver candidates with physical + virtual memory primitives reachable from IOCTL handlers. All mitigations, ROP gadgets, and I/O methods scored. |
| **2026-03-01** | Backfill: 13 case studies added for 2022--2024 CVEs with published exploit research. CLFS ransomware chain (CVE-2022-24521, CVE-2022-35803, CVE-2023-23376), Project Zero registry audit (CVE-2022-34707, CVE-2023-23420), DEVCORE kernel streaming (CVE-2024-30090, CVE-2024-30084, CVE-2024-38144), activation context bugs (CVE-2022-22047, CVE-2022-41073). Corpus now at 157 CVEs, 58 exploited ITW. |
| **2026-02-28** | 58 new case studies across afd.sys, clfs.sys, win32k, dwmcore.dll, ntfs.sys, ntoskrnl, plus new deep dives: [afd.sys](case-studies/afd-deep-dive.md), [win32k](case-studies/win32k-deep-dive.md), [ntfs.sys](case-studies/ntfs-deep-dive.md), and new guides: [Corpus Analytics](guides/corpus-analytics.md), [Exploit Chain Patterns](guides/exploit-chain-patterns.md), [Patch Patterns](guides/patch-patterns.md), [Mitigation Timeline](guides/mitigation-timeline.md). |
