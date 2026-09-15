# Claim register

Every factual claim in this reference that is not self-evident from the text
carries an opaque id, `BZM2-<domain>-<nnn>`. This file is the public half of the
register: the id and the claim, and nothing else.

Each id resolves, in the internal ledger, to a specific document, page or source
locator behind it. That resolution is not public — some of the material is under
NDA. What is public is the guarantee: **if a claim has no id, it should not be
here**, and any id can be challenged and traced to real source material in one
hop by anyone with access to the internal ledger.

`kind` says what sort of evidence stands behind the claim, without saying what
that evidence is:

| kind | meaning |
| --- | --- |
| `vendor-stated` | the vendor's own documentation says it in words |
| `vendor-drawn` | derived from vendor material that demonstrates it rather than stating it — a schematic, a register map, reference source |
| `measured` | observed by us on real hardware |
| `our-inference` | reasoned by us from the above; the weakest kind, and always marked |
| `third-party` | a public datasheet or standard not belonging to the vendor |

## Register

| id | claim | kind |
| --- | --- | --- |
| `BZM2-ENG-001` | The engine identifier is a 12-bit row/column pair, row in the low six bits: `engine_id = (col << 6) \| row`. | `vendor-drawn` |
| `BZM2-ENG-002` | `StartNonce` and `EndNonce` are per addressable engine tile. The four engines at a tile share one nonce window. | `vendor-drawn` |
| `BZM2-ENG-003` | A device carries 236 addressable engine tiles of 4 engines each, 944 engines per ASIC. | `vendor-stated` |
| `BZM2-ENG-004` | Both nonce window endpoints must be even. | `vendor-stated` |
