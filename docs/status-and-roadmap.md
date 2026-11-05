# Status and roadmap

Current state of the protocol work:

| Area | Available today? |
|---|---|
| **ADP Protocol** | Specification v0.1.2 (draft) and test vectors published for reading and review; licence terms not yet decided. |
| **Reference implementations** (Python, TypeScript) | Full core implementations remain internal; selected Python primitives and the tested External Verifier V1 extension are now [published](../reference/README.md). |
| **External Verifier V1** | Implemented and tested in staging; public extension/docs/tests; hosted activation pending. |
| **Public MCP test sandbox** | **Live:** [no-auth test endpoint](https://iamskelo.com/adp/mcp-public) for synthetic deals. |
| **Protected MCP integration** | Deployed; requires authorization. |
| **Optional Evidence Replay anchor** | Isolated mechanism tested with synthetic data on Sui Testnet; not integrated into the production recorder. |
| **SKELO ADP Cloud** | **Planned. Not developed. Not available.** No date promised. |

## Hosted sandbox / MCP service

The public test endpoint is available without registration, API keys or OAuth. It has temporary isolated test deals, usage limits, and disabled external URL retrieval for verification. The protected production integration remains separate.

On 30 October 2026, SKELO successfully ran all five tools via a Claude Web connector with a synthetic PASS / ELIGIBLE deal. This was **SKELO's own integration test**, not independent third-party validation. The public [activity monitor](https://iamskelo.com/adp/activity) displays anonymized events; `unclassified` is not an external-user count.

## Capability table

| Capability | Implemented | Internally validated | Publicly available |
|---|---|---|---|
| Agreement and verification workflow | Yes | Yes | Specification and vectors (v0.1.2) |
| Payment-free profile | Yes | Yes | Specification and vectors |
| Authenticated remote MCP integration | Yes | Yes | Authorised integrations only |
| Public self-service MCP sandbox | Yes | Yes; Claude Web integration tested | Yes, synthetic tests only |
| Evidence Replay with optional Sui anchor | Yes, isolated build | Yes, synthetic Sui Testnet checks | Documentation and test transaction only; no production enrolment |
| External Verifier V1 | Yes, staging | 52 security + 98 regression checks; real OAuth/MCP client test | Extension code, schemas, client example and contract tests; no hosted activation |
| Independent second implementation | No | N/A | No |
| Reference transport / identity binding | No | N/A | No |
| Cloud platform | No | N/A | No |

## Direction (no dates, no commitments)

- External review of the specification and threat model; independent implementations.
- Reference bindings for transport and identity (for example `did:key`, A2A/HTTP).
- Publication of further materials once open questions are settled.
- Production review for recorder/witness operation, key custody, backup custody and retention before any Sui Mainnet decision.
