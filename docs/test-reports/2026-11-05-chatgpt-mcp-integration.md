# SKELO ADP – ChatGPT MCP integration test (2026-11-05)

## Result: PASS — existing public MCP workflow

An external ChatGPT client used the connected SKELO ADP MCP tools to execute a **synthetic** German-language invoice-check demonstration. This is a record of actual tool responses, not a test plan.

- Deal ID: `fb3cb3ea-4d87-4956-98ab-f7b150965354`
- Test input: entirely fictional invoice for EUR 200; no real invoice, personal data, or payments
- Frozen acceptance criteria: 3 delivery items, German output, no source requirement, no evidence claims
- Final result: `PASS`
- Settlement status: `ELIGIBLE` (policy eligibility only; **no payment executed**)

### Observed MCP operations

| Tool | Actual response |
| --- | --- |
| `adp_create_deal` | `AWAITING_ACCEPTANCE`; frozen acceptance specification and policy hashes returned |
| `adp_acknowledge_deal` | `ok: true`, `dealState: ACCEPTED` |
| `adp_submit_delivery` | `state: DELIVERED` |
| `adp_get_verification` | `state: PASS`, `finalResult: PASS`, `settlementStatus: ELIGIBLE` |

One initial `adp_submit_delivery` invocation was rejected by tool argument validation because `provider_name` was omitted. The corrected invocation succeeded.

The verification response listed four successful checks:
- `acceptanceSpecHashUnchanged` — `PASS` / `OBJECTIVE_VERIFIED`
- `signatureValid` — `PASS` / `OBJECTIVE_VERIFIED` (Ed25519)
- `itemCount` — `PASS` / `STRUCTURAL_VERIFIED`
- `outputLanguageMatches` — `PASS` / `STRUCTURAL_VERIFIED`

### Scope and limitations

This test demonstrates that **ChatGPT, acting as an external MCP client**, can complete the existing sandbox deal lifecycle using the connected ADP tools. It does **not** establish that a genuine invoice was independently examined or that its economic claims are true. No independent subject-matter verifier was used.

It does **not** test the newly developed **External Verifier V1** submission path, protected verifier OAuth scopes, public TLS access to that protected verifier path, or a Claude client. The connector exposed only the five existing sandbox tools: create, read, acknowledge, submit, and get verification.

External Verifier V1 remains **staging-tested**, not production-released. Production deployment requires separate explicit approval and completion of operational safeguards, including off-host backup custody.

This report is documentation only. It does not authorize deployment, payment, key changes, or changes to existing production deals.
