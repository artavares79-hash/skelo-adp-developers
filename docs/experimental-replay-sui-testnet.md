# Experimental Evidence Replay V1, Policy v5 and Sui Testnet anchoring

**Status:** isolated development / staging tests only; **not deployed to production**. This document reports information provided by the SKELO development team, not independently audited results. The experimental source code and complete test reports have not been published here.

## Version boundaries

- **ADP protocol specification:** public draft **v0.1.2**, unchanged.
- **Policy v5:** an implementation-level proposed verification-policy update for new deals; **not** a new protocol specification version. Intended to mark unsupported mandatory execution claims `NOT_VERIFIABLE` / `INCONCLUSIVE`, with a signed failing decision and no settlement eligibility. Existing signed historical records must remain immutable.
- **Evidence Replay V1:** isolated recorder, encrypted timeline, event hash chain, signed anchors, protected export, and independent offline-verifier prototype. This does not establish completeness of recording or factual correctness.
- **Sui anchoring:** experimental **Testnet** batching of replay anchors and related integrity commitments; no ADP token, proprietary blockchain, Mainnet deployment, or automatic production anchoring.

## Reported tests (private development workspaces)

| Scope | Reported result | Evidence availability |
|---|---|---|
| Evidence Replay initial synthetic tests | 72/72 | Private workspace; not independently reproduced here |
| Two-agent integration run | 81/81; 16 real MCP calls; 47 recorder events | Private workspace; both agents shared provider/account/host |
| Claude verification remediation | 112/112 regressions; four Claude deals and 22 tool calls; 109/109 follow-up checks | Private workspace; not published |
| Production-preflight follow-up | 50/50 integration and 7/7 package checks | Private workspace; production still NO-GO |
| Sui Testnet isolated workspace | 181 tests reported green (16 live, 7 batch, 34 logic, 52 blocker, 72 V1-copy) | Private workspace; not independently reproduced here |

The reported Sui Testnet batch transaction digest is:

```text
C44NYGHhZVZb4WciFYUSuuzqRqwruViVogLXX4GRthAa
```

The development report associates this digest with checkpoint `401258158` and a batched Merkle root covering replay anchors, witness receipts and backup/retention-related commitments. **This repository does not contain the source export, Merkle inclusion proofs or signed witness receipts required to independently verify those assertions.** A transaction digest alone does not prove that a specific replay export was anchored. Testnet transaction-history availability can also vary by endpoint.

## Verification requirements for a reproducible public demonstration

A future release should provide **sanitized, non-sensitive** fixtures, a versioned verifier, the precise canonicalization and hash/signature formats, signing public keys, an exported replay bundle, a transaction digest and checkpoint, and a Merkle inclusion proof binding the exported anchor to the on-chain root. A verifier should:

1. Validate event ordering, event hashes and signatures, and disclose any unobserved spans or `agent_asserted` events.
2. Independently recompute the bundle's commitment and Merkle proof.
3. Read the Sui **Testnet** commitment and confirm the digest/checkpoint against a trustworthy source, reporting unavailable history distinctly from verified success.
4. Reject changed, missing, reordered, replayed or locally re-signed data when it conflicts with the externally anchored commitment.
5. Never treat the presence of an anchor as proof of semantic truth, execution completeness, or legal liability.

**There is currently no public download in this repository for the experimental offline verifier, and no claim that the public MCP endpoint exposes replay export or anchoring tools.** Do not attempt to test these features through the existing public MCP tools until a supported interface is explicitly published.

## Production blockers and release criteria

The team's latest preflight remained **NO-GO**. Outstanding work includes an actual LocalSystem service-account key test, independently operated production recorder/witness, off-host backup custody with a real restore test, approved retention values, and a production fix for an unsafe public-sandbox 24-hour deletion rule. Three historical public test deals were reported missing and found in checkpoints; no reconstruction or production hotfix deployment was reported at that stage.

No release, live endpoint, production key, Mainnet funding or automatic anchoring should be inferred from successful Testnet experiments. A production release requires documented authorization, security review, backup/retention decisions, and fresh integration verification.

## Useful references

- [Current public protocol specification](../spec/ADP-v0.1.2-EN.md)
- [MCP integration](mcp-integration.md)
- [Sui network documentation](https://docs.sui.io/develop/sui-architecture/networks)
