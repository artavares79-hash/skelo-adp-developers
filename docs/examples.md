# Synthetic examples: what does verification mean?

These scenarios are **illustrative**, use invented data, and are **not executable ADP API requests**. They do not describe publicly available tool schemas or imply that an arbitrary factual claim can be verified.

## Example 1 — A research brief that passes agreed structural checks

A requester asks a provider agent for a short research brief.

**Example acceptance terms (conceptual):**

~~~json
{
  "task": "Produce a synthetic market briefing",
  "acceptanceCriteria": {
    "requiredSections": 3,
    "citationsRequired": true,
    "language": "en"
  }
}
~~~

The provider acknowledges the agreed terms, works outside ADP and submits a briefing with three sections and reference fields.

ADP then evaluates the submitted claims and evidence against the criteria established for this agreement. **If those configured checks are satisfied**, the workflow can yield an eligible outcome for an external integration to consider.

This does **not** independently establish that each source is correct, the analysis is insightful, or any payment should automatically occur.

## Example 2 — A delivery that does not satisfy the terms

The same agreement requires citations, but the submitted delivery omits them.

The relevant checks are unsatisfied, so the result can be a **non-eligible** verification outcome. The criterion was defined before delivery; it was not invented after the provider submitted the work.

## Compare the two outcomes

| Item | Example 1 | Example 2 |
| --- | --- | --- |
| Required sections | Included | Included |
| Required citation fields | Included | Missing |
| Agreed checks | Satisfied in this illustration | Not satisfied |
| Possible verification outcome | Eligible | Non-eligible |
| Automatic payment by ADP | **No** | **No** |

## Why this matters

A message saying “done” is not the same as delivering against a previously agreed acceptance test. ADP makes that difference explicit, while the integrator retains responsibility for additional quality, security, factual and business checks.

[See more possible use cases](use-cases.md) · [Explore the protocol workflow](protocol-workflow.md)
