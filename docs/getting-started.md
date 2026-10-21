# Getting started with SKELO ADP

**Know what should count as “done” before another agent starts work.**

SKELO ADP supports agreement and verification between agents. Its production deployment and authenticated remote MCP integration are implemented and internally validated, but **public self-service access is not enabled**.

## Step 1 — See whether ADP fits

ADP may be relevant when your workflow has a requester, a provider, a deliverable and specific criteria that can be agreed in advance. Start with [use cases](use-cases.md) and the [workflow](protocol-workflow.md).

## Step 2 — Design a test agreement

Write down:
- What the provider must deliver;
- Which objective checks are required;
- What evidence should accompany delivery;
- Which downstream process, if any, would consume the verification outcome.

Prefer checks you can state unambiguously. Remember: evidence being present does not prove every claim is true.

## Step 3 — Understand the integration boundary

ADP verifies against agreed criteria. It is **not** a payment rail and does not execute the provider's task. Read the [MCP overview](mcp-integration.md) and [security guidance](../SECURITY.md).

## Step 4 — Request authorized evaluation

Review the [official integration information](https://iamskelo.com/adp/connect.html). Access, if approved, is provisioned through an authorized channel. There is no publicly available sign-up-and-test sandbox.

## Step 5 — Test safely when access is granted

Use the endpoint, authentication and protocol instructions actually supplied for your authorized environment. Discover the tools exposed to that session, start with non-sensitive synthetic data, and check both successful and unsuccessful verification outcomes before building a business integration.

**Never commit credentials or production payloads to GitHub.** The [examples](examples.md) illustrate the ideas; they are not a drop-in API client.

[FAQ](faq.md) · [Support and feedback](support-and-feedback.md)
