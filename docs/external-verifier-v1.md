# External Verifier V1 — implemented staging integration

**Published snapshot: v1-staging-2026-11-05.** Implementation and reference checks are public. The protected hosted External Verifier API/tool, TEST profile, production Policy v5, production Evidence Replay and Sui publisher have **not** been activated by this publication. Do not send the new tool to the public sandbox and expect it to exist. The existing five public tools and protected OAuth integration remain separate.

This is an opt-in **application profile**, `adp.external-verifier/1`, with settlement policy `adp.external-verifier.settlement/1`; it does not revise the v0.1.2 draft specification or rewrite historical agreements. A new deal freezes a designated approved Ed25519 verifier and mandatory professional scope before delivery. ADP checks the specialist's signed attestation; it does not implement finance, insurance, software or research expertise in the core.

## What is implemented

- Operator-controlled verifier allowlist with public key, allowed scope IDs, and separate creator/verifier OAuth grant roles. Arbitrary client-supplied trust roots are rejected.
- Authenticated MCP `adp_submit_verification` and operator-only REST submission, full deal/spec/delivery binding, existing Ed25519 VerificationResult, nonce protection and immutable delivery.
- One hash-bound structured evidence artifact for each frozen criterion, with signed PASS / FAIL / NOT_VERIFIABLE status. No confidence score substitutes for evidence.
- Combined structural/professional release gate, current registry and validity checks, signed `adp.external-gate/1` application receipt.
- Missing/negative/contradictory/invalid evidence never permits release. Canonical identical retry is idempotent; same nonce on a different result is replay; any distinct second valid result latches CONFLICT. No in-place FAIL-to-PASS replacement.
- TEST OAuth profile `adp.test-verifier/1`: explicit server role marker, tool allowlist and pinned synthetic deal IDs/spec/delivery hashes checked again on the actual REST operation. No TEST creation/delivery/admin permissions or direct REST access.

## Endpoint and authentication boundaries

