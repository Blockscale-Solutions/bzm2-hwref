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
| `third-party` | a public source not belonging to the vendor: a datasheet, a standard, or a published open-source implementation |

## Register

| id | claim | kind |
| --- | --- | --- |
| `BZM2-ENG-001` | The engine identifier is a 12-bit row/column pair, row in the low six bits: `engine_id = (col << 6) \| row`. | `third-party` |
| `BZM2-ENG-002` | The register map exposes **one nonce window per addressable engine position**: `StartNonce` and `EndNonce` are written against the same 12-bit engine id as every other work register, and no finer unit appears in the write path. | `third-party` |
| `BZM2-ENG-003` | A device carries **236 addressable engine positions**. | `third-party` |
| `BZM2-ENG-004` | Both nonce window endpoints must be even. | `vendor-stated` |
| `BZM2-ENG-005` | Each addressable position contains **4 engines**, for 944 engines per ASIC. | `vendor-stated` |

### Public sources for `third-party` rows

`third-party` means the source is public and can be named here, which is the
point of the kind. These three resolve to
[`johnny9/ESP-Miner-Bonanza`](https://github.com/johnny9/ESP-Miner-Bonanza)
(GPL-3.0), an independent open-source implementation that drives this part:

| id | where |
| --- | --- |
| `BZM2-ENG-001` | `components/asic/bzm_topology.c:78` - `physical_id = ((uint16_t) column << 6) \| row`; 12-bit width from `components/asic/include/bzm.h:16` (`BZM_MAX_ENGINE_COUNT 4096`) |
| `BZM2-ENG-002` | `components/asic/bzm_work.c:33-34` writes `BZM_REG_START_NONCE` and `BZM_REG_END_NONCE` against `work->engine_id`, the same id used for every other work register at `:30-56`; offsets at `components/asic/bzm_work_registers.h:11-12` |
| `BZM2-ENG-003` | `components/asic/include/bzm_topology.h:16` - `BZM_TOPOLOGY_ENGINE_COUNT 236U`, asserted as a hardware-validity gate at `components/asic/bzm_bringup.c:1031`. Independently corroborated by our own capture: 23,600 work engines across 100 devices |

**`BZM2-ENG-005` deliberately has no public row.** The x4 is vendor-only. Note
that `944` appears in the same open-source firmware and means something else
there - 236 positions x 4 **ASICs on a board**, not 236 positions x 4 engines on
one ASIC. Citing it for the ASIC-internal x4 would be wrong by construction while
every individual number looked right.

