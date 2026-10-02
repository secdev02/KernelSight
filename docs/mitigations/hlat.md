---
description: "HLAT: Hypervisor-enforced Lazy Address Translation (Intel VT-rp). The hypervisor owns kernel-mode translation, so editing guest PTEs no longer redirects what the kernel sees. Closes the whole table-hijack family on the hardware that supports it, and deliberately protects nothing else."
tags:
  - kernel-layer
  - VTL1
---

# HLAT

HLAT is the defense this site's homepage curve has been waiting for, and the reason its
platform selector has an HLAT toggle. With it active, the processor translates kernel-mode
addresses through paging structures the hypervisor owns and populates lazily; the guest's
own page tables still exist, but they no longer govern what kernel-mode code sees. Every
technique whose last step is "edit a guest PTE" stops at that step.

What it does not do is equally important, and this page's inventory keeps both halves
honest: HLAT protects *translation*, not data, and its guarantee covers supervisor mode.

| | |
|---|---|
| Layer | Kernel. The protected asset is kernel-mode address translation itself. |
| Enforced by | Hypervisor. Parallel paging structures maintained above the guest. |
| Mechanism | Supervisor-mode walks resolve through hypervisor-populated tables, updated lazily as the guest legitimately maps pages. |
| Introduced | Intel VT-rp hardware, 11th-generation and newer; active with VBS, default on Windows 11 24H2-era builds. |

## One mechanism, closed family, open edges

<div class="ks-figure" markdown>
  <span class="ks-figure-label">FIG_020: What the guest may edit, and what the processor uses</span>
  <svg viewBox="0 0 820 260" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Without HLAT, kernel-mode and user-mode translation both walk guest-owned page tables, so a guest PTE edit redirects the kernel. With HLAT, kernel-mode walks use hypervisor-owned tables, so the same edit changes nothing the kernel sees, while user-mode translation still consults the guest tables.">

    <text class="ks-label" x="30" y="30">WITHOUT HLAT</text>
    <rect class="ks-box" x="30" y="44" width="340" height="60"/>
    <text class="ks-annotation" x="45" y="66">Kernel and user mode both walk guest page tables.</text>
    <text class="ks-annotation" x="45" y="84">Edit a PTE, redirect the kernel. The DOG family lives here.</text>

    <text class="ks-label" x="450" y="30">WITH HLAT</text>
    <rect class="ks-box" x="450" y="44" width="340" height="30"/>
    <text class="ks-annotation" x="465" y="64">Kernel mode: hypervisor-owned tables. PTE edits do nothing.</text>
    <rect class="ks-box" x="450" y="82" width="340" height="30"/>
    <text class="ks-annotation" x="465" y="102">User mode: still guest tables. The open edge.</text>

    <text class="ks-annotation" x="30" y="150">The closed family is large: SSDT, Shadow SSDT, IDT and GDT hijacking via FWA-backed clones,</text>
    <text class="ks-annotation" x="30" y="168">PTE repointing, and page-swapping supervisor data pages all end in the same step, and the</text>
    <text class="ks-annotation" x="30" y="186">same step is the one HLAT removes. The open edges are different in kind: user-mode access</text>
    <text class="ks-annotation" x="30" y="204">through remapped guest PTEs, and data-only attacks that never touch translation at all.</text>
    <text class="ks-annotation" x="30" y="236">See the DOG profile for the family prediction this page's first row now carries.</text>
  </svg>
</div>

## Bypass inventory

<div id="hlat-nav"></div>

