# Driver Signature Enforcement

Driver Signature Enforcement decides which drivers may load. Its bypass inventory is the shortest
sentence on this site: every BYOVD driver in the corpus passed it. DSE verifies the signer, not the
behavior, so a validly signed driver with a validly signed vulnerability loads without objection.
The defense that answers that is the [vulnerable driver blocklist](driver-blocklist.md), one layer
up, and the two pages explain each other.

That is the framing to hold while reading the inventory below: DSE is a boundary against
*unsigned* code, and every technique here is signed.

| | |
|---|---|
| Layer | Kernel. The protected asset is kernel code integrity at load time. |
| Enforced by | Kernel. `ci.dll` validates the signature chain at driver load. |
| Mechanism | Signature chain check at load; policy flags in code integrity state. |
| Introduced | Windows Vista x64, extended through attestation and WHQL eras. |

## What the check actually asks

<div class="ks-figure" markdown>
  <span class="ks-figure-label">FIG_018: What DSE asks, and what it never asks</span>
  <svg viewBox="0 0 820 260" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="DSE asks whether the image is signed by a chain to a trusted root. It never asks whether the signed driver is dangerous. Forty-one BYOVD drivers in this corpus satisfy the first question and fail only the second.">

    <text class="ks-label" x="30" y="30">THE QUESTION DSE ANSWERS</text>
    <rect class="ks-box" x="30" y="44" width="340" height="72"/>
    <text class="ks-annotation" x="45" y="70">Is this image signed, and does the chain</text>
    <text class="ks-annotation" x="45" y="88">resolve to a kernel-mode trusted root?</text>
    <text class="ks-annotation" x="45" y="106">Yes for all 41 BYOVD drivers in the corpus.</text>

    <text class="ks-label" x="450" y="30">THE QUESTION IT NEVER ASKS</text>
    <rect class="ks-box" x="450" y="44" width="340" height="72" stroke-dasharray="4 3"/>
    <text class="ks-annotation" x="465" y="70">Does this driver expose physical memory,</text>
    <text class="ks-annotation" x="465" y="88">arbitrary kernel R/W, or MSR access to</text>
    <text class="ks-annotation" x="465" y="106">whatever process asks?</text>

    <path class="ks-arrow" d="M200 116 C 200 160 620 160 620 116"/>
    <text class="ks-annotation" x="410" y="166" text-anchor="middle">the gap between the two is the whole BYOVD corpus</text>

    <text class="ks-annotation" x="30" y="212">See the BYOVD reference for the mechanics, and the LOLDrivers deep analysis</text>
    <text class="ks-annotation" x="30" y="228">for what signed-but-dangerous looks like at scale: 1,775 drivers, scored.</text>
  </svg>
</div>

## Bypass inventory

<div id="dse-nav"></div>

<script>
(window.__ksnav = window.__ksnav || []).push({
  sel:'#dse-nav',
  title:'Driver Signature Enforcement',
  sub:'Three techniques. None of them defeats a cryptographic check; two route around it and one switches it off after the fact.',
  fromPlatform:function(p){
    return {build:String(p.build), kwrite:p.prims, hvci:p.hvci};
  },
  controls:[
    {id:'build',label:'Build',type:'select',default:'26100',options:[['19041','Windows 10 2004'],['22621','Windows 11 22H2'],['26100','Windows 11 24H2'],['26200','Windows 11 25H2']]},
    {id:'dse_held',label:'What you hold',type:'checks',wide:true,options:[['kwrite','kernel write primitive',true],['hvci','HVCI / VBS active',true]]}
  ],
  techniques:(function(){var REF='../../reference/';var CS='../../case-studies/';return [
    {name:'BYOVD: load a signed vulnerable driver',cat:'signed-driver-abuse',layer:'kernel',asOf:'2026-09-30',basis:'cited',ev:function(s){
      return ['open','A valid signature','The check passes because the signature is genuine; the vulnerability is not part of the question. This is the defining pattern of the corpus: start at <a href="'+REF+'byovd/">the BYOVD reference</a>, then read <a href="'+CS+'Capcom-sys/">Capcom.sys</a> for the cleanest single example. The answer at this layer is the <a href="../driver-blocklist/">blocklist</a>, not DSE.'];}},
    {name:'Flip code-integrity flags at runtime',cat:'policy-edit',layer:'kernel',asOf:'2026-09-30',basis:'inferred',ev:function(s){
      if(!s.kwrite) return ['gated','Needs a kernel write primitive','The flags are kernel-resident state, so reaching them requires the primitive first.'];
      if(s.hvci) return ['gated','HVCI validates independently','With HVCI active, load-time validation runs on a path the flag flip does not govern, so clearing the in-kernel flag does not restore unsigned loading.'];
      return ['open','Have kernel write, HVCI off','The enforcement state is ordinary kernel data. Clear it and subsequent loads skip the check the flag drove.'];}},
    {name:'Enable test-signing boot configuration',cat:'config-abuse',layer:'kernel',asOf:'2026-09-30',basis:'inferred',ev:function(s){
      return ['gated','Admin, reboot, and a loud artifact','A BCD edit requires an admin token and a reboot, and the desktop watermark plus boot-entry telemetry are high-fidelity signals. A real technique, but a noisy one.'];}}
  ];})()
});
</script>

## Why the inventory looks like this

The first technique is open on every configuration, and that is the honest answer: DSE was never
the layer that stops signed drivers, because stopping signed drivers is a policy question, and
policy about *which* signer is a different defense. The second technique is where the platform's
hardening curve shows: the same kernel write buys less on an HVCI machine, because the
hypervisor-backed validation does not consult the flag the primitive flipped.

For a defender, the actionable version of this page is: DSE failures are unsigned-load attempts,
which are rare and loud, while the signed-vulnerable-driver problem belongs to blocklist telemetry.

## What a defender sees

Unsigned driver load attempts (event code 5038 and neighbors), code-integrity policy state changing
after boot, and test-signing boot entries. All three are strong signals with low legitimate
traffic. The fourth signal, a signed driver loading that happens to be vulnerable, is invisible
here by construction: see the [blocklist](driver-blocklist.md) page for where that lands.
