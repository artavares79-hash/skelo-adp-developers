# Synthetic examples: agreed before, verified after

These are **illustrations using invented data**, not executable ADP API requests or public tool schemas. They show the difference between **binding the conditions before work** and deciding what to accept only after receiving a result.

## First: create a bound agreement

A requester wants a synthetic three-section research briefing, in English, with specified evidence requirements.

**Conceptual acceptance terms — not a real request payload:**

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

Before the agent starts, ADP creates a signed acceptance specification for the deal and binds it to a verification policy. The provider acknowledges the **exact specification and policy**. A delivery without the required valid acknowledgement is rejected.

The following scenarios assume that initial step has occurred unless otherwise noted.

## Scenario A — Complete delivery

The provider submits an English briefing with the three required sections and the specified reference fields. The delivery is bound to the original deal and specification.

**Possible result:** The objective checks can pass. Any evidence-related outcome depends on which evidence rules are configured and satisfied. The integrating system may consider the ADP eligibility outcome before accepting the work or taking another action.

**This does not prove** that every cited fact is correct or every analytical conclusion is sound.

## Scenario B — Missing agreed requirement

The provider submits two sections instead of the three fixed in the agreement.

**Possible result:** The missing mandatory item is a failed objective check; the submission is not treated as having met that criterion. The requester does **not** have to invent a new acceptance rule after delivery: the requirement was already bound to this deal.

## Scenario C — Different terms submitted after the work

The provider tries to reference a modified acceptance specification that asks for only two sections, instead of the signed specification agreed at the beginning.

**Expected result:** A mismatched or modified specification binding is rejected. The submitted terms cannot silently replace the originally bound agreement.

## Scenario D — No valid provider acknowledgement

A provider sends a delivery without first acknowledging the deal's exact specification and policy.

**Expected result:** ADP rejects that delivery. This is a **pre-delivery protocol requirement**, not just an end-of-job quality score.

## Scenario E — Evidence-supported versus unverifiable claims

A delivery may include claims and cited evidence. Where the agreement and verification configuration support those checks, ADP can evaluate claim/evidence relationships, including situations where a source supports or conflicts with a claim.

However, an analytical or predictive claim may remain **objectively unverifiable**. ADP can distinguish this from an objectively supported claim. Under some configured policies, an outcome containing unverifiable claims **may still be eligible**, provided no mandatory objective check failed.

**ELIGIBLE does not mean “every claim is true.”** Integrators must decide whether their own use case needs stronger evidence, independent validators or human approval.

## Why the two phases matter

| Before execution | After the delivery |
| --- | --- |
| Define acceptance conditions, evidence requirements and verification policy | Check against those already agreed conditions |
| Bind a signed specification to a concrete deal | Confirm the submitted delivery refers to that same specification |
| Require the provider to acknowledge the precise terms | Produce a signed verification result and eligibility outcome |
| No payment or work execution by ADP | External system chooses whether to release, reject or seek changes |

**Downstream limitation:** ADP supplies the decision input. It cannot itself stop external payments, protect customer data, verify business authority or force another platform to obey the result. Such controls must be implemented by the integrating system.

[Protocol workflow](protocol-workflow.md) · [Use cases](use-cases.md) · [MCP integration](mcp-integration.md)
