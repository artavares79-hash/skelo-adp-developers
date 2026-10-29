# Release notes — ADP v0.1.2 (draft specification)

**Status:** draft, not agreed with third parties, not independently reviewed. Terms of use for this material are not decided yet; no permission beyond reading is granted.

## What is published
1. **English normative specification** — read and implement ADP without the German sources.
2. **Payment-free profile** — complete agreements (terms → countersignature → verdict → release rule → record) with no payment system.
3. **Test vectors** — language-neutral payment-free vectors (26 release cases, 12 record cases) and the v0.1.1 vector set.
4. **Documentation** — responsibilities, conformance, versioning, status.

## Action required when upgrading from v0.1.1
Verdicts must carry the evidence the agreed terms require; otherwise the release rule answers `DENIED: EVIDENCE_REQUIREMENTS_UNMET` (spec §4.7 / §18.1). Nothing else on the wire changed; objects and hashes of v0.1.1 stay valid.

## What this release is not
Not a payment system, not a transport, not an identity system, not a hosted service. No software packages are published with this release. See [`docs/responsibilities.md`](docs/responsibilities.md) and [`docs/status-and-roadmap.md`](docs/status-and-roadmap.md).
