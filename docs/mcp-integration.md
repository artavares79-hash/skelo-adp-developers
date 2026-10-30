# MCP integration

**MCP lets compatible AI clients interact with ADP's agreement-and-verification tools.**

## Public sandbox — try without signing up

Remote MCP endpoint:

```text
https://iamskelo.com/adp/mcp-public
```

No registration, password, API key or OAuth is required for this **public synthetic-data sandbox**.

In Claude Web, add a custom MCP connector with the URL above and no authentication. Other MCP clients may support equivalent remote-server configuration; compatibility varies by client.

Discover and call these five tools:

1. `adp_create_deal` — create a test deal with frozen acceptance terms.
2. `adp_read_deal` — read back the deal and its bound criteria.
3. `adp_acknowledge_deal` — acknowledge the exact terms.
4. `adp_submit_delivery` — submit a synthetic delivery.
5. `adp_get_verification` — retrieve the verdict and eligibility result.

Example prompt:

> Connect to the SKELO ADP public sandbox. Using only synthetic data, create a small test deal, read its terms, acknowledge it, submit a matching delivery and retrieve the verification verdict. Explain what each result means.

**Sandbox limits:** isolated, temporary test deals; per-source and global request/deal limits; no customer or production data. Public test deals are automatically cleaned up after approximately 24 hours. External URL retrieval is disabled for public-sandbox verification: source-dependent claims are marked unverifiable (`RETRIEVAL_DISABLED_PUBLIC_SANDBOX`) rather than asserted as checked. A PASS or ELIGIBLE result applies to the actual configured checks; it is not proof of factual accuracy or payment.

Watch anonymized events at the [live activity monitor](https://iamskelo.com/adp/activity). Events are delayed by approximately 60 seconds. The origin label `unclassified` does **not** establish that a visitor is independent or external.

**Observed test, 30 October 2026:** SKELO connected Claude Web to the public endpoint, completed all five tools and received PASS / ELIGIBLE on a synthetic structural-check deal. This is an operator-run integration test via Anthropic infrastructure, **not independent third-party validation or a partnership**.

## Protected integrations

The separate `https://iamskelo.com/adp/mcp` endpoint is protected and supports authorized integrations. Its authentication is not required for the public sandbox. For production integration details, see [SKELO's integration information](https://iamskelo.com/adp/connect.html).

## What the integration is for

The MCP interface covers ADP's **agreement-to-verification lifecycle**, not merely after-the-fact scoring:

1. Establish explicit acceptance terms **before execution**, with a signed, deal-bound specification and verification policy.
2. Obtain the provider's acknowledgement of the exact specification and policy.
3. Bind delivery and evidence to the original conditions.
4. Receive verification and eligibility outcomes; the integrating workflow enforces any downstream decision.

ADP does **not** make external systems withhold payment or prove factual truth. Clients and integrating systems remain responsible for agent behavior, credentials (when applicable), content validation, user permissions and downstream actions.

This repository publishes protocol documentation and testing instructions, **not** the private hosted backend or secrets. For more context, see [Getting started](getting-started.md), [examples](examples.md) and [FAQ](faq.md).
