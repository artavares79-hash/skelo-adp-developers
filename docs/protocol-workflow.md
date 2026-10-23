# Protocol workflow

**The protocol starts before an agent executes a task.** The acceptance basis must be agreed and bound before the provider can submit a delivery to ADP.

1. **Establish the deal.** Requester and provider identify the job, explicit objective acceptance criteria, evidence requirements and verification rules. Free-form expectations are not silently converted into guaranteed tests.
2. **Create and freeze the specification.** ADP creates a signed, deal-bound acceptance specification and binds its verification/settlement policy. The frozen specification and policy can be identified through their cryptographic hashes.
3. **Acknowledge the exact terms.** The provider acknowledges the specific deal and the exact specification **and policy** hashes. A delivery submitted through ADP without the required valid acknowledgement is rejected.
4. **Perform the work externally.** The provider executes outside ADP. ADP is not an execution engine and cannot stop actions performed outside its own integration.
5. **Submit a bound delivery and evidence.** The submitted delivery must refer to the originally bound deal and specification. A different specification or other mismatched binding is rejected rather than treated as an acceptable substitute.
6. **Verify against what was agreed.** ADP checks the signed/bound terms, configured structural conditions and, where specified and supported, claim/evidence relationships. Unverifiable claims are distinguished from objectively verified ones; evidence presence alone does not establish factual truth.
7. **Return a signed outcome for a downstream decision.** ADP produces a verification result and a settlement-eligibility decision. A payment rail or other external workflow **may** use this output, but must itself authenticate, authorize and enforce any actual release. ADP neither holds funds nor moves money.

## Why the timing matters

| An ordinary after-the-fact check | A pre-execution ADP handoff |
| --- | --- |
| A result arrives and a reviewer may decide what counts as acceptable | The agreed objective checks are established **before** the work begins |
| The acceptance basis may be reconstructed from messages | The deal is bound to a signed specification and policy, acknowledged by the provider |
| A generic “done” event can move a workflow forward | ADP gives an explicit outcome tied to the original deal and submitted evidence |
| The caller must decide whether to proceed | The caller **still** decides, but can enforce a gate based on the ADP outcome |

**Boundary:** ADP cannot retroactively undo executed work or an external payment. Prevention of premature settlement requires an external workflow that actually waits for and validates the ADP result.

[Illustrative test scenarios](examples.md) · [MCP integration](mcp-integration.md) · [Project overview](../README.md)
