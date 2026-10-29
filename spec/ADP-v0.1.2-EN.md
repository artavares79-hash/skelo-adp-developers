# Agent Deal Protocol (ADP) v0.1.2 — Normative Specification (English)

Status: **Draft specification; not yet agreed with third parties or independently reviewed.**
Version: 0.1.2 — a *compatible* consolidation of ADP v0.1.1 (German source text `ADP-v0.1.1.md`) and the v0.1.2 changes (`ADP-v0.1.2.md`, German); both German source documents are internal working texts and are not part of this release - this English text consolidates them.
Publication status of this copy: **Draft v0.1.2, published for reading and review.** Licence terms for this text have not been decided yet; until they are published, no permission beyond reading is granted.
Note on identifiers: the extension URI `https://adp-spec.org/ext/v0.1` (section 10) is used purely as a *namespace identifier string*; implementations compare it as an opaque string and never need to resolve it. As of 2026-10-29 the authors cannot demonstrate control of the domain `adp-spec.org` (it does not resolve); no ownership of that domain is claimed.
The key words **MUST**, **MUST NOT**, **SHOULD**, **MAY** are to be read as in RFC 2119 / RFC 8174.

## 0. About this document

**This English text is the normative text of ADP v0.1.2.** It is a translation and consolidation, not a redesign: **no protocol semantics were changed** while translating. Every wire value, object field, hash and signature rule of v0.1.1 is unchanged. The only normative differences of v0.1.2 relative to v0.1.1 are collected in §18 ("Changes in v0.1.2") and are all additive or enforce rules v0.1.1 already stated. Where this text and the German v0.1.1 text disagree, treat it as an erratum of this document and report it; the test vectors (§16) decide interoperability questions.

Object `*Version` constants (`adp-acceptance/0.1`, `adp-verification/0.1`, `adp-record/0.1`), the extension URI (`https://adp-spec.org/ext/v0.1`) and all hash values of the examples in §13 are unchanged from v0.1.1.

Editorial notes on the German source (no semantic effect): (a) the AP2 constraint is spelled `payment.x-adp-deal-reference` in §2.5 of the source and `x-adp.deal_reference` in §11 and in the examples; this text uses `x-adp.deal_reference` everywhere except where it quotes both spellings, and treats the spelling as an AP2 binding detail outside the ADP core; (b) in the source, the DealRecord section appears after §14; here it is §13.11.

## 1. Purpose, scope, and what ADP is not

ADP is a **universal Agent Deal Protocol**. It settles one gap between agents that do not know each other: **whether a service has been performed as agreed, who may decide that, and how that decision releases a follow-up action — in a way a third party can verify independently.** What "release" means is decided by a *binding*:

* a **payment binding** (AP2, x402, ERC-8183, PSP rails; §12) — **optional**;
* a **payment-free binding** (§17) — release means: the performance is proven to meet the agreed terms and the follow-up (hand-over to the next stage, an approval, an internal business process) may proceed.

Payments, wallets, AP2 and x402 are **not a prerequisite for any ADP function**.

ADP does **not** define: a transport, agent discovery, general negotiation, a general identity system, wallet systems, the owner's authority as such, a payment rail, an escrow system, reputation, or a general dispute resolution procedure. For those, ADP refers to A2A, AP2, MCP, x402/ERC-8183/PSP rails and external identity systems. §19 lists precisely which responsibilities stay with the integrator.

### 1.1 The five core elements

| # | Element | Kind | Mandatory in v0.1 |
|---|---|---|---|
| 1 | `dealId` | convention (no object) | yes |
| 2 | `AcceptanceSpec` | signed object | yes |
| 3 | `VerificationResult` | signed object | yes |
| 4 | Release rule (historically "settlement rule") | normative rule (no object) | yes |
| 5 | `DealRecord` | derived, referencing object | structure normative; exchange optional |

No sixth object is defined. Fields that were considered and rejected are documented where they would otherwise be expected.

### 1.2 Terminology (wire values unchanged)

| Wire value / name | Meaning |
|---|---|
| state `SETTLED`, `DealRecord.outcome = "SETTLED"` | **Successfully released conclusion.** With a payment binding: the payment was released. Payment-free: the performance was established and the release granted. |
| state `REJECTED`, `outcome = "REJECTED"` | Conclusion without release (FAIL, expiry, reversal). |
| "settlement rule" (§5) | The **release rule**; the seven conditions of §5.1 apply unchanged. |
| error `ALREADY_SETTLED` | The one-time consumption has already happened (§5.6). |

Implementations MAY use other words in their user interfaces (for example "released"); on the wire they MUST use the values above.

## 2. `dealId`

### 2.1 Format
`dealId` is a **UUIDv4** (RFC 9562), lowercase with hyphens, for example `8f14e45f-ceea-467e-9c99-2c8e3b6a1c1f`. No URN prefix is required; separation from foreign identifiers is the job of the container (§2.5), not of the format.

### 2.2 Creation
* The **requester** (the agent asking for the performance — normally the later payer) MUST create `dealId` **before** the first `AcceptanceSpec` is signed, at the latest when it sends the request message.
* Creation uses a cryptographically secure random generator, 122 random bits (standard UUIDv4). No central registry or coordinator is needed.

### 2.3 Uniqueness / collision protection
* The collision probability of UUIDv4 is negligible at realistic deal volumes.
* **Additional protection (normative):** A `dealId` is bound to exactly **one** tuple `(requesterKeyId, providerKeyId, acceptanceSpecHash)` as soon as an `AcceptanceSpec` with this `dealId` has been signed. If the same `dealId` later appears with a **different** `acceptanceSpecHash` or different parties, every ADP-conformant participant MUST treat it as a conflict and reject it with the error `DEAL_ID_COLLISION` (§9). This replaces a central registry by a local uniqueness check at every participant.

### 2.4 Immutability
After the first signed reference to an `AcceptanceSpec`, `dealId` is **immutable**. A new deal (also one with changed terms) MUST receive a new `dealId`.

### 2.5 References in existing standards
| Standard | Location | Type |
|---|---|---|
| A2A | `Task.metadata["https://adp-spec.org/ext/v0.1"]["dealId"]` (extension namespace, §10) | string |
| AP2 | new constraint type in the open mandate (§11), field `dealId` | string, part of a new constraint type that AP2 explicitly allows |
| x402 | `extra.dealId` in the payment-requirements / settlement object (§12.1) | string; `extra` is reserved by x402 for additional rail-specific fields |
| ERC-8183 | the `reason` parameter of `complete()`/`reject()` MUST contain a hash that includes `dealId` (§12.2) | `bytes32` commitment |

### 2.6 Replay protection
`dealId` alone does not protect against re-submission of individual messages (that is the job of `nonce` in `VerificationResult`, §4.6, and of the one-time consumption in §5.6). `dealId` only prevents two independent deals from being mixed up unnoticed.

## 3. `AcceptanceSpec`

### 3.1 Basic rule
An `AcceptanceSpec` MUST be completely created, canonicalised, hashed and signed **before** execution of the performance begins (state `ACCEPTANCE_LOCKED`, §8). From then on it is **immutable**: changed conditions require a new `AcceptanceSpec` with its own hash **and** — because that changes the economic content of the agreement — a new `dealId` (§2.4), unless both parties consensually sign a replacement reference (§3.7).

### 3.2 Canonical schema (v0.1, minimal)

| Field | Type | Mandatory | Meaning |
|---|---|---|---|
| `specVersion` | string, constant `"adp-acceptance/0.1"` | yes | versioning of the object type |
| `dealId` | string (UUIDv4) | yes | binding to §2 |
| `subjectHash` | string (hex SHA-256) | yes | hash of the agreed performance description (for example the hash of the A2A request message or an AP2 checkout reference). ADP does not define *what* is hashed — only that a hash of the performance agreed elsewhere is bound here |
| `verificationMethod` | object `{type, …}` | yes | §3.3 |
| `acceptanceCondition` | object, method-dependent | yes | §3.3 |
| `verifierAuthorization` | object | yes | §3.4 |
| `validity` | object `{notBefore, notAfter}` (RFC 3339) | yes | validity window for delivery **and** verification |
| `evidenceRequirements` | array of strings | yes; may be empty `[]` | which evidence types a `VerificationResult` must reference (§4, §4.7) |
| `issuer` | string (identity reference, defined outside ADP) | yes | who issued the spec |
| `signature` | object | yes | §7 |

There are nine mandatory fields (not counting `signature` itself, which is the envelope). `providerAck` (§3.6) is optional.