| Surface | Existing hosted availability | V1 candidate use |
|---|---|---|
| [`/adp/mcp-public`](https://iamskelo.com/adp/mcp-public) | Five public synthetic-sandbox tools, no login | No external-review access or new submission tool |
| [`/adp/mcp`](https://iamskelo.com/adp/mcp) | Protected MCP / existing OAuth | After separate activation, authorized external-review tools |
| [`/adp/connect.html`](https://iamskelo.com/adp/connect.html) | Integration information | Enrollment/contact information; no public self-enrollment |
| `/api/playground/external/deals/...` | Existing operator-authenticated API family | Candidate additions documented in OpenAPI; TEST OAuth credentials are denied on direct REST |

Paths in the [OpenAPI contract](../schemas/external-verifier-v1.openapi.json) are backend-relative. The existing website proxy adds `/adp`; no new routing is required by the candidate. The [MCP schema snapshot](../schemas/external-verifier-v1-mcp.json) is extracted from the tested adapter, not claimed as the currently deployed tool list.

An ordinary approved creator may create/acknowledge/deliver its own external-profile deals; the designated review grant may read and submit results. The legacy static REST token is an operator credential and must never be handed to an external or TEST specialist. Normal client behavior is preserved. A valid OAuth token alone is not a TEST authorization.

## New agreement and delivery

Authenticated creation uses existing `request` and structural `criteria` plus:

```json
{
  "externalVerifier": {
    "verifierId": "approved-specialist-v1",
    "publicKey": "OPERATOR_APPROVED_BASE64URL_ED25519_PUBLIC_KEY",
    "scope": [{"id": "invoice-total", "description": "The synthetic invoice total must equal the agreed EUR 200."}]
  }
}
```

The placeholder key is intentionally unusable. The operator resolves/verifies the real specialist identity, key possession and permitted criteria independently. Scope contains 1–10 unique ordered entries; put mandatory specialist requirements there, not only in request prose. Existing legacy semantic claims/customRequirement are not mixed into this profile.

Read back `signedAcceptanceSpec`, the full `acceptanceSpecHashFull` and `verificationSettlementPolicy.policyHash`; acknowledge both exact bindings with the existing acknowledgment tool. The deployed application's ACK is its signed application receipt of the authenticated provider acknowledgment, not a claim that an external provider supplied its own separate private-key signature. This reference subset is not a claim of full normative v0.1.2 conformance.

Submit the first delivery once. It becomes immutable. Read `canonicalDelivery` and `deliveryHashFull`; normalizers may escape/truncate input. Sign **the returned full canonical hash**, not an input hash, truncated UI hash or timestamp guessed by the client. `delivery.sources` retains `{name,url}` objects; malformed formats fail early. Existing request size limit is 16 KiB.

## Sign and submit the external result

The existing core wire version is `adp-verification/0.1`. Required fields are `resultVersion`, `dealId`, `acceptanceSpecHash`, `deliveryHash`, `verifierId`, `result`, `evidenceRefs`, `timestamp`, `nonce`, plus the signature envelope. Exact input properties are in the published JSON schema.

For every frozen criterion, in scope order:

```json
{
  "evidenceRefs": [{"criterionId":"invoice-total","status":"PASS","evidenceHash":"SHA256_OF_ADP_CANONICAL_ARTIFACT"}],
  "evidence": [{"criterionId":"invoice-total","artifact":{"synthetic":true,"observedAmount":200,"expectedAmount":200}}]
}
```

`evidenceRefs` is inside the signed VerificationResult; artifacts accompany it. `evidenceHash` uses the existing ADP `object_hash`. All mandatory criterion statuses PASS yields core PASS; any FAIL or NOT_VERIFIABLE yields core FAIL, while the application preserves the richer professional state. Signature envelope: canonical unpadded base64url `{alg:"EdDSA",kid:<frozen verifierId>,sig:<64-byte Ed25519 signature>}`. Timestamp must be in agreement validity and not more than 60 seconds ahead of server time; use a new nonce for a distinct signed result.

Call:

```text
MCP adp_submit_verification:
  {deal_id, verification_result, evidence}
Operator REST POST /api/playground/external/deals/{deal_id}/verification:
  {verificationResult, evidence}
```

The [Python example](../examples/python/external_verifier_client.py) builds that exact envelope from the returned signed agreement/canonical delivery and a caller-held signing object. It accepts a pre-authorized OAuth access token in memory; it never needs the operator credential or a committed private key. OAuth enrollment uses existing discovery, consent/access code, Authorization Code + PKCE-S256 and callback/state validation. TEST grants must be locally classified before token issuance. Token scope text or client headers cannot grant extra privileges.

## Decision matrix

| Evidence/conditions | Professional status | Final result | Gate |
|---|---|---|---|
| No specialist report | NOT_VERIFIABLE | INCONCLUSIVE | DENIED / NOT ELIGIBLE |
| Mandatory criterion FAIL | FAIL | FAIL | DENIED / NOT ELIGIBLE |
| Mandatory criterion NOT_VERIFIABLE | NOT_VERIFIABLE | INCONCLUSIVE | DENIED / NOT ELIGIBLE |
| Second distinct valid signed result | CONFLICT | INCONCLUSIVE unless structure fails | DENIED / NOT ELIGIBLE |
| All specialist criteria and structure PASS, current authorization/validity/integrity intact | PASS | PASS | ALLOWED / ELIGIBLE |
| Invalid signature/binding/evidence | Reject submission; no new trusted result | No forged PASS | Never release on the rejected submission |

Structural FAIL remains FAIL and blocks even a valid specialist PASS. HTTP 200 indicates transport success, not professional PASS. Inspect `structuralStatus`, `professionalStatus`, `finalResult`, `settlementDecision`, `settlementStatus`, `withinValidity`, `verifierCurrentlyAuthorized`, `evidenceIntegrityValid`, and the signed decision receipt. Pin the known operator gate public key independently; do not trust a key merely because a response includes it. The current combined gate, not an isolated external PASS, is the release input.

Invalid forged negative reports do not overwrite a previously valid result; only independently valid distinct signatures create a conflict. Re-review requires a newly acknowledged linked deal with `supersedesDealId` and genuinely changed canonical delivery. Changed ignored fields/server timestamps/truncated-away text are insufficient. Historical agreements, policies and signatures remain intact.

## TEST profile and permission enforcement

The operator creates new synthetic test agreements with `syntheticTest: true`. The server freezes `{version:"adp.synthetic-test/1",synthetic:true,settlement:"TEST_ONLY_NO_PAYMENT"}` into the signed external-verifier binding. Clients cannot retrofit this into old signed deals. The operator separately pins approved deal IDs and exact spec/delivery hashes in a private `ADP_TEST_VERIFIER_POLICY_PATH` file. Server verification proves these bindings and operator authorization, not that arbitrary text is semantically synthetic; selection of approved data is the operator's responsibility.

For a fresh unused OAuth grant, the local-only `register_test_grant(grant_id, verifier_id)` helper writes `test_verifier_grant_profiles`; there is no HTTP enrollment endpoint. Missing/disabled/malformed policy never downgrades a marked TEST principal to legacy rights. Allowed tools are a server-configured subset of `adp_read_deal`, `adp_get_verification`, `adp_submit_verification`; `apiActions` must be `[]`. TEST credentials on direct REST, alternate MCP, demo or legacy operations are denied. The internal bridge uses 20-second, single-use credentials bound to method/path/body/deal/tool and original OAuth grant, checked on both sides. Refresh retains the server grant classification; revocation is checked again before execution.

Both registry and policy are private operator-controlled configuration, not public data. No real IDs, keys or active configurations are provided here. A policy skeleton is `{version:1,enabled:false,grants:{},deals:{}}`. Per-grant entries require exactly `enabled`, `profile`, `verifierId`, `publicKey`, `tools`, `apiActions`, `dealIds`; per-deal entries exactly `synthetic`, `acceptanceSpecHash`, `deliveryHash`. Registry TEST entries use `testOnly:true` plus existing approved key/scope/role fields. See [host contracts](../reference/README.md).

Before any TEST grant exists an old executable may be restored under a controlled rollout. Once marked grants exist, keep the profile table and guards: disable new TEST activity and make a forward fix. An older executable that ignores this gate is not a safe rollback. Never erase existing customer state to roll back code.

## Validation, limits and availability

Staging evidence: 52 authorization/security checks and 98 existing regression checks passed. A separate same-host client performed full real OAuth/PKCE, 32 MCP calls (28 tools), 24 operator API calls and 42 client checks: PASS/ALLOWED, FAIL/DENIED, NOT_VERIFIABLE/DENIED, CONFLICT/DENIED and manipulated-signature/binding rejection. Three ordinary MCP compatibility calls confirmed the pre-existing synthetic control deal unchanged. These are operator-run tests using synthetic data, not an external professional audit. No private run paths, grant IDs, test keys, real customer data or raw operational traces are published.

The publication passed 45 portable contract tests of the actual extension and client example with a synthetic host fixture. They are not a substitute for the separately executed full staging HTTP test. A [sanitized validation summary](external-verifier-v1-validation.json) records test counts and boundaries without operational identifiers. No complete private server or OS-specific key provisioning is bundled. Single-service-process concurrency is covered; multi-host/worker operation is not released. Canonicalization is the existing limited-number/BMP-key reference scope, documented in its source; this is not a new general-purpose JCS implementation.

A valid signature proves who attested to a bound result, not factual truth or independent execution. Vet specialists and keep signing keys outside ADP. Independent expert review, production onboarding/approval and external backup custody remain operational responsibilities. No payment rails, wallets, Sui Mainnet transactions, productive Sui publisher, Policy v5 or production Evidence Replay are activated by GitHub publication. Existing repository license/usage terms are unchanged.
