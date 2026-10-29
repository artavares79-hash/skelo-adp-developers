# SKELO ADP — Agent Deal Protocol

**Agree before execution. Freeze the terms. Verify before release.**

An AI agent can promise a result, report "done" and even trigger a follow-up action. But who defines — **before the work starts** — what counts as an acceptable delivery, and prevents the goalposts from moving afterwards?

The **Agent Deal Protocol (ADP)** is a small, payment-independent protocol for exactly that. Two parties sign the terms of a job (the *AcceptanceSpec*) before work begins; the provider countersigns *exactly these terms*; a designated verifier later signs a verdict that is bound to the terms and to the delivered artifact; a strict release rule decides whether the follow-up may happen; and a hash-chained *DealRecord* lets **anyone re-verify the whole exchange independently**, offline.

ADP is **not** a payment rail, escrow service, identity authority, transport, or truth oracle. **It works completely without payments** (the *payment-free profile*, spec §17). Where money is involved, payment systems can be bound to it from the outside.

## Current version: v0.1.2 (draft)

| Item | Status |
|---|---|
| **Specification v0.1.2 (English)** | [`spec/ADP-v0.1.2-EN.md`](spec/ADP-v0.1.2-EN.md) — draft, published for reading and review |
| **Test vectors** | [`conformance/`](conformance) — language-neutral payment-free vectors (JSON) and the v0.1.1 vector set |
| **Documentation** | [`docs/`](docs) — workflow, responsibilities, conformance, versioning, FAQ, status |
| **Hosted sandbox / MCP service** | Separate, access by approval only — [iamskelo.com/adp/connect.html](https://iamskelo.com/adp/connect.html) |
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