**Explicitly removed relative to the phase-0.5 sketch:**
* `timeoutBehavior` as a field — removed. The behaviour when `validity.notAfter` expires is completely and uniformly fixed by the state machine (§8: no `VERIFIED_PASS` without a valid deadline ⇒ transition to `REJECTED`). A choice field (`auto-accept`/`auto-reject`/`escalate`) would permit inconsistent behaviour between implementations. v0.1 knows exactly **one** timeout behaviour: expiry without a valid `VERIFIED_PASS` ⇒ `REJECTED`.
* `checks[]` as an array of several checks — reduced to a single `verificationMethod` object. T1 and T2 each need exactly one method; an array would be a feature in stock without demonstrated need (§17 principle). If a later use case needs AND-combined checks, that is a backward-compatible extension of `verificationMethod.type` (for example `type: "all-of"` with a sub-list).

### 3.3 `verificationMethod` / `acceptanceCondition` (v0.1: two methods, no more)

v0.1 defines **only two** method types, because only these are demonstrated by T1 and T2. Further types are a later, additive extension.

**`type: "hash-equals"`** (case T1):
```json
"verificationMethod": {"type": "hash-equals", "algorithm": "sha-256", "canonicalization": "JCS-RFC8785"},
"acceptanceCondition": {"expectedHash": "<hex>"}
```
The result is accepted if `SHA-256(JCS(delivery content))` equals `expectedHash` exactly.

**`type: "sandboxed-test-suite"`** (case T2):
```json
"verificationMethod": {
  "type": "sandboxed-test-suite",
  "testSuiteHash": "<hex SHA-256 of the hidden test suite, bound in advance>",
  "sandboxProfile": {"maxRuntimeSeconds": 30, "maxMemoryMB": 512, "network": "none"}
},
"acceptanceCondition": {"requiredExitCode": 0}
```
The result is accepted if the test suite with hash `testSuiteHash`, executed in the described sandbox profile against the delivery, ends with `requiredExitCode`. The test suite itself is **not** disclosed in the `AcceptanceSpec` (only its hash); disclosure happens at verification time by the verifier (§14).

An ADP-v0.1-conformant verifier MUST support at least `hash-equals`; `sandboxed-test-suite` is **optional**, but if an `AcceptanceSpec` references this type, a `VerificationResult` for it MUST supply the evidence fields described in §4.7, otherwise it is invalid.

### 3.4 `verifierAuthorization` — who may verify

**Normative core decision (the answer to "the verifier must not by default be the buyer"):** v0.1 allows exactly **one** mechanism: **`designated-key`**.

```json
"verifierAuthorization": {
  "mode": "designated-key",
  "verifierKeyId": "<identity reference, resolved externally>",
  "verifierPubKey": "<base64url Ed25519 public key>"
}
```

A `VerificationResult` is valid only if it was signed with the private key belonging to `verifierKeyId`/`verifierPubKey` (otherwise `UNAUTHORIZED_VERIFIER`, §9). **Who** stands behind this key is arbitrary:
* the requester itself (`verifierKeyId` = requester key) — permitted, but the specification does not force anyone to do this;
* a **named third party** (for example a specialised checking agent) — same mechanism, different key;
* a **deterministic verifier service** (for example a sandbox execution environment with its own key) — same mechanism.

**Alternatives examined and rejected for v0.1:**
* *Role enum (`buyer`/`third-party`/…)* instead of a key reference — rejected. A role name triggers no cryptographic check; in the end a key is needed anyway. The role is pure description without normative effect and is therefore not included (it could be added as an optional, non-normative free-text field `verifierLabel`, but **not** in the v0.1 core).
* *Threshold / multiple verifiers (M-of-N)* — rejected for v0.1. Neither T1 nor T2 requires it; it would complicate the release rule (§5) considerably (aggregation logic, partial quorums). It can be added in a later version as an alternative `mode` (`"threshold-key-set"`) without breaking v0.1 objects, because `verifierAuthorization.mode` is already an open discriminator.
* *Free-text `verifierLabel`* — removed (see above).

### 3.5 Protection against later change (core requirement)
1. The `AcceptanceSpec` is signed **before** execution starts (`issuer` signature, §7).
2. Its hash (`acceptanceSpecHash` = SHA-256 over the JCS of the spec **without** the `signature` field, §6) is **embedded in the agreement / the owner authorisation** — with a payment binding as an AP2 constraint (§11), in the payment-free profile through the mechanism of §17.2 — and not merely sent along loosely.
3. A `VerificationResult` (§4) references **exclusively** `acceptanceSpecHash`, never the content directly.
4. The release rule (§5) requires that the referenced `acceptanceSpecHash` **equals the independently bound hash**.

**Result:** neither provider nor buyer can, after delivery, slip in a different `AcceptanceSpec` without either (a) the signature check failing or (b) the referenced hash no longer matching the bound hash → error `ACCEPTANCE_SPEC_MISMATCH` (§9). The provider is de facto bound by its execution (which rests on the original spec); it MAY additionally countersign (`providerAck`, optional, §3.6), which is recommended in v0.1 but not mandatory — and mandatory in the payment-free profile (§17).

### 3.6 Optional field `providerAck`
```json
"providerAck": {"kid": "<provider key id>", "sig": "<signature over the same JCS body without signature/providerAck>"}
```
SHOULD be set when the provider explicitly accepts the spec before it starts executing (it strengthens the evidence in a dispute — which lies outside ADP). It need not be set for v0.1 conformance, because AP2/A2A consent to execution is implicitly present (the provider only starts work if it knows and accepts the referenced spec), and a mandatory field would not strengthen the core chain (§3.5) further. `providerAck` does **not** change `acceptanceSpecHash` (§6).

### 3.7 Replacement (change after signing)
An `AcceptanceSpec` MUST NOT be edited. Replacement is possible only through a **new**, fully signed `AcceptanceSpec` with the same `dealId`, **and only while the deal is still in state `CREATED`** (§8) — that is, **before** the transition to `ACCEPTANCE_LOCKED`. After `ACCEPTANCE_LOCKED` the bound hash is final; every "change" then necessarily means a new `dealId` (§2.4).

## 4. `VerificationResult`

### 4.1 Basic rule
A `VerificationResult` is the **only** source for the statement "PASS" or "FAIL". It is created **after** delivery, **within** the window fixed in `AcceptanceSpec.validity`.

### 4.2 Canonical schema

| Field | Type | Mandatory | Meaning |
|---|---|---|---|
| `resultVersion` | string, constant `"adp-verification/0.1"` | yes | versioning |
| `dealId` | string (UUIDv4) | yes | binding to §2 |
| `acceptanceSpecHash` | string (hex SHA-256) | yes | which spec applied (§3.5) |
| `deliveryHash` | string (hex SHA-256) | yes | hash of the verified delivery (not the delivery itself) |
| `verifierId` | string (= `verifierAuthorization.verifierKeyId` of the referenced spec) | yes | who verified |
| `result` | enum `"PASS"` \| `"FAIL"` | yes | §4.3 |
| `evidenceRefs` | array of `{type, hash}` | yes; may be `[]` only if `evidenceRequirements` in the spec was empty | evidence references, §4.7 |
| `timestamp` | string (RFC 3339) | yes | time of verification |
| `nonce` | string (UUIDv4) | yes | replay protection, §4.6 |
| `signature` | object | yes | §7; the key MUST match `verifierId` |

Nine mandatory fields (not counting `signature`).

### 4.3 Only PASS/FAIL — examined and confirmed
**Decision: YES, only PASS/FAIL for v0.1.**
* T1 (`hash-equals`): the result is binary by definition — hashes are equal or not. A score would be meaningless.
* T2 (`sandboxed-test-suite`): `requiredExitCode` is binary as well. A percentage of passed individual tests is conceivable but not demanded by T1/T2 (the requirement was "tests PASS/FAIL", not "test coverage").
* No demonstrated use case in phases 0/0.5 demands scores, opinions or multi-level quality models. **Not included.** A later version could introduce a third value `INDETERMINATE` for "the verifier could not finally verify"; for v0.1 this is deliberately **not** distinguished: *not conclusively verifiable counts as `FAIL`* (conservative, see threat model §15).

### 4.4 What a third party can verify cryptographically
An independent checking program that has (a) the referenced `AcceptanceSpec`, (b) the `VerificationResult` and (c) the verifier's public key **can, without any further communication**, establish:
1. **Which `AcceptanceSpec` applied** — by recomputing `SHA-256(JCS(AcceptanceSpec without signature))` and comparing with `VerificationResult.acceptanceSpecHash`.
2. **Which result was verified** — `deliveryHash` is available; whether it matches the actual delivery is checked by a third party by recomputing, if it receives the delivery itself (ADP does not require every third party to do so — only that it is **possible**).
3. **Who verified** — `verifierId`, plus signature verification with the key stored in `AcceptanceSpec.verifierAuthorization.verifierPubKey`.
4. **Whether this verifier was authorised** — comparison `VerificationResult.verifierId == AcceptanceSpec.verifierAuthorization.verifierKeyId` **and** a valid signature with the key stored there.
5. **PASS or FAIL** — field `result`, protected against falsification by the signature.

