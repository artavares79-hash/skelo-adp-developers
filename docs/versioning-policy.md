# Versioning policy (proposal)

## Version numbers
| What | Example | Meaning |
|---|---|---|
| **Specification version** | `ADP v0.1.2` | The protocol text and its vectors. |
| **Wire version strings** | `adp-acceptance/0.1`, `adp-verification/0.1`, `adp-record/0.1` | Appear in signed objects. Change **only** when a change makes older objects unverifiable or ambiguous. v0.1.1 → v0.1.2 did not change them. |

## Rules
1. **Spec `PATCH`** increases for compatible consolidations that do not change behaviour.
2. **Pre-1.0:** a `MINOR` increase may contain breaking changes to the specification. Each is listed in the changelog with a migration note. Wire-level breaks always increment the wire version strings.
3. **Spec-level change process:** anything touching a hash, signature rule, wire field, state or error code is a `spec-change`: public issue, rationale, updated vectors, implementations updated together, and a version decision by the maintainers.
4. **Strictness changes** (like the evidence rule in 0.1.2, which enforced something earlier versions already required) are announced as potentially breaking, with a temporary opt-out, and are never silent.
5. **1.0** is not planned until: an independent second implementation passes the vectors, the threat model has been reviewed externally, and governance is settled.
6. **Pre-release identifiers** (`0.1.3a1`, `0.1.3-rc.1`) mark builds that are not recommended for production.

## Support window
None defined. Only the latest `0.1.x` is maintained.
