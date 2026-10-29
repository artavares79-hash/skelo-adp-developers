# Changelog

Changes to the specification. Versioning rules: [`docs/versioning-policy.md`](docs/versioning-policy.md).

## [0.1.2] - draft
- First **English normative text** (`spec/ADP-v0.1.2-EN.md`), consolidating v0.1.1 and the v0.1.2 changes. No semantic change relative to v0.1.1; all example hashes and signatures are byte-identical to the German source.
- **Evidence enforcement** made enforceable (§4.7 / §18.1): missing or malformed required evidence yields `DENIED` with reason `EVIDENCE_REQUIREMENTS_UNMET`. *Potentially breaking for callers that signed verdicts without evidence.*
- **Payment-free profile** `adp-payment-free` (§17): mandatory valid provider countersignature; `adp.owner_authorization` record entry as an alternative to `ap2.*`. A validator policy, not a wire field.
- Neutral wording: payments are optional bindings, not a prerequisite.
- Responsibilities of integrators (§19) and implementation notes (§20).
- Language-neutral payment-free test vectors (`conformance/t3-payment-free-vectors.json`).

## [0.1.1]
Frozen v0.1.1 specification with the v0.1 errata and 14 conformance vectors (German text).
