# Frequently asked questions

## Is ADP real or only a concept?

The agreement-and-verification workflow and remote MCP integration are implemented. The public sandbox has been tested using an actual Claude Web connector.

## Can I connect an MCP client today?

**Yes, if your client supports the public remote MCP endpoint.** Add `https://iamskelo.com/adp/mcp-public` with no authentication. Claude Web was successfully tested on 30 October 2026. Other clients may have different connector requirements; universal compatibility is not guaranteed.

## Where are the public API keys?

**You do not need any.** The [public MCP sandbox](https://iamskelo.com/adp/mcp-public) requires no account, password, API key or OAuth. Use synthetic data only. Protected production integrations require separate authorization.

## How do I request a protected integration?

For non-confidential use-case details, [open an evaluation request](https://github.com/artavares79-hash/skelo-adp-developers/issues/new?template=integration-interest.yml) or review [SKELO's integration information](https://iamskelo.com/adp/connect.html). Approval is not guaranteed.

## Is ADP open source?

The **protocol specification** v0.1.2 is published for reading and review. Licence terms for the text have not been decided yet; until they are published, no permission beyond reading is granted. The hosted backend and its internal security implementation are not published.

## Isn't this just another AI quality checker?

No. ADP starts **before** delivery: it binds a signed acceptance specification and verification policy to a deal, and the provider acknowledges those terms. Delivery is checked against the original agreement rather than requirements invented afterwards.

## Can a provider change the conditions after accepting a deal?

A delivery referring to modified bound terms does not silently replace the accepted specification. External relationships still require their own identity, access, consent and legal controls.

## Does ELIGIBLE mean the work is factually correct?

No. ADP distinguishes supported objective checks from claims that cannot be verified. The public sandbox disables external URL retrieval, so source-dependent checks are marked unverifiable. ELIGIBLE can still occur when mandatory checks pass; downstream systems must impose any stricter quality requirements.

## Can ADP guarantee a payment won't happen before verification?

No. ADP **does not control external payment rails**. A payment or workflow integrator must authenticate the result and enforce any real release gate.

## Does ADP make payments or hold money?

No. ADP can produce a verification or eligibility outcome; a separate system performs any transaction.

## Can ADP guarantee factual accuracy?

No. Its verification applies only to the criteria and evidence checks established for a particular agreement.

## Does MCP mean ADP was built by the MCP project?

No. MCP is an interface through which compatible agents use ADP tools. ADP's agreement and verification rules are separate.

## Can I try ADP without approval?

**Yes.** Add `https://iamskelo.com/adp/mcp-public` to a compatible MCP client without authentication, and follow the [getting-started guide](getting-started.md). Watch anonymized activity at [ADP Live Activity](https://iamskelo.com/adp/activity). The public test deals are temporary and rate-limited.

## Can I report a problem or suggest improvements?

For non-sensitive feedback, follow [Support and feedback](support-and-feedback.md). Never post credentials, customer data or vulnerability details in public issues.
