# AI agents can say “done.” But what did they agree to deliver?

**The case for binding acceptance terms before execution — then verifying delivery before downstream release.**

AI agents are getting better at delegating tasks. One agent can ask another to summarize a document, prepare research, transform data or generate a report. The provider agent can send back an answer that says the work is complete.

But a reply is not an acceptance test.

The harder question is: **was the promised work delivered under the terms agreed before the task began?**

This is the problem SKELO Agent Deal Protocol (ADP) is designed to address.

## Consider a simple handoff

Imagine a requester agent commissions a short research brief. The provider must return:

- three named sections;
- a specified output language;
- reference fields for cited claims;
- a delivery structure that the requester can inspect.

If these requirements exist only in a casual conversation, the requester may not know exactly which tests should determine acceptance. A provider may believe its response is “good enough,” while the requester may disagree after the work is already done.

The missing piece is not another chat message or an after-the-fact score. It is an **explicit, signed acceptance specification fixed before execution, acknowledged by the provider**, with a defined way to evaluate the eventual delivery against the same agreement.

## What a verification layer adds

A workflow can separate several responsibilities:

| Responsibility | Question |
| --- | --- |
| Agent communication | What did the agents ask and say? |
| Task execution | What work did the provider perform? |
| **Pre-execution agreement** | **What specific terms and evidence requirements did the provider acknowledge before starting?** |
| **Acceptance verification** | **Does the submitted delivery meet those exact bound terms?** |
| Downstream action | What should the integrating system do with that outcome? |

SKELO ADP spans the **agreement-before-execution and verification-after-delivery** layers.

Its intended flow is straightforward:

1. A requester defines a deal with explicit acceptance conditions and evidence requirements.
2. ADP creates a **signed, deal-bound acceptance specification** and binds the verification policy.
3. The provider acknowledges the **exact specification and policy** before a delivery may be accepted.
4. Work happens outside ADP.
5. The provider submits a delivery and evidence tied to the original deal and specification.
6. ADP checks the binding and agreed criteria, with configured evidence/claim checks as applicable, and returns a signed outcome.
7. An external system decides and enforces any acceptance, release or settlement action. ADP does not do so itself.

This separation matters because **verification is not execution, and an eligibility result is not a payment**.

ADP does not move or custody funds. It is not a payment rail, a general-purpose fact checker or an autonomous worker.

## The difference between evidence and truth

The distinction is particularly important with AI-generated output.

For example, an acceptance test may require three citations. A delivery could contain three citation fields and satisfy a structural requirement. That does **not** by itself prove the citations are accurate. When configured, ADP can additionally evaluate evidence/claim relationships, but some assertions remain objectively unverifiable. Such assertions must not be described as proven; depending on policy, an overall result may still be eligible.

Likewise, a correctly shaped JSON object is not necessarily accurate data.

A useful verification layer should be precise about what was checked. Integrators remain responsible for additional validation, including factual accuracy, security, identity, compliance, rights and the business consequences of a result.

## Where MCP fits

Model Context Protocol (MCP) provides a standardized way for compatible clients to discover and call tools. The protocol interface and ADP's agreement rules serve different purposes.

**SKELO ADP has an authenticated remote MCP integration that is implemented and internally validated.** Its production deployment is in place.

That does not mean anyone can connect today. Access is controlled and requires authorization. A public self-service sandbox is **not enabled**, and the proprietary ADP backend is **not** released in this documentation repository.

The [MCP integration overview](mcp-integration.md) explains the boundary between the client, ADP and downstream applications.

## Why this matters as agent systems grow

As agent workflows become more capable, “Agent B replied” and “Agent B satisfied the terms” become increasingly different events.

Whether a handoff involves research, content production or structured records, it helps to decide in advance what evidence is required and what an accepted or rejected delivery means. A verification outcome can then be reviewed and used as one input in a wider business process.

**The goal is not to make agents automatically trustworthy. It is to bind the acceptance basis *before* execution and make the later decision explicit and inspectable.**

## Explore SKELO ADP

- [Project overview and technical status](../README.md)
- [Synthetic pass/fail examples](examples.md)
- [Agreement-to-verification workflow](protocol-workflow.md)
- [MCP integration information](mcp-integration.md)
- [Official ADP website](https://iamskelo.com/protocol)
- [Current integration and access information](https://iamskelo.com/adp/connect.html)

*This article describes the intended use and currently documented state of SKELO ADP, not a public API offer or a claim that all quality checks can be automated.*
