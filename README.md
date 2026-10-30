# SKELO ADP — Agent Deal Protocol

**Agree before execution. Freeze the terms. Verify before release.**

An AI agent can promise a result, report "done" and even trigger a follow-up action. But who defines — **before the work starts** — what counts as an acceptable delivery, and prevents the goalposts from moving afterwards?

The **Agent Deal Protocol (ADP)** is a small, payment-independent protocol for exactly that. Two parties sign the terms of a job (the *AcceptanceSpec*) before work begins; the provider countersigns *exactly these terms*; a designated verifier later signs a verdict that is bound to the terms and to the delivered artifact; a strict release rule decides whether the follow-up may happen; and a hash-chained *DealRecord* lets **anyone re-verify the whole exchange independently**, offline.

ADP is **not** a payment rail, escrow service, identity authority, transport, or truth oracle. **It works completely without payments** (the *payment-free profile*, spec §17). Where money is involved, payment systems can be bound to it from the outside.

## Try ADP now — free public MCP sandbox

**No account, password, API key or OAuth required.** Add this remote MCP server to a compatible AI client:

```text
https://iamskelo.com/adp/mcp-public
```

For example, in Claude Web, add a custom connector using that URL and connect without authentication. Then ask your agent:

> Use the SKELO ADP tools to create a synthetic test deal, read it, acknowledge the frozen terms, submit a test delivery and retrieve its verification result. Use no personal or customer data.

Available tools: `adp_create_deal`, `adp_read_deal`, `adp_acknowledge_deal`, `adp_submit_delivery`, `adp_get_verification`.

See the [quickstart](docs/getting-started.md), [MCP integration guide](docs/mcp-integration.md), and [live activity monitor](https://iamskelo.com/adp/activity). The sandbox uses isolated, temporary test deals and usage limits. **External URL retrieval is disabled for public-sandbox verification**; unavailable source checks are marked accordingly, not presented as verified.

**Observed integration test (30 October 2026):** A Claude Web custom connector completed all five MCP tools with a synthetic test deal, resulting in PASS / ELIGIBLE for the configured structural checks. This was SKELO's own test through Anthropic infrastructure, **not independent external validation, a certification, or a partnership**. PASS does not establish factual truth or a payment.

The separate `/adp/mcp` endpoint remains protected for authorized integrations.

## Current version: v0.1.2 (draft)

| Item | Status |
|---|---|
| **Specification v0.1.2 (English)** | [`spec/ADP-v0.1.2-EN.md`](spec/ADP-v0.1.2-EN.md) — draft, published for reading and review |
| **Test vectors** | [`conformance/`](conformance) — language-neutral payment-free vectors (JSON) and the v0.1.1 vector set |
| **Documentation** | [`docs/`](docs) — workflow, responsibilities, conformance, versioning, FAQ, status |
| **Public hosted MCP sandbox** | [Try without login](https://iamskelo.com/adp/mcp-public) — synthetic tests only |
| **Authorized hosted MCP integration** | Separate protected endpoint — [integration information](https://iamskelo.com/adp/connect.html) |
| **SKELO ADP Cloud** | Planned. Not built. Not available. |

Terms of use for the published material have **not been decided yet**. Until they are published, no permission beyond reading is granted. Nothing here is an offer.

## How a deal works

1. **Freeze the terms.** The requester signs an AcceptanceSpec: what counts as success, who may judge, until when, which proofs every verdict must carry.
2. **Countersign.** The provider signs *these exact terms* (`providerAck`). Without it, the payment-free profile refuses to proceed.
3. **Work happens outside ADP.**
4. **Verify.** The designated verifier signs a `PASS`/`FAIL` verdict carrying the required evidence references.
5. **Release rule (spec §5).** Seven conditions — deal id agreement, valid and independently bound terms, delivery binding, authorised verifier, valid signatures, validity window, not yet consumed — plus the v0.1.2 evidence check (§18.1) must all hold: `ALLOWED` or `DENIED`.
6. **Record.** A DealRecord with a hash chain closes the deal as `SETTLED` or `REJECTED`. Anyone can re-verify it with only the exchanged files and the parties' public keys.

"Released" means: the work is proven to meet the agreed terms and may be acted upon. ADP moves nothing; your application performs the follow-up.

## What ADP does not do

ADP does not transport messages, identify parties, manage keys, decide who may authorise what, check whether claims are *true*, move money, or settle disputes. [`docs/responsibilities.md`](docs/responsibilities.md) lists precisely what your application must provide.

## Documentation

| | |
|---|---|
| [Specification v0.1.2 (EN)](spec/ADP-v0.1.2-EN.md) | normative |
| [Conformance and test vectors](docs/conformance.md) | how to test an implementation |
| [Responsibilities](docs/responsibilities.md) | ADP vs. your application |
| [Versioning policy](docs/versioning-policy.md) | |
| [Changelog](CHANGELOG.md) · [Release notes 0.1.2](RELEASE-NOTES-0.1.2.md) | |
| [Security policy](SECURITY.md) | |
| Background | [workflow](docs/protocol-workflow.md), [use cases](docs/use-cases.md), [FAQ](docs/faq.md), [MCP integration](docs/mcp-integration.md), [status and roadmap](docs/status-and-roadmap.md) |

**Official website:** [iamskelo.com/protocol](https://iamskelo.com/protocol) · [iamskelo.com/adp](https://iamskelo.com/adp/)