### 4.5 Unauthorised verifier
If `verifierId` does not equal `AcceptanceSpec.verifierAuthorization.verifierKeyId`, the `VerificationResult` MUST be discarded as invalid (`UNAUTHORIZED_VERIFIER`), regardless of whether its signature is technically valid. Authorisation is **bound to the spec**, not global.

**Order of checks (erratum, clarified — semantics unchanged):** this identity comparison (`vr.verifierId == spec.verifierAuthorization.verifierKeyId`) MUST be performed **before** the cryptographic verification of the `VerificationResult` signature (§5.1 condition 5). That is the only meaning of the phrase "regardless of whether its signature is technically valid": an implementer MUST NOT, and in the case of a mismatching `verifierId` should not, need to touch the signature at all — the result is rejected on identity grounds alone.

### 4.6 Replay protection
`nonce` MUST be unique per `(dealId, verifierId)` pair. A second `VerificationResult` with an already seen `(dealId, nonce)` MUST be discarded. This prevents an old, valid PASS result from being re-submitted for another purpose. (Protection against **multiple consumption** of the same valid result is a separate rule, §5.6.)

### 4.7 Evidence references
`evidenceRefs[].type` MUST match an entry of `AcceptanceSpec.evidenceRequirements` (at least one entry per required type). For `hash-equals`, `{"type": "delivery-hash", "hash": "<deliveryHash>"}` suffices. For `sandboxed-test-suite`, an entry `{"type": "test-execution-log-hash", "hash": "<SHA-256 of the execution log>"}` MUST additionally be present (the log itself is referenced, not contained in the object). The precise, enforceable form of these rules is given in §18.1.

## 5. Release rule ("settlement rule"; not an object)

### 5.1 Normative core
A `VerificationResult` with `result: "PASS"` MAY trigger a release for `dealId` **if and only if all** of the following conditions hold:

1. **`dealId` agreement:** `VerificationResult.dealId` == `AcceptanceSpec.dealId` == the deal reference in the binding object (§12; in the payment-free profile §17).
2. **Valid `AcceptanceSpec`:** its signature (§7) is valid, and its hash equals the independently bound hash (§3.5, §11, §17.2).
3. **Delivery binding:** `VerificationResult.deliveryHash` corresponds to an actually referenceable delivery (artifact hash from the transport protocol, for example an A2A artifact).
4. **Authorised verifier:** as in §4.5.
5. **Valid signatures:** both `AcceptanceSpec.signature` and `VerificationResult.signature` are cryptographically valid (§7).
6. **Within validity:** `AcceptanceSpec.validity.notBefore ≤ VerificationResult.timestamp ≤ AcceptanceSpec.validity.notAfter`.
7. **Not already consumed:** see §5.6.

If these seven conditions hold, the release (binding-specific: `capture`, `complete`, PSP capture, or the payment-free follow-up) **MUST** be permitted to be triggered. A binding adapter that nevertheless refuses despite PASS and valid conditions behaves outside ADP (that is a matter for the respective binding / owner override and is not regulated by ADP — see "buyer refuses despite PASS" in the threat model, §15).

### 5.2 FAIL
A `VerificationResult` with `result: "FAIL"` MUST NEVER trigger a release. A binding adapter MUST, on a valid FAIL result, trigger the binding-specific reversal path (`void`/`refund` for x402, `reject()` for ERC-8183; payment-free: no follow-up, outcome `REJECTED`). A FAIL with an **invalid** signature or wrong `dealId`/`acceptanceSpecHash` is simply **ignored** (neither release nor reversal is triggered by it) — the deal remains in its previous state until a valid result or a timeout occurs.

### 5.3 No result / timeout
If `validity.notAfter` expires without a valid `VerificationResult` with `PASS`, the state MUST transition to `REJECTED` (§8) and the binding-specific reversal path MUST be triggerable (for example x402 `reclaim`, which according to its specification can anyway be executed unilaterally by the client after `captureDeadline` — see §12.1).

### 5.4 Why no separate `SettlementAuthorization` object
A separate signed object would either (a) duplicate the fields of `VerificationResult` (redundancy, an additional source of error in case of inconsistency between the two objects) or (b) require a third party to issue it, which according to the phase-0.5 analysis need not exist. The rule in §5.1 is fully evaluable from already existing, signed objects — an adapter (§12, §17) implements it as a **local check**; no new network object is exchanged.

### 5.5 Binding neutrality
The rule in §5.1 uses **no** binding-specific terms. §12 shows how x402 and ERC-8183 consume it; a future PayPal/Stripe/stablecoin binding, like the payment-free profile, must check the same seven conditions without any change to §5.1.

### 5.6 Replay and double-consumption protection
Every adapter MUST keep, per `(dealId, acceptanceSpecHash)` pair, a **one-time-consumption state** (local to the adapter, not ADP-central): as soon as a release has been triggered for this pair, every further release attempt with the same pair MUST be rejected with `ALREADY_SETTLED` — regardless of whether a new, technically valid `VerificationResult` with a different `nonce` is presented. This closes the gap that a second PASS result (for example issued again by the same verifier) could trigger a second release.

