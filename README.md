# SKELO ADP
### Agent Deal Protocol

**Agree before execution. Freeze the terms. Verify before release.**

An AI agent can promise a result, report “done” and even trigger a downstream action. But who establishes **what counts as an acceptable delivery before the work starts** — and prevents the goalposts from changing afterward?

**SKELO Agent Deal Protocol (ADP)** is a pre-execution agreement and verification layer for autonomous-agent handoffs. It creates a signed, deal-bound acceptance specification; binds the provider's acknowledgement to the exact specification **and** verification policy; evaluates the later delivery and evidence against those frozen terms; and returns a settlement-eligibility outcome for an external system to use.

> **The distinction:** ADP is **not merely a check added after the result arrives**. Its agreement, acceptance criteria and provider commitment are bound **before** the delivery is accepted. A mismatch between the agreed specification and the submitted delivery is not silently accepted.

**Current status:** Agreement and verification workflow implemented · Production deployment in place · Authenticated remote MCP integration implemented and internally validated · **Access by approval only**

[Explore the protocol](https://iamskelo.com/protocol) · [See the ADP walkthrough](https://iamskelo.com/adp/) · [Read the MCP guide](docs/mcp-integration.md) · [Integration information](https://iamskelo.com/adp/connect.html)

---

## The problem: acceptance cannot be defined after delivery

Imagine a requester agent commissioning a research brief from a provider agent.

- **Before work:** The requester specifies three required sections, an output language, evidence requirements and objective acceptance checks. ADP binds the deal to a signed acceptance specification and a defined verification policy. The provider acknowledges those exact terms.
- **During work:** The provider produces the brief outside ADP.
- **At delivery:** The submitted result is matched to the original deal and frozen specification. ADP checks the agreed requirements and evidence, then returns a signed verification outcome.
- **After verification:** The integrating workflow decides whether to accept, request correction, or authorize an external follow-up action. ADP does not execute or force that action.

**Why this matters:** Neither side should be able to silently substitute new acceptance rules when the result is already on the table. ADP makes the agreed basis for the decision explicit, linked to the particular deal and inspectable.

## Where ADP fits

| Layer | Its role |
| --- | --- |
| Agent communication / orchestration | Agents discover each other, delegate and execute work |
| **ADP: before execution** | **Bind deal, signed acceptance specification, verification policy and provider acknowledgement** |
| **ADP: at delivery** | **Match the delivery to the original terms; evaluate criteria and configured claim/evidence checks** |
| **ADP: after verification** | **Produce a verification and settlement-eligibility outcome** |
| External workflow / payment system | Validate and enforce its own acceptance, release or payment action |

ADP is **not** a payment rail, escrow provider, identity authority, autonomous worker or general-purpose truth oracle. A workflow must explicitly use the ADP outcome to enforce a release gate; ADP cannot block an external action that bypasses this integration. Eligibility is **not** proof that every underlying factual claim is true.

## From agreement to outcome

~~~mermaid
flowchart LR
  A["Deal + explicit acceptance checks"] --> B["Signed spec + policy bound before work"]
  B --> C["Provider ACK: exact spec + policy"]
  C --> D["Work executed outside ADP"]
  D --> E["Delivery tied to original terms + evidence"]
  E --> F["Verification + signed outcome"]
  F --> G["Eligibility decision"]
  G --> H["External system chooses and enforces any action"]
~~~

1. **Agree first:** Specify a deal, explicit acceptance criteria, verification policy and required evidence before the work begins.
2. **Freeze and acknowledge:** ADP signs and binds the acceptance specification and policy to the deal. The provider acknowledges those exact terms; a delivery without a valid acknowledgement is rejected.
3. **Execute externally:** The provider performs the task outside ADP.
4. **Deliver against the original deal:** The submission must identify the expected frozen specification; mismatches are rejected.
5. **Verify:** ADP applies the established structural and, when configured, claim/evidence checks; it also distinguishes outcomes that cannot be objectively verified.
6. **Return eligibility:** ADP issues a signed verification result and eligibility outcome. **The integrating system** remains responsible for any release, settlement or payment decision.

[See the complete workflow](docs/protocol-workflow.md) · [Walk through synthetic examples](docs/examples.md)

## Where it could be useful

**See six concrete integration concepts involving existing platforms:** [n8n, LangGraph, GitHub Actions, Zendesk, Shopify Flow and HubSpot](docs/real-world-integration-opportunities.md). Each scenario separates features these products already offer from proposed ADP integration work; no vendor partnerships or ready-made adapters are claimed.

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
| [Real-world integration opportunities](docs/real-world-integration-opportunities.md) | Six specific examples using existing AI and automation platforms |
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

**SKELO ADP — Agree first. Freeze the terms. Verify before release.**
