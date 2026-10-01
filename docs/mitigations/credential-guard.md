---
tags:
  - user-layer
  - VTL1
description: "The page the rest of the site points at: the secrets live in VTL1, and a VTL0 kernel read/write primitive, however complete, has no path there. The direct read is closed."
---
# Credential Guard

Credential Guard is the page the rest of this section keeps pointing at. The homepage's worked
example ends with it untouched; the [bypass matrix](../bypasses/) draws it above the line a kernel
primitive cannot cross; [Protected Process Light](protected-process.md) uses it as the contrast
that explains itself. The reason is one architectural fact: the secrets live in VTL1, and a VTL0
kernel read/write primitive, however complete, has no path there.

That makes this inventory the most instructive on the site, because it is the only one where the
honest verdict for the headline technique is `closed`.

| | |
|---|---|
| Layer | User. The protected asset is credential material: hashes, keys, tickets. |
| Enforced by | Hypervisor. LSASS secrets are held by an isolated LSA in VTL1. |
| Mechanism | Isolation, not access control. The data is moved out of reach. |
| Introduced | Windows 10 Enterprise 1607, as a VBS feature; enabled by default on Enterprise from 22H2. |

## Isolation versus a stored decision

<div class="ks-figure" markdown>
  <span class="ks-figure-label">FIG_019: Why the primitive has no path</span>
  <svg viewBox="0 0 820 250" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="In VTL0, PPL stores a protection decision in kernel memory, so a kernel write edits the decision. In VTL1, Credential Guard moves the secret across a hypervisor boundary the primitive cannot address.">

    <text class="ks-label" x="30" y="30">PPL, THE OTHER MODEL</text>
    <rect class="ks-box" x="30" y="44" width="360" height="56"/>
    <text class="ks-annotation" x="45" y="66">A decision stored in VTL0 kernel memory.</text>
    <text class="ks-annotation" x="45" y="84">Kernel write edits the decision. Open.</text>

    <text class="ks-label" x="450" y="30">CREDENTIAL GUARD, THIS MODEL</text>
    <rect class="ks-box" x="450" y="44" width="340" height="56" stroke-dasharray="4 3"/>
    <text class="ks-annotation" x="465" y="66">The secret itself lives in VTL1.</text>
    <text class="ks-annotation" x="465" y="84">Kernel write has no address to write. Closed.</text>

    <line class="ks-line" x1="415" y1="30" x2="415" y2="220" stroke-dasharray="5 4"/>
    <text class="ks-annotation" x="425" y="216">hypervisor boundary, the same line the matrix draws</text>

    <text class="ks-annotation" x="30" y="140">The consequence for technique one below: no amount of kernel capability changes the verdict.</text>
    <text class="ks-annotation" x="30" y="158">What changes it is not loading: with VBS off, LSA falls back to running in VTL0, and the</text>
    <text class="ks-annotation" x="30" y="176">page becomes a note about a defense that is not present. The configuration selector below</text>
    <text class="ks-annotation" x="30" y="194">models exactly that, and the first row is why the hardening curve moves.</text>
  </svg>
</div>

## Bypass inventory

<div id="cg-nav"></div>

<script>
(window.__ksnav = window.__ksnav || []).push({
  sel:'#cg-nav',
  title:'Credential Guard',
  sub:'Three techniques. One closed, one open, one that depends on whether VBS is present at all. Read together they say: the bypass is to not fight the isolation.',
  fromPlatform:function(p){
    return {build:String(p.build), vbs:p.hvci};
  },
  controls:[
    {id:'build',label:'Build',type:'select',default:'26100',options:[['19041','Windows 10 2004'],['22621','Windows 11 22H2'],['26100','Windows 11 24H2'],['26200','Windows 11 25H2']]},
    {id:'cg_state',label:'Posture',type:'checks',wide:true,options:[['vbs','VBS active, Credential Guard on',true]]}
  ],
  techniques:(function(){return [
    {name:'Read LSASS secrets directly',cat:'isolation',layer:'user',asOf:'2026-09-30',basis:'inferred',ev:function(s){
      if(!s.vbs) return ['open','VBS is off','Without VBS there is no VTL1: LSASS runs in VTL0, its memory is kernel-reachable, and this page describes a defense that is not present.'];
      return ['closed','No path to the asset','The secrets are held by the isolated LSA in VTL1. A VTL0 kernel read primitive has no address for them, and no flag to flip creates one. This is the closed verdict the matrix exists to show.'];}},
    {name:'Sidestep: relay and prompt attacks',cat:'sidestep',layer:'user',asOf:'2026-09-30',basis:'inferred',ev:function(s){
      return ['open','Never touches the secret','Attacks that never hold the hash need no bypass of its storage: NTLM relay to a willing target, or capturing credentials at the logon prompt before Credential Guard is ever consulted. The isolation holds; the theft happens elsewhere.'];}},
    {name:'Downgrade: suppress VBS on next boot',cat:'downgrade',layer:'user',asOf:'2026-09-30',basis:'inferred',ev:function(s){
      if(!s.vbs) return ['open','VBS is off','The downgrade already happened, whether by hardware that cannot support it, by policy, or by choice. The machine answers every question the VTL0 way.'];
      return ['gated','Admin, reboot, UEFI lock','VBS enrollment can carry a UEFI lock so the setting survives reinstalls. Suppressing it requires admin, a reboot, and visible configuration changes, each of which is its own detection story.'];}}
  ];})()
});
</script>

## Why the inventory looks like this

The open entry is not a weakness of Credential Guard; it is the boundary of what isolation can
mean. A defense that holds secrets can do nothing about an adversary who arranges for the user to
hand over a fresh credential, which is why the realistic posture stacks this page on top of
[LSA Protection](lsa-protection.md) for the VBS-off case, and on MFA and relay hardening for the
sidestep.

The closed entry deserves its confidence check, which is why it carries `basis: inferred` rather
than `cited`: it is reasoned from the architecture, matching every public description of the
feature, but this corpus has no case study that attempted the direct read and failed against it.
If one is ever published, the verdict flips to `cited` or to a new technique, and this page is
where that lands.

## What a defender sees

VBS and Credential Guard status reported per machine, which is the cheapest high-value telemetry
on this page: the third technique lives or dies by whether VBS is actually on across the fleet.
Credential use that succeeds without any corresponding isolated-LSA authentication flow is the
signature of the sidestep, and belongs in identity telemetry rather than endpoint telemetry.
