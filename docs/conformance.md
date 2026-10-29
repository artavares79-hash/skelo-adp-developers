# Conformance and compatibility

This page tells an implementer how to check that their software behaves like ADP v0.1.2, and what the repository itself tests.

## 1. Test material in this repository
| Material | Location | Content |
|---|---|---|
| v0.1.1 vectors (German text, unchanged values) | [`conformance/ADP-v0.1.1-test-vectors.md`](../conformance/ADP-v0.1.1-test-vectors.md) | canonicalisation, hashes, signatures: positive P1–P4, negative N1–N10 with raw values and the keys reserved for tests |
| v0.1.2 payment-free vectors (language neutral) | [`conformance/t3-payment-free-vectors.json`](../conformance/t3-payment-free-vectors.json) | 26 release cases (`settlementCases`, S01–S24 incl. S14b, S16b) and 12 `DealRecord` cases (`dealRecordCases`, D01–D12); fixed test keys in `keys`; deterministic |
| Worked examples in the specification | spec §13, §14 | T1/T2 objects with their hashes and signatures |

The test keys in these files are **public and insecure by design**.

## 2. How an independent implementation should use them
1. Implement RFC 8785 canonicalisation (integers only — reject floats) and SHA-256; reproduce the hashes in spec §13/§14 and the P1–P4/N1–N10 vectors.
2. Implement Ed25519 signing/verification over the canonical bytes (spec §7); Ed25519 is deterministic, so signatures in the vectors must match byte for byte.
3. Run every case of `t3-payment-free-vectors.json`: feed the listed inputs to your release evaluation / record builder and compare **decision, error code and reason prefix** with the expected values.

## 3. Claiming conformance
No conformance rule, certification programme or badge exists yet. Do not imply SKELO's endorsement of an implementation.

## 4. Cross-language compatibility actually tested
* The maintainers' two reference implementations (Python, TypeScript; not part of this publication) pass the same `t3-payment-free-vectors.json`, and each verifies the other's output.
* **Not tested:** any third-party implementation; mixed v0.1.1/v0.1.2 deployments beyond the shared vectors.
