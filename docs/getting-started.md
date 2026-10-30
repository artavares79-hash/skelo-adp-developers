# Getting started with SKELO ADP

**Define and bind acceptable delivery criteria before execution — then verify against those terms.**

## Try it now with your own AI agent

Use this public MCP endpoint in a compatible remote-MCP client:

```text
https://iamskelo.com/adp/mcp-public
```

**No sign-up, password, API key or OAuth required.** For Claude Web, add a custom connector with this URL and no authentication. Then ask:

> Use SKELO ADP with synthetic test data only. Create a deal with simple objective acceptance criteria, read it, acknowledge the frozen terms, submit a matching delivery, and get its verification result. Explain the outcome.

The five tools are `adp_create_deal`, `adp_read_deal`, `adp_acknowledge_deal`, `adp_submit_delivery` and `adp_get_verification`. See [MCP integration](mcp-integration.md) for the workflow and sandbox limits. Observe anonymized test events in the [live activity monitor](https://iamskelo.com/adp/activity).

**Use synthetic data only.** Public test deals are temporary and rate-limited. The public sandbox does not fetch external source URLs, so source-dependent claims are not verified. A structural PASS / ELIGIBLE is not proof of truth or an actual payment.

## Step 1 — See whether ADP fits

ADP may be relevant when a workflow has a requester, provider, deliverable, objective criteria and a downstream action needing a verifiable acceptance basis. Start with [use cases](use-cases.md) and the [workflow](protocol-workflow.md).

## Step 2 — Design a pre-execution agreement

Write down:
- What the provider must deliver;
- Which objective checks are required;
- What evidence should accompany delivery;
- Which verification rules should apply;
- How the provider acknowledges the bound specification and policy;
- Which downstream process, if any, consumes the result.

Evidence being present does not prove every claim is true.

## Step 3 — Understand the integration boundary

ADP verifies against the agreed supported checks and requires the provider's acknowledgement of bound terms. It is **not** a payment rail and does not execute the provider's task. An external integrator must enforce any real acceptance or payment gate. Read [MCP integration](mcp-integration.md) and [security guidance](../SECURITY.md).

## Step 4 — Move beyond the public sandbox

The public sandbox is for experiments, not confidential or production workflows. For a protected integration, review [SKELO's integration information](https://iamskelo.com/adp/connect.html) and request authorized access.

## Step 5 — Test safely

Try both successful and unsuccessful synthetic cases, including missing acknowledgement, changed terms and unverifiable claims, before attaching any business process. **Never commit credentials or production payloads to GitHub.**

[FAQ](faq.md) · [Support and feedback](support-and-feedback.md)
