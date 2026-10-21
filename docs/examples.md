# Synthetic examples

These examples are illustrative, non-production data; they are not API requests.

## Research summary

```json
{
  "task": "Produce a concise synthetic market summary",
  "acceptanceCriteria": {
    "requiredSections": 3,
    "citationsRequired": true,
    "language": "en"
  }
}
```

The provider returns three sections and synthetic citations. ADP evaluates the delivery against the frozen criteria. If the checks pass, the requester’s downstream workflow can consider the eligible outcome.

## Negative result

A delivery without the required citations does not satisfy the same agreement and can return a non-eligible result. That is a verification outcome, not a claim that content is universally false.

An authorized MCP-capable client discovers its available ADP capabilities, participates in the deal workflow, and reads the verification state. It should begin with synthetic data and keep final settlement in its own governed workflow.
