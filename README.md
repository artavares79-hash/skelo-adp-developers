# SKELO ADP
### Agent Deal Protocol

**Clear terms. Evidence-backed delivery. Verifiable outcomes.**

AI agents can message each other. They can delegate tasks. They can trigger payments. But **who determines whether the promised work was actually delivered as agreed?**

SKELO ADP focuses on that missing decision: a structured agreement-and-verification workflow between autonomous agents.

> **The idea:** Define what “done” means *before* work starts. Submit a delivery with the agreed evidence. Evaluate it against the terms that were fixed at the start.

**Current status:** Agreement and verification workflow implemented · Production deployment in place · Authenticated remote MCP integration implemented and internally validated · **Access by approval only**

[Explore the protocol](https://iamskelo.com/protocol) · [See the ADP walkthrough](https://iamskelo.com/adp/) · [Read the MCP guide](docs/mcp-integration.md) · [Integration information](https://iamskelo.com/adp/connect.html)

---

## The problem: “Done” is not the same as “accepted”

Imagine two AI agents:

- **Requester:** “Write a short research brief with three sections and cited sources.”
- **Provider:** “Done — here is the brief.”

The response arrived. But were all three sections present? Were the requested citations supplied? Was the agreed format followed?

Without shared acceptance criteria, the requester is left to interpret what “done” means *after* delivery.

**ADP makes the acceptance terms explicit before execution and provides a defined verification outcome afterward.** It does not promise to determine universal factual truth or guarantee work quality beyond the checks agreed for a particular deal.

## Where ADP fits

| Layer | What it answers |
| --- | --- |
| Agent communication | “What did the agents say?” |
| **SKELO ADP** | **“Did this delivery satisfy the previously agreed checks?”** |
| Payment or downstream workflow | “What action should happen next?” |

ADP is **not** a payment processor, escrow service, autonomous worker, or general-purpose truth oracle. It does not hold funds or initiate transfers. An external system decides whether and how to use its verification result.

## From agreement to outcome

~~~mermaid
flowchart LR
  A["Requester and provider<br/>define the deal"] --> B["Fix acceptance<br/>criteria"]
  B --> C["Provider<br/>acknowledges"]
  C --> D["Work happens<br/>outside ADP"]
  D --> E["Delivery +<br/>evidence"]
  E --> F["ADP evaluates against<br/>agreed criteria"]
  F --> G["Verification outcome"]
  G --> H["External system decides<br/>what happens next"]
~~~

1. **Agree:** Define the deliverable and explicit acceptance criteria.
2. **Fix the terms:** Establish the checks before execution, rather than changing them after delivery.
3. **Acknowledge:** The provider accepts the agreed terms.
4. **Deliver:** The provider performs the work externally and supplies delivery claims and evidence.
5. **Verify:** ADP evaluates the submission against the fixed criteria.
6. **Decide:** A separate integration may use the outcome to inform its own workflow.

[See the complete workflow](docs/protocol-workflow.md) · [Walk through synthetic examples](docs/examples.md)

## Where it could be useful

**Deep dive:** [AI agents can say “done.” Who checks the delivery?](docs/why-agent-delivery-verification-matters.md) — a technical explainer on acceptance criteria, evidence and verification boundaries.

**Multi-agent research** — One agent requests a brief from another, with required sections, references and format defined in advance.

**AI-assisted content production** — A requester specifies expected assets, language and delivery structure before another agent submits work.

**Structured data handoffs** — One agent requests a defined set of fields or evidence from a second agent; the receiving workflow checks the agreed submission requirements.

These are *illustrative use cases*, not claims of existing customer integrations or guarantees that subjective quality and source truth are automatically verified.

[Explore use cases](docs/use-cases.md)

## What is ready today?

| Capability | Current state |
| --- | --- |
| Agreement, delivery, evidence and verification workflow | Implemented and internally validated |
| Production-compatible deployment | Deployed |
| Authenticated remote MCP integration | Implemented and internally validated |
| Access for external integrations | **Controlled; authorization required** |
| Public self-service sandbox | **Not enabled** |
| Public ADP source-code release | **Not available** |

MCP allows an authorized compatible client to discover and invoke the ADP tools exposed to its session. This repository does **not** provide public credentials, unapproved tool schemas, or a copy of the backend.

**Built and internally validated is not the same as publicly open.** No public self-service endpoint or instant account creation is promised.

## Interested in evaluating ADP?

**Developing an MCP-capable agent or a multi-agent workflow?** [Join the open discussion on verifiable agent delivery](https://github.com/artavares79-hash/skelo-adp-developers/issues/1). We are gathering concrete synthetic use cases and independent technical feedback.

**Interested in testing ADP with your own agents?** [Request a controlled evaluation on GitHub](https://github.com/artavares79-hash/skelo-adp-developers/issues/new?template=integration-interest.yml) or consult the [official integration information](https://iamskelo.com/adp/connect.html).

GitHub requests are visible to other users after the repository is published. Do not include confidential information, tokens, personal contact data or private endpoints. Requests are reviewed individually; no automatic access or response time is promised.

1. Start with the [plain-language walkthrough](https://iamskelo.com/adp/) and [synthetic examples](docs/examples.md).
2. Read [Getting started](docs/getting-started.md), the [MCP integration overview](docs/mcp-integration.md), and the [security notes](SECURITY.md).
3. Review the [official integration information](https://iamskelo.com/adp/connect.html) for the currently available contact/access route.
4. If evaluation access is approved, use the connection instructions provided privately and **test with synthetic data first**.

No public sign-up or instant sandbox access is currently offered.

## Documentation

| Start here | What you will find |
| --- | --- |
| [Getting started](docs/getting-started.md) | How to assess fit and request authorized access |
| [Use cases](docs/use-cases.md) | Scenarios showing the problem ADP addresses |
| [Synthetic examples](docs/examples.md) | A concrete pass/fail walkthrough, **not** executable API requests |
| [Protocol workflow](docs/protocol-workflow.md) | The seven-step agreement-to-outcome flow |
| [MCP integration](docs/mcp-integration.md) | What MCP enables and what remains access-controlled |
| [Frequently asked questions](docs/faq.md) | Clear answers on access, trust, source code and payments |
| [Security](SECURITY.md) | Integration responsibilities and vulnerability reporting |
| [Status and roadmap](docs/status-and-roadmap.md) | Implemented vs. validated vs. publicly available |
| [Support and feedback](docs/support-and-feedback.md) | Contact and documentation feedback paths |

## About this repository

This is the **documentation home** for SKELO ADP. The ADP backend and security implementation remain proprietary and are **not included** here. Documentation is not an open-source release of the protocol implementation.

**Official website:** [iamskelo.com/protocol](https://iamskelo.com/protocol)

---

**SKELO ADP — Define the deal. Check the delivery. Keep the decision explicit.**
