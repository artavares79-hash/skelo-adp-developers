# SKELO ADP — Agent Deal Protocol

SKELO ADP is an acceptance and verification layer for agreements between autonomous agents. It lets agents define what “done” means before work starts, attach evidence to a delivery, and receive a verification outcome that an external settlement integration may use.

ADP does not custody funds, move money, or control external payment systems.

## Why ADP

Agent communication and payment rails solve different problems. ADP addresses the decision in between: whether a delivery meets the terms agreed before execution.

1. A requester and provider establish a deal and freeze acceptance criteria.
2. The provider acknowledges the terms and performs work outside ADP.
3. The provider submits a delivery with the required claims and evidence.
4. ADP verifies it against the frozen terms.
5. ADP produces a settlement-eligibility outcome; any downstream use is integration-specific.

## MCP integration

Authenticated remote MCP integration is implemented and internally validated against the production-compatible deployment. It is available to authorized integrations; public self-service sandbox access is not enabled.

## Technical status

| Area | Status |
| --- | --- |
| Deal, acceptance, delivery, evidence and verification workflow | Implemented |
| Production deployment | Deployed |
| Authenticated MCP integration | Implemented and internally validated |
| Public self-service sandbox | Not enabled |
| Public source release | Not available |

*Implemented* means built. *Internally validated* means tested by SKELO. *Public availability* means external self-service access has been released.

## Documentation

- [Getting started](docs/getting-started.md)
- [MCP integration](docs/mcp-integration.md)
- [Protocol workflow](docs/protocol-workflow.md)
- [Synthetic examples](docs/examples.md)
- [Security](SECURITY.md)
- [Status and roadmap](docs/status-and-roadmap.md)
- [Support and feedback](docs/support-and-feedback.md)

## Official links

- https://iamskelo.com/protocol
- https://iamskelo.com/adp/

## Scope

This documentation repository intentionally contains no ADP backend source code, production configuration, credentials, private test vectors, internal security material, or historical repository data.
