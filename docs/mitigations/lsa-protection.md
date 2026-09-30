---
tags:
  - user-layer
---
# LSA Protection

LSA Protection is [Protected Process Light](protected-process.md) applied to one process that
matters more than any other: the Local Security Authority, where the credential material lives.
Running LSA as a protected process closes the classic user-mode path, `Mimikatz` style in-memory
dumping from an adjacent process, and it is the first thing an attacker notices when that path
returns nothing.

But the framing follows the PPL page exactly, and so does the verdict: the enforcement is a byte
in kernel memory consulted at handle-open time. Against a user-mode adversary it is a wall.
Against a kernel read/write primitive it is a speed bump, because the primitive does not need to
open a handle at all.

| | |
|---|---|
| Layer | User. The protected asset is credential material held in LSASS. |
| Enforced by | Kernel. LSA runs as PPL; the object manager checks handle opens. |
| Mechanism | `RunAsPPL` protection level on the LSA process. |
| Introduced | Windows 8.1 Update (KB2973201), by registry opt-in; hardened since. |

## Bypass inventory

<div id="lsa-nav"></div>

<script>
(window.__ksnav = window.__ksnav || []).push({
  sel:'#lsa-nav',
  title:'LSA Protection',
  sub:'Three techniques, all familiar from the PPL page: the defense stores a decision in kernel memory, and kernel memory is exactly what the attacker holds.',
  fromPlatform:function(p){
    return {build:String(p.build), kwrite:p.prims, blocklist:true};
  },
  controls:[
    {id:'build',label:'Build',type:'select',default:'26100',options:[['19041','Windows 10 2004'],['22621','Windows 11 22H2'],['26100','Windows 11 24H2'],['26200','Windows 11 25H2']]},
    {id:'lsa_held',label:'What you hold',type:'checks',wide:true,options:[['kwrite','kernel write primitive',true],['blocklist','driver blocklist is current',true]]}
  ],
  techniques:(function(){var CS='../../case-studies/';return [
    {name:'Kernel-context read of LSASS memory',cat:'privilege-object',layer:'user',asOf:'2026-09-30',basis:'inferred',ev:function(s){
      if(!s.kwrite) return ['gated','Needs a kernel write primitive','Without kernel access, the protection holds: this is the wall LSA Protection was built to be.'];
      return ['open','Have kernel access','The primitive reads or copies LSASS memory from kernel context, where the object manager is never asked for a handle. Same shape as the PPL downgrade, one step shorter.'];}},
    {name:'Dump via vulnerable signed driver',cat:'privilege-object',layer:'user',asOf:'2026-09-30',basis:'cited',ev:function(s){
      if(s.blocklist) return ['gated','Driver is blocklisted','The PPLdump class of tool: borrow a kernel primitive from a signed driver, then dump LSASS. The drivers it borrows are exactly the corpus, and the good ones are blocklisted. See <a href="'+CS+'Truesight-sys/">Truesight.sys</a> for the pattern.'];
      return ['open','Blocklist stale or disabled','With the list stale, the borrowed driver loads and the dump proceeds.'];}},
    {name:'Abuse a PPL-signed host as a proxy',cat:'privilege-object',layer:'user',asOf:'2026-09-30',basis:'inferred',ev:function(s){
      return ['gated','Needs a specific signed host','Techniques that get code running inside an already-protected, Microsoft-signed process exist and recur, but each depends on a particular binary and closes when that binary is fixed. A moving target, not a standing bypass.'];}}
  ];})()
});
</script>

## Why the inventory looks like this

Everything here is the [PPL](protected-process.md) inventory with one substitution: the protected
process now holds secrets, so the payoff for the same techniques is larger while the difficulty is
unchanged. That is worth saying plainly to defenders: LSA Protection raises the floor against
commodity malware, which is most of the threat, and buys nothing against the kernel-primitive
adversary this site is about. The answer to that adversary is one layer up:
[Credential Guard](credential-guard.md) moves the secrets themselves out of VTL0, which is a
different kind of answer entirely.

## What a defender sees

Failed handle opens against the LSA process from medium-integrity processes, which is commodity
malware hitting the wall and a useful low-severity signal. Kernel-context access to LSASS memory
is the higher-fidelity event, and the driver-load signals from the second technique arrive earlier
still. A fleet relying on LSA Protection alone should treat any VBS-capable machine without
Credential Guard as the gap it is.
