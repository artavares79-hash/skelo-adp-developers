# Getting started with SKELO ADP

**Define and bind what counts as an acceptable delivery *before execution* — then verify against those exact terms.**

SKELO ADP supports agreement and verification between agents. Its production deployment and authenticated remote MCP integration are implemented and internally validated, but **public self-service access is not enabled**.

## Step 1 — See whether ADP fits

ADP may be relevant when your workflow has a requester, a provider, a deliverable, objective criteria that can be bound in advance, and a downstream action that needs a verifiable acceptance basis. Start with [use cases](use-cases.md) and the [workflow](protocol-workflow.md).

## Step 2 — Design a pre-execution agreement

Write down:
- What the provider must deliver;
- Which objective checks are required;
- What evidence should accompany delivery;
- Which verification rules should apply to the deal;
- How the provider will acknowledge the exact bound specification and policy;
- Which downstream process, if any, would consume the verification outcome.

Prefer checks you can state unambiguously. Remember: evidence being present does not prove every claim is true.

## Step 3 — Understand the integration boundary

ADP requires the delivery to match the signed, deal-bound acceptance terms and the provider's acknowledgement. It then verifies against the agreed supported checks. It is **not** a payment rail and does not execute the provider's task; an external integrator must enforce any actual acceptance or payment gate. Read the [MCP overview](mcp-integration.md) and [security guidance](../SECURITY.md).

## Step 4 — Request authorized evaluation

Review the [official integration information](https://iamskelo.com/adp/connect.html). Access, if approved, is provisioned through an authorized channel. There is no publicly available sign-up-and-test sandbox.

## Step 5 — Test safely when access is granted

Use the endpoint, authentication and protocol instructions actually supplied for your authorized environment. Discover the tools exposed to that session, start with non-sensitive synthetic data, and check both successful and unsuccessful verification outcomes, including a missing provider acknowledgement, changed specification and objectively unverifiable claim, before building a business integration.

**Never commit credentials or production payloads to GitHub.** The [examples](examples.md) illustrate the ideas; they are not a drop-in API client.

[FAQ](faq.md) · [Support and feedback](support-and-feedback.md)
