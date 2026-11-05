# Changelog

Changes to the specification. Versioning rules: [`docs/versioning-policy.md`](docs/versioning-policy.md).

## External Verifier V1 application snapshot — 2026-11-05

- Publish actual tested application modules, selected existing crypto/binding primitives, host contracts and portable contract tests. This does not claim full core-v0.1.2 reference conformance.
- New-deal approved verifier/scope binding, signed external results/evidence, fail-closed combined gate, immutable conflict history and replay protection.
- Server-side TEST grant profiles and tool/deal/hash allowlists; direct REST denied; one-use scoped internal MCP bridge.
- Exact candidate MCP/OpenAPI contracts and safe Python client example. Hosted production remains unchanged; public sandbox still has five tools.
- Specification and signed wire versions remain unchanged. Production Policy v5, Evidence Replay, Sui publishing and payments are not enabled. No existing deals are migrated.

## [0.1.2] - draft
- First **English normative text** (`spec/ADP-v0.1.2-EN.md`), consolidating v0.1.1 and the v0.1.2 changes. No semantic change relative to v0.1.1; all example hashes and signatures are byte-identical to the German source.
- **Evidence enforcement** made enforceable (§4.7 / §18.1): missing or malformed required evidence yields `DENIED` with reason `EVIDENCE_REQUIREMENTS_UNMET`. *Potentially breaking for callers that signed verdicts without evidence.*
- **Payment-free profile** `adp-payment-free` (§17): mandatory valid provider countersignature; `adp.owner_authorization` record entry as an alternative to `ap2.*`. A validator policy, not a wire field.
- Neutral wording: payments are optional bindings, not a prerequisite.
- Responsibilities of integrators (§19) and implementation notes (§20).
- Language-neutral payment-free test vectors (`conformance/t3-payment-free-vectors.json`).

## [0.1.1]
Frozen v0.1.1 specification with the v0.1 errata and 14 conformance vectors (German text).
