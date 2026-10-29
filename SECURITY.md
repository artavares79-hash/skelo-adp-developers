# Security policy

## Reporting a vulnerability

Do **not** open a public issue for a suspected vulnerability.

Use GitHub **private vulnerability reporting** for this repository (*Security → Report a vulnerability*). Please include: affected component and version, impact, minimal reproduction, and whether you intend to disclose publicly.

This is a small project: there is no SLA and no bounty. Reports are handled on a best-effort basis.

## Scope

In scope: the specification (design flaws that break its stated guarantees, e.g. canonicalisation, signature, hash-chain or replay issues) and the published conformance data.
Out of scope: the hosted sandbox/MCP service at iamskelo.com (see the contact route on that site), third-party dependencies, and social-engineering or physical attacks.

## Security model in one paragraph

ADP proves *who* signed *which* terms, verdict and delivery hash, in *which* order, and refuses a second release of the same deal. It does **not** authenticate parties (key distribution is yours), protect private keys, or prove that a delivery is correct or a verifier honest. See [`docs/responsibilities.md`](docs/responsibilities.md) and spec §15 (threat model).

## Known limitations (draft)

* The threat model (spec §15) has **not** been reviewed by an independent security reviewer.
* There is no independent second implementation yet.
* The example keys in the test vectors are public and **insecure by design**; never use them.
