# Frequently asked questions

## Is ADP real or only a concept?

The agreement-and-verification workflow has been implemented and internally validated. A production deployment is in place. The authenticated remote MCP integration is also implemented and internally validated.

## Can I connect any MCP client today?

There is **no public self-service access**. Connection requires authorization, and supported capabilities depend on the session and the connection details supplied after approval. Compatibility with an arbitrary client is not promised.

## How do I express interest in an external evaluation?

When the repository is public, [open an evaluation request](https://github.com/artavares79-hash/skelo-adp-developers/issues/new?template=integration-interest.yml) using synthetic, non-confidential use-case details. You may also review [SKELO's official integration information](https://iamskelo.com/adp/connect.html). Requests do not guarantee immediate approval or a specific response time.

## Where are the public API keys and test endpoint?

They are not provided here. A public self-service sandbox has **not** been enabled. Review the [official integration information](https://iamskelo.com/adp/connect.html) for the current access process.

## Is the ADP source code open source?

No. This repository contains developer-facing documentation only. The proprietary ADP backend and its internal security implementation are not published.

## Isn't this just another AI quality checker?

No. ADP starts **before** the provider delivers anything: it binds an explicit, signed acceptance specification and verification policy to a particular deal. The provider acknowledges those exact terms. The later delivery is checked against that original agreement, rather than being scored against requirements invented after the result arrives.

Unlike a generic after-the-fact validator, ADP also enforces protocol binding requirements, including rejecting a delivery with no valid provider acknowledgement or a mismatched specification. This is a statement about **ADP's documented capabilities**, not a claim that no other product offers overlapping features.

## Can a provider change the conditions after accepting a deal?

A delivery referring to different or modified bound terms does not silently replace the originally accepted specification. ADP checks the deal and specification binding. An external business relationship still requires its own identity, access, consent and legal controls.

## Does ELIGIBLE mean all the work is factually correct?

No. ADP distinguishes supported checks from claims that cannot be objectively verified. Depending on the agreed policy, an outcome containing unverifiable claims **can still be eligible** when mandatory objective checks pass. External systems must apply any stricter truth, quality, compliance or approval requirements appropriate for their business.

## Can ADP guarantee that a payment won't happen before verification?

No. ADP **does not control external payment rails**. It supplies a signed verification and eligibility outcome. The payment or workflow integrator must authenticate that result and enforce a genuine release gate; otherwise actions outside ADP remain possible.

## Does ADP make payments or hold money?

No. ADP can produce a verification or settlement-eligibility outcome. A separate external system remains responsible for any transaction or action.

## Can ADP guarantee the quality or factual accuracy of AI-generated work?

No. Its verification result applies to the criteria and evidence checks established for a particular agreement. Requiring a citation does not automatically prove that the citation is true.

## Does MCP mean the protocol itself was built by the MCP project?

No. MCP is an integration interface through which an authorized compatible agent can interact with tools exposed by ADP. ADP's agreement and verification rules are distinct from MCP.

## Can I try an example without access?

You can read the [synthetic examples](examples.md) and [protocol workflow](protocol-workflow.md). They illustrate the workflow but are **not** executable requests to a public ADP service.

## Can I report a problem or suggest improvements?

For non-sensitive feedback, follow [Support and feedback](support-and-feedback.md). Do not post credentials, customer data, production payloads or vulnerability details in public issues.