<script>
(window.__ksnav = window.__ksnav || []).push({
  sel:'#hlat-nav',
  title:'HLAT',
  sub:'Four techniques. Two closed by the mechanism, two open by design. Set the platform honestly: HLAT means VBS on and 11th-generation Intel or newer.',
  fromPlatform:function(p){
    return {build:String(p.build), hlat:!!(p.hvci && p.hlat)};
  },
  controls:[
    {id:'build',label:'Build',type:'select',default:'26100',options:[['19041','Windows 10 2004'],['22621','Windows 11 22H2'],['26100','Windows 11 24H2'],['26200','Windows 11 25H2']]},
    {id:'hlat_state',label:'Platform',type:'checks',wide:true,options:[['hlat','HLAT active (VBS on, 11th-gen Intel or newer)',true]]}
  ],
  techniques:(function(){var PR='../../primitives/',NE='../../notable-exploits/';return [
    {name:'Kernel table hijack via FWA clone (SSDT, IDT, GDT)',cat:'table-hijack',layer:'kernel',asOf:'2026-10-03',basis:'inferred',ev:function(s){
      if(!s.hlat) return ['open','No HLAT','The clone-and-repoint mechanism works: the processor follows the repointed guest PTE in kernel mode. See <a href="'+NE+'juan-sacco-dog/">the DOG profile</a> for the family this row carries.'];
      return ['closed','Kernel walks are hypervisor-owned','Repointing a guest PTE does not change what the processor uses for supervisor-mode translation, so the modified clone is never seen. One hardware feature, four techniques, one cause: recorded as inferred until someone publishes the test.'];}},
    {name:'Page swap against supervisor data pages',cat:'page-swap',layer:'kernel',asOf:'2026-10-03',basis:'cited',ev:function(s){
      if(!s.hlat) return ['open','VBS alone is not enough','Swapping the physical page behind a protected variable defeated the KDP-era setup; the technique is documented against g_CiOptions in Fortinet\'s DSE tampering analysis.'];
      return ['closed','Supervisor translation is hypervisor-owned','The swap works by changing what a supervisor-mode access resolves to, which is exactly the resolution HLAT removes.'];}},
    {name:'User-mode access through a remapped guest PTE',cat:'pte-remap',layer:'kernel',asOf:'2026-10-03',basis:'inferred',ev:function(s){
      return ['open','HLAT governs supervisor mode','User-mode translation still consults the guest page tables, so a <a href="'+PR+'arw/pte-manipulation/">remapped user PTE</a> read from ring 3 resolves as the attacker arranged. HLAT\'s contract does not cover this edge; recorded as inferred until tested in public.'];}},
    {name:'Data-only attacks that never touch translation',cat:'data-only',layer:'kernel',asOf:'2026-10-03',basis:'cited',ev:function(s){
      return ['open','Out of scope by design','Token swapping, callback stripping, protection-byte edits: none of them edit a PTE, so none of them meet HLAT. The <a href="'+NE+'lazarus-fudmodule/">FudModule</a> operating model walks past this page entirely.'];}}
  ];})()
});
</script>

## Why the inventory looks like this

HLAT is a single-purpose defense, and the inventory is wide at the top and open at the
bottom for the same reason: it removes exactly one step, the supervisor-mode PTE
redirection, and everything that ends in that step falls with it, while everything that
never needed the step was never in scope. That shape is the site's whole thesis in one
page: same Windows version, same HVCI checkbox, different silicon, materially different
answers.

The practical reading for a defender: on a fleet of 11th-generation-and-newer Intel
machines with VBS, the [FWA](../primitives/exploitation/fwa.md)-and-clone family and the
page-swap class are closed pending a public falsification, and the remaining kernel
threat is the data-only one, which no translation control addresses. On mixed or older
fleets, both classes are live, which is the gap the [bypass matrix](../bypasses/)
expresses per build and per CPU.

## What a defender sees

VBS and HLAT status per machine, reported alongside HVCI, is the health signal; the
hardware floor means fleet age, not policy, decides coverage. A PTE edit attempt
succeeding in user mode while kernel-mode redirection fails is the signature of HLAT
doing its job while its documented edge stays open, and belongs in the same telemetry
stream as the [data-only](vbs-hvci.md) detections.

## Sources

Intel VT-rp and Microsoft's hypervisor documentation for the mechanism; Fortinet
(FortiGuard Labs), "The Swan Song for Driver Signature Enforcement Tampering", and
CryptoPlague, "The dusk of g_CiOptions", for the page-swap class; the Exploit Pack DOG
series for the table-hijack family this page's first row predicts closed.
