# MCP integration

**MCP is how an authorized compatible client can talk to ADP. ADP is the agreement-and-verification layer behind it.**

## Current availability

- **Implemented:** authenticated remote MCP integration.
- **Validated:** internally tested by SKELO against the production-compatible deployment.
- **Deployment:** production deployment in place.
- **External access:** controlled and subject to authorization.
- **Public self-service sandbox:** not enabled.

A finished integration is not the same as a public endpoint anyone can use. No public token, connection URL or instant self-service test access is supplied by this repository.

## What happens in an authorized integration?

1. A developer reviews ADP's [workflow](protocol-workflow.md) and [use cases](use-cases.md).
2. An authorized evaluation is requested through [SKELO's integration information](https://iamskelo.com/adp/connect.html).
3. If approved, the developer receives the specific endpoint, authentication requirements and supported protocol instructions through the approved channel.
4. The client establishes an authenticated MCP session and discovers the tools available to that session.
5. Synthetic positive and negative test cases are run before any business workflow is attached.
6. The developer's own system decides how to act on ADP's verification result.

## Responsibilities and limits

**ADP:** Applies its agreement and verification rules to the submitted claims and evidence, subject to the agreed checks.

**The MCP client and integrating system:** Handle agent behavior, credential protection, input and output handling, additional content validation, user permissions, and any downstream decision or payment.

**This repository:** Supplies a conceptual integration guide. It does not publish backend implementation, credentials, environment-specific endpoints, private test vectors, or tool schemas that have not been approved as a public contract.

For a first look, see [Getting started](getting-started.md), [synthetic examples](examples.md) and the [FAQ](faq.md).