The consumption state and the nonce history MUST survive restarts of the adapter for as long as the replayed object could still be accepted (at least until `validity.notAfter`, §15 #5). In concurrent deployments the claim of the one-time consumption MUST be atomic (exactly one claimant wins). The reference implementations provide an in-memory engine and an optional durable engine (§20).

## 6. Canonicalisation and hashing

**One mandatory method for all ADP objects:**

1. **Serialisation / canonicalisation:** JSON Canonicalization Scheme (JCS), **RFC 8785**. Reason for reuse instead of invention: JCS is already used by A2A (agent-card signing, §8.4.1 of the A2A specification) and similar determinism requirements apply to AP2 (SD-JWT hash computation) — one method across the stack reduces implementation errors.
2. **Before canonicalisation:** the field `signature` (and `providerAck`, if present) MUST be removed from the object — exactly the pattern of A2A §8.4.1 ("signature field exclusion").
3. **Hash algorithm:** **SHA-256**, output as a lowercase hexadecimal string (compatible with VCAP §5.1 and x402/AP2 practice).
4. **All numeric fields** in ADP objects are either strings (hex, IDs, timestamps) or integers without fractional digits (for example `requiredExitCode`, `maxRuntimeSeconds`) — floating-point numbers with JCS rounding ambiguity are deliberately avoided in **ADP's own** objects. (For **foreign** payloads — for example the T1 result object itself — JCS applies according to its own definition; see the test vectors.)
5. **Number format (erratum):** RFC 8785 prescribes the ECMAScript `Number::toString` serialisation for JSON numbers. Accordingly an integral floating-point number serialises **without** a decimal point — `44.0` **MUST** be canonicalised as `44`, **not** as `44.0`. Implementers who use a standard JSON library (for example Python's `json.dumps`) directly often get the wrong result here, because such libraries retain the floating-point character of the source value. An ADP-v0.1.1-conformant canonicalisation MUST implement this behaviour correctly for **every** canonicalised payload — not only for ADP's own objects (which per item 4 contain no floating-point numbers anyway) but also for referenced foreign payload such as delivery contents whose hash is embedded in an `AcceptanceSpec`/`VerificationResult`.

No home-grown method is used. Only RFC 8785 (JCS) and SHA-256 (FIPS 180-4) are used.

*Practical note (informative):* the reference implementations additionally refuse numbers outside their documented scope with `CANONICALIZATION_ERROR` rather than guessing; integrators SHOULD use integers (for example cents) or strings for decimals.

## 7. Signature model

### 7.1 What is signed
The following ADP objects MUST be signed to be valid: `AcceptanceSpec`, `VerificationResult`. A `DealRecord` MAY be signed (§13.11). No other object exists in v0.1.

### 7.2 Signature method
* **Algorithm:** **EdDSA over Ed25519** (RFC 8032). Reason for reuse: identical to the method chosen by VCAP, and compatible with common agent identity keys (`did:key`, RFC 9421 keys).
* **Signature input:** `Ed25519_Sign(privateKey, JCS(object without "signature" field))` — see §6.
* **Envelope format:**
  ```json
  "signature": {"alg": "EdDSA", "kid": "<key reference>", "sig": "<base64url, unpadded>"}
  ```
* No own certificate format, no own key distribution.

### 7.3 Identity versus signature binding (clean separation)
**ADP defines no identity system.** `kid` (and `verifierKeyId`, `issuer`) is an **external** reference whose resolution lies outside ADP: it can be an A2A **signed agent card** (public key contained there), an RFC 9421 / Web Bot Auth JWKS directory, a `did:key`/`did:web` document, or a company-internal key directory. **ADP requires only:** the referenced key MUST be resolvable and trustworthy for the recipient in some way — *how* is the deployment's business, not this specification's.

**Interface requirement for key resolution (erratum, clarified, no new mechanism):**
1. `kid` identifies exactly one key; ADP makes no statement about how this key is obtained.
2. Key resolution (the mapping `kid` → concrete public key) lies **completely outside ADP** — for `AcceptanceSpec.verifierAuthorization` it is already solved **inside** the object in `designated-key` mode (§3.4: `verifierPubKey` is embedded directly, no external resolution needed); for the signature of the `AcceptanceSpec` itself (by `issuer`) and for `providerAck` (by the provider `kid`) there is **no** equivalent embedded field — the recipient MUST resolve these keys through a mechanism outside ADP (see above).
3. **MUST rule:** a signature verification MUST NOT be considered successful as long as `kid` has not been resolved by the verifying participant to **exactly one** key it considers trustworthy. If `kid` cannot be resolved (unknown, ambiguous, untrusted), the verification MUST be treated like an invalid signature — error code `INVALID_SIGNATURE` (§9), **no** separate error code for a failed resolver step, because the result is identical from the point of view of the calling check ("cannot be confirmed as validly signed") and an additional code would needlessly enlarge the small error model demanded in §9/§17.

### 7.4 Alternatives examined and rejected
* **JWS instead of raw Ed25519 + JCS:** rejected for v0.1, because an additional encoding layer (base64url JSON header) adds no value over the established VCAP/A2A practice and the test vectors stay easier to follow when signature object and payload are separate. A later version MAY admit JWS as an alternative `alg` family (`signature.alg` is already an open discriminator).
* **EIP-712 (as in x402 offer & receipt):** rejected as a **mandatory** method of the ADP core, because it presupposes an EVM address / chain-ID binding that is not justified outside a payment binding (§12). Payment bindings MAY additionally require EIP-712 signatures where the target rail needs them — that is a matter of the binding, not of the core.

## 8. Minimal state machine

Only economically relevant ADP states — no A2A task states are duplicated.

```
CREATED
  │  (dealId created, request sent — pure bookkeeping, no new signal)
  ▼
ACCEPTANCE_LOCKED
  │  (AcceptanceSpec signed + hash bound — §3.5)
  ▼
DELIVERED
  │  (delivery referenceable, deliveryHash exists)
  ├──► VERIFIED_PASS ──► SETTLED
  ├──► VERIFIED_FAIL ──► REJECTED
  └──► (validity.notAfter passes without a valid PASS) ──► REJECTED
```

**Explicitly removed state:** `EXECUTING`. Between `ACCEPTANCE_LOCKED` and `DELIVERED` no ADP object changes; the progress of execution is already fully represented by A2A `TASK_STATE_WORKING` ("ADP shall only define economically relevant state transitions"). A duplicate here would have no normative effect.

**Explicitly merged:** `EXPIRED` was **not** introduced as a separate final state but is a **transition reason** into `REJECTED` (economically identical outcome: no release). An optional, non-normative field of the `DealRecord` (`outcomeReason`) can distinguish "FAIL" from "EXPIRED" without the state machine itself needing more states.

### 8.1 Transition table

| From | To | Preconditions | Required objects | Signatures | Result |
|---|---|---|---|---|---|
| — | `CREATED` | `dealId` freshly created (§2.2/2.3) | — | — | `dealId` reserved |
| `CREATED` | `ACCEPTANCE_LOCKED` | `AcceptanceSpec` complete (§3.2), validly signed; `acceptanceSpecHash` bound (§3.5, §11, §17.2) | `AcceptanceSpec` | `issuer` (requester); optional `providerAck` | conditions for delivery/verification fixed |
| `ACCEPTANCE_LOCKED` | `DELIVERED` | delivery exists, `deliveryHash` computable; **must lie within the `validity` window** | transport artifact (outside ADP, for example A2A `Artifact`) | no ADP signature | basis for verification exists |
| `DELIVERED` | `VERIFIED_PASS` | valid `VerificationResult` with `result: PASS`, all checks of §5.1 (1–6) satisfied | `VerificationResult` | `verifierId` | release may be triggered |
| `DELIVERED` | `VERIFIED_FAIL` | valid `VerificationResult` with `result: FAIL` | `VerificationResult` | `verifierId` | reversal may be triggered |
| `VERIFIED_PASS` | `SETTLED` | §5.1 fully (including item 7, one-time consumption) satisfied, binding-side release successful | binding confirmation (outside ADP; payment-free: the follow-up was performed) | binding-specific | `DealRecord.outcome = SETTLED` |
| `VERIFIED_FAIL` | `REJECTED` | binding-side reversal triggered (payment-free: nothing to reverse) | binding confirmation (outside ADP) | binding-specific | `DealRecord.outcome = REJECTED` |
| `ACCEPTANCE_LOCKED` / `DELIVERED` | `REJECTED` | `validity.notAfter` exceeded without a valid PASS | none new | — | `DealRecord.outcome = REJECTED (expired)` |

**`SETTLED` and `REJECTED` are terminal.** No transition back; a new attempt requires a new `dealId`.

## 9. Error model (interoperable, minimal)

| Code | Meaning | Raised at |
|---|---|---|
| `INVALID_SIGNATURE` | signature of an ADP object does not verify against the referenced key (also: key not resolvable, §7.3) | §7 |
| `UNKNOWN_DEAL` | `dealId` cannot be assigned to a known `CREATED`/`ACCEPTANCE_LOCKED` state | §2, §8 |
| `DEAL_ID_COLLISION` | the same `dealId` seen again with a differing `(parties, acceptanceSpecHash)` tuple | §2.3 |
| `ACCEPTANCE_SPEC_MISMATCH` | the referenced `acceptanceSpecHash` does not match the independently bound hash | §3.5, §5.1(2) |
| `UNAUTHORIZED_VERIFIER` | `verifierId` in the `VerificationResult` ≠ `verifierAuthorization.verifierKeyId` of the spec | §4.5, §5.1(4) |
| `DELIVERY_HASH_MISMATCH` | the referenced `deliveryHash` does not correspond to the actual delivery (on own recomputation) | §5.1(3) |
| `VERIFICATION_EXPIRED` | `VerificationResult.timestamp` lies outside `validity` | §5.1(6), §5.3 |
| `ALREADY_SETTLED` | a consumed PASS already exists for `(dealId, acceptanceSpecHash)` | §5.6 |
| `CANONICALIZATION_ERROR` | an object cannot be canonicalised unambiguously according to §6 (for example a forbidden floating-point form) | §6 |

Nine error codes. No error hierarchy, no sub-codes — deliberately small (§17). A repeated `nonce` (§4.6) has no dedicated code: the object is simply discarded (reference implementations signal it as a distinct exception/error class, not as a tenth wire code). A release refused because required evidence is missing (§18.1) is a *decision* (`DENIED` with a reason beginning `EVIDENCE_REQUIREMENTS_UNMET`), not a tenth error code.

## 10. A2A binding

**A2A itself is not changed.** ADP is declared as an **A2A extension** (A2A specification §4.6, "profile extension" + use of metadata).

### 10.1 Extension declaration
```json
{
  "capabilities": {
    "extensions": [
      {
        "uri": "https://adp-spec.org/ext/v0.1",
        "description": "Agent Deal Profile: acceptance criteria, verification result and settlement-authorization binding for agent-to-agent service deals.",
        "required": false
      }
    ]
  }
}
```
`required: false` — consistent with A2A §4.6.3: an agent without ADP support MUST NOT fail; it ignores the metadata and treats the task like any other A2A task (§10.4).

### 10.2 Transport of `dealId`
In `Task.metadata`, under the extension namespace key:
```json
{"metadata": {"https://adp-spec.org/ext/v0.1": {"dealId": "8f14e45f-ceea-467e-9c99-2c8e3b6a1c1f"}}}
```
Likewise in every `Message` that is ADP-relevant: `"extensions": ["https://adp-spec.org/ext/v0.1"]` plus a `metadata` entry with the same key.

### 10.3 `AcceptanceSpec` reference and `VerificationResult` transport
* The complete `AcceptanceSpec` (or `VerificationResult`) is transmitted as a `DataPart` of a `Message` under the same extension namespace:
  ```json
  {"kind": "data", "data": {"https://adp-spec.org/ext/v0.1": {"acceptanceSpec": { /* see §3.2 */ }}}}
  ```
* An A2A `Artifact` (the delivery) does **not** normatively reference its own hash in A2A itself (A2A has no mandatory `hash` field for artifacts — phase-0.5 finding); ADP-conformant participants therefore MUST additionally send the hash as an accompanying `DataPart` message: `{"data": {"https://adp-spec.org/ext/v0.1": {"deliveryHash": "<hex>", "artifactId": "<A2A artifactId>"}}}`.

### 10.4 Compatible behaviour without ADP support
An agent that does not declare/activate the extension sees perfectly normal A2A `Task`/`Message`/`Artifact` objects with additional `metadata` entries under a foreign URI that are meaningless to it — explicitly provided for by A2A §4.6.1, and breaks nothing. It can complete the task as usual; it merely does not take part in the ADP state machine (§8), and the ADP benefits (conditional, verification-bound release) do not apply for this task.

### 10.5 Versioning
`https://adp-spec.org/ext/v0.1` is the **complete, versioned** extension URI (A2A §4.6.3: "A new URI MUST be created for breaking changes"). `adp-acceptance/0.1`, `adp-verification/0.1`, `adp-record/0.1` (the object `*Version` fields) follow independently, so that an object schema can evolve on its own without breaking the transport extension URI as long as the change is backward compatible.

## 11. AP2 binding (payment binding; optional)

**AP2 itself is neither changed nor duplicated.** Only what AP2 cannot do by itself is bound: the link between `dealId`/`AcceptanceSpec` and an already existing AP2 owner authorisation.

### 11.1 New constraint type (explicitly allowed by AP2)
AP2 normatively allows new constraint types (`agent_authorization.md`: "New mandate types and new constraint types MAY be defined in addition to these"; unknown constraints on a verifier that does **not** know them lead to `unresolved_constraint` — i.e. the constraint is **never silently ignored** but forces explicit handling).

```json
{
  "type": "x-adp.deal_reference",
  "dealId": "8f14e45f-ceea-467e-9c99-2c8e3b6a1c1f",
  "acceptanceSpecHash": "a371ac92c8fae7e017d259ebeac4910b917a46ad029e35d16b4a4de12418633d"
}
```
This constraint is included in the **open** payment mandate (alongside `payment.amount_range`, `payment.allowed_payees`, etc.) and MUST — like every AP2 constraint — be satisfied in the **closed** mandate (AP2 verification: constraints are evaluated against the closed mandate).

### 11.2 What is thereby normatively bound
* **`dealId`** links the AP2 mandate with the A2A task (§10.2) and the payment-rail object (§12).
* **`acceptanceSpecHash`** prevents exactly the risk described in §3.5: a payee (provider) cannot obtain a settlement whose `VerificationResult` refers to a different `AcceptanceSpec` than the one bound in the mandate — the AP2 verification itself (not ADP) already fails in this case.
* The **maximum economic authorisation** (amount, category, counterparty) remains **entirely** in existing AP2 fields (`payment.amount_range`, `payment.allowed_payees`, possibly `payment.budget`) — ADP adds **no** field of its own for it, which would be duplication.

### 11.3 Explicitly not part of the binding
The AP2 statement "agent-to-agent delegation … outside the scope of the current specification" remains untouched — ADP does not delegate the mandate check itself, it only appends an additional constraint check already provided for by AP2. Owner authorisation **itself** (who may issue a mandate at all, human-present/human-absent flows) remains entirely with AP2 and the identity layer.

## 12. Payment bindings (optional, outside the core)

**The ADP core is binding-neutral (§5.5).** Bindings translate the release rule (§5.1) into rail-specific calls. A binding MAY read ADP core objects but MUST NOT change their schema.

### 12.1 ADP–x402 binding

| ADP concept | x402 counterpart |
|---|---|
| `dealId` transport | `extra.dealId` in the `PaymentRequirements`/settlement object (x402 `extra` is reserved for additional fields) |
| release rule §5.1 satisfied | precondition before the resource server **itself** (x402: "server consent … `capture` … not client-authorized") triggers the `capture` operation of the `auth-capture` scheme. **Normative clarification for ADP-conformant servers:** an ADP-v0.1-conformant resource server MUST refuse `capture` as long as no valid `VerificationResult` with `PASS` according to §5.1 exists — an **additional** obligation imposed by ADP, not a change to x402 itself. |
| §5.2 FAIL | resource server triggers `void` (the hold is released without capture) |
| §5.3 timeout | client uses x402's own `reclaim` mechanism after `extra.captureDeadline` — **unchanged from x402**; ADP adds nothing, because x402 already solves this unilaterally and without facilitator involvement |
| §5.6 one-time consumption | the `capture` call itself is, according to the x402 schema, already "No — once per payment" (not repeatable beyond the maximum); the additional `(dealId, acceptanceSpecHash)` check prevents **two different** `capture` calls from being justified with the same verification evidence if the payment is made in partial amounts |

### 12.2 ADP–ERC-8183 binding

| ADP concept | ERC-8183 counterpart |
|---|---|
| `verifierAuthorization` | the on-chain `evaluator` account MUST correspond to the verifier named in `AcceptanceSpec.verifierAuthorization.verifierKeyId` (binding by owner-side configuration at job creation, `setProvider`/constructor parameter — outside ADP) |
| release rule §5.1 satisfied | precondition before the evaluator calls `complete(jobId, reason)`. **Normative clarification:** `reason` MUST contain `SHA-256(JCS(VerificationResult without signature))` (according to ERC-8183 the field is already provided as an "optional attestation commitment … hash of off-chain evidence" — ADP merely fills it with a fixed content) |
| §5.2 FAIL | evaluator calls `reject(jobId, reason)`; `reason` likewise references the `VerificationResult` hash |
| §5.3 timeout | ERC-8183's own `claimRefund` mechanism after `expiredAt` — unchanged |
| dispute | **Explicitly not changed by ADP.** ERC-8183 itself states "No dispute resolution or arbitration; reject/expire is final" — ADP adopts this unchanged; an ADP FAIL is therefore as final as an ERC-8183 `reject`. |

### 12.3 Extensibility
A future `ADP-PayPal` / `ADP-Stripe` / `ADP-Stablecoin-X` binding MUST check exclusively the seven conditions of §5.1 and translate them into rail-specific release/reversal calls. No binding MAY require new fields in `AcceptanceSpec`/`VerificationResult` — that would violate binding neutrality (§5.5) and would no longer be an ADP-v0.1-conformant binding.

## 13. Normative examples and the `DealRecord`

### 13.1 T1 — deterministic data transformation (complete example)
Real, recomputed values (generation method: see the test vectors, §16). **Test keys — never use in production.**

Flow: `input → agreement (A2A request + AP2 mandate with x-adp.deal_reference) → AcceptanceSpec (signed, ACCEPTANCE_LOCKED) → delivery (A2A artifact) → VerificationResult (PASS) → release (x402 capture) → DealRecord`

**13.2 `dealId`:** `8f14e45f-ceea-467e-9c99-2c8e3b6a1c1f`

**13.3 `AcceptanceSpec` (complete, signed)**
```json
{
  "specVersion": "adp-acceptance/0.1",
  "dealId": "8f14e45f-ceea-467e-9c99-2c8e3b6a1c1f",
  "subjectHash": "9837630e92998ac2ead4300b63ecd9569db49b7ffb15e3a50d8f298f0ebc70cd",
  "verificationMethod": {"type": "hash-equals", "algorithm": "sha-256", "canonicalization": "JCS-RFC8785"},
  "acceptanceCondition": {"expectedHash": "5770e1a47a18adf70baf4b335998bfc10d4df98927e6878a556ef26825f83d10"},
  "verifierAuthorization": {"mode": "designated-key", "verifierKeyId": "did:key:buyer-verifier-1", "verifierPubKey": "A6EHv_POEL4dcN0Y50vAmWfk1jCbpQ1fHdyGZBJVMbg"},
  "validity": {"notBefore": "2026-09-22T10:00:00Z", "notAfter": "2026-09-22T10:10:00Z"},
  "evidenceRequirements": ["delivery-hash"],
  "issuer": "agent:buyer-a.example",
  "signature": {"alg": "EdDSA", "kid": "did:key:buyer-a-1", "sig": "c6TdGJyg9rZnfV8_etSlodXCZSZr7EUMcyB-Ct2_QcOwabOW9EXnRPZisLKmQE-BI8gmjMbZr2vHUC-bEshLBQ"}
}
```
`acceptanceSpecHash` (SHA-256 over the JCS without `signature`) = `a371ac92c8fae7e017d259ebeac4910b917a46ad029e35d16b4a4de12418633d`

**13.4 AP2 mandate constraints (excerpt)**
```json
{ "type": "payment.amount_range", "min": "0", "max": "1.00", "currency": "EUR" },
{ "type": "payment.allowed_payees", "payees": ["agent:provider-b.example"] },
{ "type": "x-adp.deal_reference",
  "dealId": "8f14e45f-ceea-467e-9c99-2c8e3b6a1c1f",
  "acceptanceSpecHash": "a371ac92c8fae7e017d259ebeac4910b917a46ad029e35d16b4a4de12418633d" }
```

**13.5 Delivery (A2A artifact content, JCS-relevant part)**
```json
{"totals": {"A": 120.5, "B": 44.0}}
```
Canonical JCS bytes (RFC 8785 — note `44.0` → `44`, no decimal point, §6 item 5): `{"totals":{"A":120.5,"B":44}}`

`deliveryHash` = `SHA-256(canonical bytes)` = `5770e1a47a18adf70baf4b335998bfc10d4df98927e6878a556ef26825f83d10` — equal to `acceptanceCondition.expectedHash` ⇒ condition met.

**13.6 `VerificationResult` (PASS, complete, signed)**
```json
{
  "resultVersion": "adp-verification/0.1",
  "dealId": "8f14e45f-ceea-467e-9c99-2c8e3b6a1c1f",
  "acceptanceSpecHash": "a371ac92c8fae7e017d259ebeac4910b917a46ad029e35d16b4a4de12418633d",
  "deliveryHash": "5770e1a47a18adf70baf4b335998bfc10d4df98927e6878a556ef26825f83d10",
  "verifierId": "did:key:buyer-verifier-1",
  "result": "PASS",
  "evidenceRefs": [{"type": "delivery-hash", "hash": "5770e1a47a18adf70baf4b335998bfc10d4df98927e6878a556ef26825f83d10"}],
  "timestamp": "2026-09-22T10:04:12Z",
  "nonce": "a1e3f9c2-4b7d-4e21-9a10-000000000001",
  "signature": {"alg": "EdDSA", "kid": "did:key:buyer-verifier-1", "sig": "8ZqhcPOb4_tMGG84ovW4dcoisiLheH43LpN1X5Hc_HzR-SbHLI5Iam_9yihglyoYtxUvGX1ltCvrNhfzVd4ABQ"}
}
```
`verificationResultHash` (SHA-256 over the JCS without `signature`) = `f04cddf009898aa361d6c033925ecfc06a0f7bb7382d5720afb5bb0e610911af`

Check according to §5.1: (1) `dealId` agrees ✓ (2) `AcceptanceSpec` signature valid, hash equals the AP2 constraint ✓ (3) `deliveryHash` referenceable ✓ (4) `verifierId` == `verifierAuthorization.verifierKeyId` (checked **before** step 5, §4.5) ✓ (5) both signatures valid ✓ (6) `timestamp` within `validity` ✓ (7) not yet consumed ✓ ⇒ **release permitted.**

**13.7 x402 settlement (binding, excerpt)**
```json
{
  "scheme": "auth-capture",
  "extra": {"paymentFlow": "escrow", "captureDeadline": "2026-09-22T10:10:00Z", "dealId": "8f14e45f-ceea-467e-9c99-2c8e3b6a1c1f"},
  "settleAction": "capture",
  "settlementRuleCheck": "PASS-§5.1-satisfied"
}
```

**13.8 `DealRecord`**
```json
{
  "recordVersion": "adp-record/0.1",
  "dealId": "8f14e45f-ceea-467e-9c99-2c8e3b6a1c1f",
  "entries": [
    {"type": "a2a.artifact", "hash": "5770e1a47a18adf70baf4b335998bfc10d4df98927e6878a556ef26825f83d10"},
    {"type": "a2a.task", "hash": "9749c77a6ce453ed84e4c632473c1f2f2c8c508b40dd29554d4f0f758dbe705f"},
    {"type": "adp.acceptance_spec", "hash": "a371ac92c8fae7e017d259ebeac4910b917a46ad029e35d16b4a4de12418633d"},
    {"type": "adp.verification_result", "hash": "f04cddf009898aa361d6c033925ecfc06a0f7bb7382d5720afb5bb0e610911af"},
    {"type": "ap2.open_mandate", "hash": "a9471792f92278a53800b2858ab8f0f205dc9947fdb56d894d23dfed360616bf"},
    {"type": "x402.settlement", "hash": "bcd7b2ff52e703ec73de8603f71a0ccff8b5e41922107b7b35d966c561d22d5c"}
  ],
  "chainHash": "8690a4fa86ed8331bd54622a39212c6e46d2c7f1b5257a044ddeb516e9b9f7e2",
  "outcome": "SETTLED"
}
```
See §13.10 for the order, uniqueness and `chainHash` rule of `entries`.

**13.9 Negative test (one byte of the result changed)**
Delivery content changed: `{"totals": {"A": 120.5, "B": 44.1}}` (44.0 → 44.1). `deliveryHash` (tampered) = `5a8e3fc811819c2c0a14cfac0fd583f57c8fc2fd7ff62c925a6dadfc701444d6` — **not equal** to `expectedHash`.

`VerificationResult` (FAIL, complete, signed):
```json
{
  "resultVersion": "adp-verification/0.1",
  "dealId": "8f14e45f-ceea-467e-9c99-2c8e3b6a1c1f",
  "acceptanceSpecHash": "a371ac92c8fae7e017d259ebeac4910b917a46ad029e35d16b4a4de12418633d",
  "deliveryHash": "5a8e3fc811819c2c0a14cfac0fd583f57c8fc2fd7ff62c925a6dadfc701444d6",
  "verifierId": "did:key:buyer-verifier-1",
  "result": "FAIL",
  "evidenceRefs": [{"type": "delivery-hash", "hash": "5a8e3fc811819c2c0a14cfac0fd583f57c8fc2fd7ff62c925a6dadfc701444d6"}],
  "timestamp": "2026-09-22T10:04:12Z",
  "nonce": "a1e3f9c2-4b7d-4e21-9a10-000000000002",
  "signature": {"alg": "EdDSA", "kid": "did:key:buyer-verifier-1", "sig": "4pSx1t0FNjzKNHCxCPN2vq6I5-Dr7n4AeBufZgJWZPHdhxcCKUZuOyhDQtAq5ZHLexz4e1Z0Up3AgoL-VQCmDQ"}
}
```
`verificationResultHash` (FAIL) = `c530273dc816fa4ac9ba7fae1016f272b41a3c4b1d8a542e72a62f7237dbdc94`. According to §5.2: **no release**; the binding must trigger `void`/`refund`. State ⇒ `REJECTED`.

### 13.10 `entries` order, uniqueness and `chainHash` computation (normative)
1. `entries[]` MUST be sorted ascending by `type` (Unicode code point comparison) before the `chainHash` is computed — this makes the computation **deterministic regardless of the order in which a party collected the references**.
   * **1a. Uniqueness (erratum):** `entries[]` MUST contain **at most one** entry per `type`. Two entries with the same `type` MUST be treated as an invalid `DealRecord` (rejection, no `chainHash` computation). This rule makes item 1 a complete sort order that can be applied unambiguously — **no** secondary sort criterion (for example by `hash`) and **no** additional sequence field is needed. Reason: every entry type defined in the DealRecord section below (`adp.acceptance_spec`, `adp.verification_result`, `ap2.*` or `adp.owner_authorization`, `a2a.artifact`, optional `a2a.task`, optional `x402.settlement`/`erc8183.tx`) designates **the one object of its kind that is decisive for this deal** — for T1 and T2 each type occurs exactly once by construction; a second instance of the same type (for example a discarded intermediate delivery) does not belong in the final `DealRecord` of this deal.
2. `chainHash = fold(SHA-256, entries, seed = SHA-256(""))`: `acc₀ = SHA-256(b"")`; `accᵢ = SHA-256(accᵢ₋₁ ∥ bytes.fromhex(entries[i].hash))`; `chainHash = acc_n` (hex).
3. This computation **can be performed independently by every party** that possesses the same referenced objects (and thereby their hashes) — **without a `DealRecord` having to be exchanged between the parties** (see §13.11, "no second ledger"). With item 1a this independence is now **completely** guaranteed: two parties with the same referenced objects **always** produce the same `chainHash`, regardless of collection order and without a special case for equal types.

### 13.11 `DealRecord` (structure)
**Uniqueness.** See §13.10 item 1a: **at most one** entry per `type`, whether the type is mandatory or optional below.

**Mandatory entries** (`entries[]` MUST contain at least these, otherwise the record is incomplete in the sense of this specification):
* `adp.acceptance_spec` (hash of the `AcceptanceSpec`)
* `adp.verification_result` (hash of the decisive `VerificationResult`)
* an entry referencing the **owner authorisation**: a type with prefix `ap2.` (payment binding) **or** the type `adp.owner_authorization` (payment-neutral, §17.3)
* an entry referencing the **delivery** (type prefix `a2a.artifact` or equivalent)

**Optional entries:**
* `a2a.task` (transport context — useful but not mandatory for economic traceability, since `dealId` is already unique)
* `adp.provider_ack` (hash of the `providerAck` object; recommended in the payment-free profile)
* `x402.settlement` / `erc8183.tx` or similar (payment evidence — SHOULD be included when `outcome: SETTLED` under a payment binding, empty for `outcome: REJECTED` without a payment movement)

**Who may create it.** **Every party in possession of the referenced objects** — there is **no** distinguished "creating" party. This is the normative consequence of §13.10 item 3: since `chainHash` is a **pure function** of the (sorted) referenced hashes, two independent parties with the same objects produce **the same** `chainHash`, independently and without coordination.

**Must it be signed?** **No, not for v0.1 conformance.** The `chainHash` is already indirectly secured by the signatures of the referenced objects (`AcceptanceSpec`, `VerificationResult`): whoever checks these two and finds all referenced hashes correct can verify the `DealRecord` independently without the `DealRecord` itself being signed. An optional signature (`recordSignatures[]`, same envelope as §7.2) MAY be added by one or both parties as a "closing confirmation", but does not change cryptographic verifiability — it is pure convenience / finality marking. **Hence the `DealRecord` is not an exchanged protocol object in the narrow sense but a standardised, deterministically computed view of already existing, signed objects** (the scope reduction identified in phase 0.5, confirmed here).

**Independent reconstruction by an auditor.** An auditor who receives (a) the `AcceptanceSpec`, (b) the `VerificationResult`, (c) the delivery (or at least its hash) and (d) the owner authorisation (or at least its binding constraint, for example `x-adp.deal_reference`) can, **without any further communication with the parties**, establish:
* *What was agreed?* — from `subjectHash` (reference to the performance description) and, under a payment binding, the AP2 constraints (amount/payee).
* *Which acceptance rule applied?* — completely from the `AcceptanceSpec` (§3.2).
* *What was delivered?* — from `deliveryHash` plus the reference to the artifact.
* *Who verified?* — from `VerificationResult.verifierId` plus signature verification against `AcceptanceSpec.verifierAuthorization`.
* *Why was it released or not?* — from `VerificationResult.result` (`PASS`/`FAIL`) applied to the release rule (§5.1/5.2).

## 14. T2 — normative example (hidden test suite)

### 14.1 Advance binding of the test-suite hash (cryptographic, before execution)
```json
{
  "specVersion": "adp-acceptance/0.1",
  "dealId": "<dealId-2>",
  "subjectHash": "<hash of the functional specification>",
  "verificationMethod": {
    "type": "sandboxed-test-suite",
    "testSuiteHash": "<SHA-256 of the test-suite file, computed BEFORE execution>",
    "sandboxProfile": {"maxRuntimeSeconds": 30, "maxMemoryMB": 512, "network": "none"}
  },
  "acceptanceCondition": {"requiredExitCode": 0},
  "verifierAuthorization": {"mode": "designated-key", "verifierKeyId": "did:key:buyer-verifier-1", "verifierPubKey": "…"},
  "validity": {"notBefore": "…", "notAfter": "…"},
  "evidenceRequirements": ["delivery-hash", "test-execution-log-hash"],
  "issuer": "agent:buyer-a.example",
  "signature": {"alg": "EdDSA", "kid": "…", "sig": "…"}
}
```
**Key point:** the provider receives **only** `testSuiteHash`, never the test suite itself. Because `testSuiteHash` is part of the signed `AcceptanceSpec` (§3.5), the provider cannot later claim that a different test suite had been agreed — and the **buyer/verifier** cannot, after delivery, slip in a different (stricter or laxer) test suite without the hash no longer matching.

### 14.2 Flow after delivery
1. The provider delivers source code as an A2A `Artifact`; `deliveryHash` is computed and sent along (§10.3).
2. The verifier (key according to `verifierAuthorization`) loads **its own, locally held** test suite, computes `SHA-256(JCS-or-raw-file-of-the-test-suite)` and MUST check that this hash equals `AcceptanceSpec.verificationMethod.testSuiteHash` (self-check of the verifier — prevents the verifier from accidentally using a wrong/outdated test suite).
3. Execution in the sandbox according to `sandboxProfile` (no network, time/memory limit) against the delivered payload.
4. The exit code is compared with `requiredExitCode`.
5. The `VerificationResult` is created with `evidenceRefs` **including** `{"type": "test-execution-log-hash", "hash": "<SHA-256 of the complete execution log: stdout, stderr, exitCode, runtime>"}` (§4.7).

### 14.3 Protection against later exchange of the tests
* **By the provider:** impossible without a collision attack on SHA-256, because `testSuiteHash` is fixed before execution starts (§14.1) and the provider never receives the test suite against which it could "optimise".
* **By the verifier/buyer after delivery:** a change of the test suite actually executed would either (a) yield a different `testSuiteHash`, so that the self-check in §14.2 step 2 fails — the verifier must then issue **no** valid result for this `AcceptanceSpec` —, or (b) become traceable through the `test-execution-log-hash` evidence field, provided a third party gets access to the recorded execution log.
* **Residual risk:** if the verifier itself is manipulated (§15, "compromised verifier") — that is an identity/trust problem outside ADP (§7.3), not technically preventable by the protocol, only **detectable** if a third party independently possesses the test suite and recomputes the `testSuiteHash`.

## 15. Security / threat model (ADP-related only)

| # | Threat | Mitigation | Residual risk |
|---|---|---|---|
| 1 | Changing the `AcceptanceSpec` afterwards | signature + hash binding (§3.5, §11, §17.2); any change yields a different hash ⇒ `ACCEPTANCE_SPEC_MISMATCH` | none, as long as SHA-256/Ed25519 are not broken |
| 2 | Exchanging the delivery | `deliveryHash` is computed by the verifier **itself** from the delivery actually received, not asserted by the provider; the `VerificationResult` binds this self-computed hash | if the transport channel (A2A) itself is compromised — outside ADP scope |
| 3 | Forged `VerificationResult` | signature obligation (§7) against the key stored in `verifierAuthorization` | key compromise, see #11 |
| 4 | Unauthorised verifier issues a result | §4.5/§5.1(4): `verifierId` MUST equal `verifierAuthorization.verifierKeyId` exactly, otherwise `UNAUTHORIZED_VERIFIER` | none, provided the key assignment is resolved correctly (§7.3, outside ADP) |
| 5 | Replay of an old, valid `VerificationResult` | `nonce` unique per `(dealId, verifierId)` (§4.6); additionally one-time consumption per `(dealId, acceptanceSpecHash)` at release (§5.6) | none within the retention period of the stored nonces (implementation matter: the nonce history MUST be kept at least until `validity.notAfter`) |
| 6 | Double release (two releases for the same deal) | §5.6: binding-specific one-time-consumption state per `(dealId, acceptanceSpecHash)`, in addition to mechanisms the binding already has (x402: "not repeatable beyond maximum") | with two **independent**, uncoordinated adapters (for example two different bindings used in parallel for the same deal) — outside the v0.1 scope, SHOULD be avoided by contract design (one binding per deal) |
| 7 | Deal-ID collision | §2.3: local uniqueness check at every participant; UUIDv4 collision probability negligible | with deliberately forced collision by a party that controls both sides — then there is no genuine foreign deal anyway |
| 8 | Evidence manipulation (forged execution log in T2) | `test-execution-log-hash` is part of the signed `VerificationResult`; independent verification requires access to the log itself | ADP does not guarantee that the log is correct *in content*, only that it cannot be exchanged *afterwards* unnoticed without invalidating the signature — correctness of content is a matter of the verifier implementation (outside ADP) |
| 9 | Buyer refuses release despite a valid PASS | §5.1 states an **obligation** ("MUST … be permitted"), but ADP cannot enforce a binding execution if the buyer / its adapter simply does not implement the rule or deliberately ignores it | **Not completely solvable within ADP** — structurally a dispute (outside ADP scope by definition); mitigable only outside ADP (for example reputation consequences, legal recourse, or a binding whose release trigger is not pulled by the buyer but automatically by the adapter on a valid PASS — a recommendation, not an obligation) |
| 10 | Provider tries to produce a PASS itself | §3.4: `verifierAuthorization` excludes any key other than the named one from counting as valid; if the requester inadvertently chooses the provider's key as verifier, that is a **configuration decision outside ADP** (ADP only demands that some designated key exists — it does not technically forbid requester and verifier happening to be chosen identical to the provider; that would be an operating error of the requester, not a protocol error) | recommendation (non-normative): the requester SHOULD never set `verifierKeyId` equal to the known provider key |
| 11 | Compromised verifier (key stolen or verifier itself dishonest) | outside ADP's technical protection scope — ADP only ensures that **one** designated, checkable verifier existed and **exactly what** it attested (traceability), not that it told the truth | **high but limited**: a compromised verifier can issue false PASS/FAIL results; traceability (§4.4) makes this **detectable** afterwards (for example in T1 by recomputing the hash comparison), but ADP does not prevent it in real time — multiple/threshold verifiers would be a countermeasure but were deliberately not included for v0.1 in §3.4 |
| 12 | Forged or transplanted provider countersignature (payment-free profile) | §17.1: the countersignature must verify over exactly the issuer-signed body, must come from the provider key (not the issuer key) and is rejected otherwise | the provider's key must be resolved by the integrator (§7.3) |
| 13 | Release despite missing evidence | §18.1: required evidence is enforced before any release; the check precedes nonce registration | an authorised verifier can still fabricate well-formed evidence (see #11) |

## 16. Conformance test vectors

* **v0.1.1 vectors** (`conformance/ADP-v0.1.1-test-vectors.md` in the release repository; German): positive vectors P1–P4 and negative vectors N1–N10, with raw values and the exact generation method, including the keys reserved **solely for test purposes**. They remain valid and unchanged for v0.1.2.
* **v0.1.2 payment-free vectors** (`conformance/t3-payment-free-vectors.json` in the release repository): language-neutral JSON, generated deterministically (Ed25519 is deterministic, all inputs fixed), covering 26 release cases (S01–S24 including S14b and S16b) and 12 `DealRecord` cases (D01–D12). **Both** reference implementations run the same file and must produce the same decision, error code, reason prefix and `chainHash` for every case.
* **End-to-end scenario** (maintainers' internal reference implementations, not part of this publication): a payment-free agreement with 14 independent checks, 12 manipulations, replay and refusal scenarios, verified by two independent verifier implementations that must agree check by check.

## 17. The payment-free profile `adp-payment-free`

The profile is **not declared by a wire field**; it is a **validator policy** agreed between the participating parties (like key resolution, §7.3). This keeps all objects unchanged. A validator operating in this profile MUST apply the following.

### 17.1 Provider countersignature (mandatory in the profile)
A valid `providerAck` is mandatory and is verified *cryptographically and by content*:
* It MUST be a valid Ed25519 signature by the provider over **exactly the JCS body the issuer signed** (the spec without `signature` and `providerAck`). It is therefore bound to **this** agreement: a countersignature of another agreement, or an agreement that the issuer quietly changes and re-signs, fails.
* The provider's key is an **external input** (key resolution lies outside ADP, §7.3).
* The provider key MUST differ from the issuer key (a self-countersignature proves nothing).
* If the countersignature is missing, invalid, or does not match the agreement, the validator MUST reject (`INVALID_SIGNATURE`).
* `providerAck` does not change `acceptanceSpecHash` (§6).

### 17.2 Binding of `acceptanceSpecHash` without AP2
§3.5/§5.1(2) require an independently bound hash. In the profile this anchor is the **provider's countersignature** (§17.1), together with a hash the validator trusts from the transport (for example A2A task metadata) or from its own storage. The anchor is always an *external input* of the validator (`bound_acceptance_spec_hash`).

### 17.3 Authorisation entry in the `DealRecord`
The mandatory "owner authorisation" entry (§13.11) is satisfied by an entry with type prefix `ap2.` **or** the type `adp.owner_authorization`. Both kinds MAY occur together. Recommended optional entry: `adp.provider_ack`. `chainHash` computation, sorting, uniqueness per type and the `outcome` values are unchanged.

### 17.4 Security boundary of `adp.owner_authorization`
The entry is, like `ap2.*`, a **hash reference**: it binds an authorisation document kept by the issuer to the deal evidence. ADP checks neither content nor issuer of that document. The authenticity of the authorisation is a matter of the issuer's identity/authorisation layer (analogously to AP2). Auditors MUST be able to request the document for the hash and check that it was issued before `ACCEPTANCE_LOCKED`.

### 17.5 Unchanged
Signatures, verifier authorisation (`designated-key`), nonce uniqueness (§4.6), one-time consumption (§5.6), validity window, tamper protection through hash chains, error model §9.

### 17.6 Files (informative convention)
ADP canonicalises JSON, not binary files. For files (for example a spreadsheet) `subjectHash` (and, if needed, an evidence entry) binds the hash of a **JSON manifest**: `{"manifestVersion":"adp-file-manifest/0.1","files":[{"name":…,"sha256":<hex of the ORIGINAL bytes>,"size":<integer>}]}`. The manifest is canonicalised like any JSON (§6). ADP does not process the file content.

## 18. Changes in v0.1.2 relative to v0.1.1

### 18.1 Evidence enforcement (§4.7 made enforceable)
§4.7 was already a MUST; the v0.1.1 reference engine did not enforce it (it returned `ALLOWED` even with empty `evidenceRefs`). Before any release the validator MUST check:
1. Every type in `AcceptanceSpec.evidenceRequirements` is covered by at least one entry of `VerificationResult.evidenceRefs` of that `type`.
2. For `verificationMethod.type = "sandboxed-test-suite"` the type `test-execution-log-hash` is additionally required (§3.3/§4.7).
3. Every `evidenceRefs` entry MUST be `{type: non-empty string, hash: 64 lowercase hex characters}`.
4. An entry of type `delivery-hash` MUST equal `VerificationResult.deliveryHash`.
5. Additional, well-formed entries of other types are allowed.

On violation the decision is `DENIED` with a reason beginning `EVIDENCE_REQUIREMENTS_UNMET`. This is not a tenth error code (§9 stays at nine) but a refusal reason. The check runs **before** the nonce is registered, so that an incomplete result does not consume a nonce. The engine only returns the decision; state keeping remains with the caller; recommended (analogous to §5.2/§5.3): leave the deal open until a valid result exists or `validity.notAfter` expires (then `REJECTED`).

**Migration:** the reference engines offer an explicit `legacy-unchecked` evidence policy solely for migrating existing callers; the default is strict.

### 18.2 Payment-free profile and neutral wording
§1 (purpose), §1.2 (terminology), §13.11 (`adp.owner_authorization`), §17 (profile). No existing field, value or hash changes; existing AP2/x402/ERC-8183 records stay valid.

### 18.3 Not part of v0.1.2
New result levels in the signed `VerificationResult`, M-of-N verifiers, rework / partial-acceptance states, file processing / `byte-hash-equals`, a tenth error code, a wire field declaring the profile.

## 19. Responsibilities: what ADP does, and what the integrator must provide

| Concern | ADP provides | The integrating application MUST provide |
|---|---|---|
| Agreement terms | the `AcceptanceSpec` structure, its signature, hash and the rules for freezing it (§3) | the business content (what the job is, what counts as success), and a way to show the terms to both parties before locking |
| Transport | nothing (only an optional A2A binding description, §10) | message delivery between agents (HTTP, queue, A2A, MCP, files…), ordering, retries, delivery of the artifact itself |
| Identity | the `kid`/`issuer` references and the rule that unresolved keys fail as `INVALID_SIGNATURE` (§7.3) | mapping `kid` → public key from a source the *verifier* trusts (key directory, agent card, DID, prior contact); proof of who a party really is |
| Key management | Ed25519 signing/verification | key generation, secure storage, rotation, revocation, compromise handling; never reuse of test keys |
| Authorisation | a place to bind an authorisation (`ap2.*` or `adp.owner_authorization`, §13.11/§17.3) and a signed statement pattern in examples | who may authorise what, the authorisation document itself and its authenticity (ADP does not inspect it, §17.4) |
| Verification logic | the verdict object, evidence rules, and checks that a verdict is bound to the terms and the delivery | the actual checking (comparing hashes, running tests, human review…), the choice of verifier, and honesty of the verifier (§15 #11) |
| Release / follow-up | the release decision (`ALLOWED`/`DENIED`) and the closing record | performing the follow-up action (payment under a payment binding, hand-over, approval…), only after `ALLOWED`; reversal on `DENIED` |
| State | in-memory nonce and consumption state; an optional durable engine in the reference implementations (§20) | choosing durable storage for production, backup, and never marking a deal consumed before the release really happened (or using the claim/complete protocol of §20) |
| Time | the validity window and its comparison | trustworthy clocks and RFC 3339 timestamps |
| Records | deterministic `chainHash` construction and validation | storing records and artifacts, privacy of delivered content (ADP stores hashes only), retention |
| Disputes | nothing (§12.2: final) | any dispute, legal or arbitration process |

## 20. Implementation notes (informative)

* **Durable state.** Both reference implementations ship the in-memory engine of §5.6 and an *optional* SQLite-backed engine with the same decisions: nonce uniqueness, atomic claim of the one-time consumption (exactly one claimant wins, also across processes), and a two-phase `claim → complete` protocol so that a crash between claim and the real release leaves the deal *in doubt* (refused, never released twice) until an operator resolves it. Behaviour of the in-memory engines is unchanged.
* **Reference implementations** are the executable companion of this text; they are not normative. The test vectors (§16) are the arbiter.
* **Draft status.** No part of this specification has been agreed with third parties; interoperability claims are limited to the two reference implementations written inside one project.
