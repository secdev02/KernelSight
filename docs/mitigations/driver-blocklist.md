---
tags:
  - kernel-layer
  - BYOVD
description: "The vulnerable driver blocklist answers what DSE cannot, and its two structural openings are list lag and the beyond-BYOVD case where the driver ships with Windows."
---
# Vulnerable Driver Blocklist

The vulnerable driver blocklist is the layer that answers what [DSE](dse.md) cannot: among validly
signed drivers, which ones are too dangerous to load. It is a deny-by-identity list, so its bypass
inventory has exactly two shapes, and both are structural rather than cryptographic: a driver the
list has not caught yet, and a driver the list can never list.

That second shape is the important one. The Lazarus Group's pivot, documented in
[Lazarus / FudModule](../notable-exploits/lazarus-fudmodule.md), was to stop bringing drivers at all
and take the primitive from `appid.sys` and `afd.sys`, components Windows ships and cannot remove.
A load-time list cannot answer that, because the answer to "should afd.sys load" is yes on every
machine in the fleet.

| | |
|---|---|
| Layer | Kernel. The protected asset is the set of drivers admitted at load. |
| Enforced by | Kernel. A WDAC policy applied to driver loads. |
| Mechanism | Deny list of signed-vulnerable drivers, distributed through servicing. |
| Introduced | Windows 10 1709 era, expanded repeatedly since; on by default with HVCI. |

## Bypass inventory

<div id="vdbl-nav"></div>

<script>
(window.__ksnav = window.__ksnav || []).push({
  sel:'#vdbl-nav',
  title:'Vulnerable driver blocklist',
  sub:'Three techniques. A list answers names, so everything here is either newer than the list, older than the list, or not the kind of thing a list can hold.',
  fromPlatform:function(p){
    return {build:String(p.build), blocklist_current:true};
  },
  controls:[
    {id:'build',label:'Build',type:'select',default:'26100',options:[['19041','Windows 10 2004'],['22621','Windows 11 22H2'],['26100','Windows 11 24H2'],['26200','Windows 11 25H2']]},
    {id:'vdbl_state',label:'Posture',type:'checks',wide:true,options:[['blocklist_current','blocklist current on this machine',true]]}
  ],
  techniques:(function(){var REF='../../reference/';var CS='../../case-studies/';return [
    {name:'Driver published or weaponized before the list catches it',cat:'list-lag',layer:'kernel',asOf:'2026-09-30',basis:'cited',ev:function(s){
      return ['open','Time works for the attacker','A list is reactive: the vulnerability must be known, triaged, and serviced before the entry lands. The corpus documents the pattern at scale in <a href="'+REF+'loldrivers-analysis/">the LOLDrivers analysis</a>, 1,775 signed drivers deep.'];}},
    {name:'Windows-shipped driver: beyond BYOVD',cat:'unlistable',layer:'kernel',asOf:'2026-09-30',basis:'cited',ev:function(s){
      return ['open','The driver must load anyway','Components like appid.sys and afd.sys ship with Windows and cannot be blocklisted without breaking the machine. See <a href="'+CS+'CVE-2024-21338/">CVE-2024-21338</a> for the technique that made this pivot famous.'];}},
    {name:'Stale list on an unmanaged machine',cat:'list-lag',layer:'kernel',asOf:'2026-09-30',basis:'inferred',ev:function(s){
      if(s.blocklist_current) return ['gated','List is current','With the policy refreshed, the known names in the corpus do not load. This is the gating that makes the first technique a race rather than a free pass.'];
      return ['open','List is stale','Between Microsoft updating the policy and a machine receiving it, every listed driver loads again. The gap is widest on unmanaged consumer hardware.'];}}
  ];})()
});
</script>

## Why the inventory looks like this

Two of the three entries are open on every configuration, which reads badly until you notice what
kind of open they are. The first is a race the list can eventually win. The second is a category
error the list can never win: `afd.sys` is load-bearing for networking. The realistic defense
posture is therefore the blocklist plus [App Control for Business](app-control-for-business.md)
with a allowlist policy, which answers "which signer may load" per fleet rather than globally, and
the detection guidance in the Lazarus profile for the unlistable case.

## What a defender sees

Telemetry for the policy version itself is the health signal: a fleet whose blocklist ages is a
fleet drifting toward the third technique. Loads of listed drivers are the loudest event on this
page, essentially zero-false-positive. For the unlistable case there is no load signal at all, which
is the point: detection moves to anomalous IOCTL traffic, as documented in
[CVE-2024-21338](../case-studies/CVE-2024-21338.md).
