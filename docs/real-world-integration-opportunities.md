# Where SKELO ADP could fit in existing AI workflows

**Real platforms already automate tasks. SKELO ADP could add an explicit agreement-and-verification step between delivery and a downstream decision.**

The examples below reference documented products that exist today. They are **proposed integration designs**, not implemented, certified or tested integrations with those vendors. SKELO has not announced partnerships with them. **No public self-service ADP MCP sandbox is available**; external integration requires authorization and may require a custom connector.

## The pattern in one picture

```text
Existing platform / agent orchestration
    |
    v
Task requested -> criteria agreed -> agent performs work
                                          |
                                          v
                                  output + evidence
                                          |
                                          v
                        SKELO ADP: verify agreed conditions
                                          |
                               outcome / eligibility
                                          |
                                          v
                 existing system decides its next action
```

*ADP does not execute tasks, independently establish arbitrary factual truth or transfer money.*

## Six practical opportunities

### 1. n8n: AI-assisted business automations

**Exists today:** [n8n](https://docs.n8n.io/) builds workflows across apps; its documented [MCP Client node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.mcpClient) can call tools exposed by an external MCP server. The MCP Client Tool node is intended for use by an AI Agent.

**Example:** An automation delegates a competitor research brief to an AI agent. The agreement calls for four specified sections, required fields and attached source references.

**Where ADP could fit:** Before an n8n workflow emails the brief or proceeds to another business step, an authorized integration could submit the delivery and evidence to ADP for verification against criteria agreed earlier.

**Implementation work needed:** Configure an authorized MCP connection and the workflow's deal lifecycle, payload mapping, authentication and result-handling steps. Availability of individual ADP tools must be established in the authorized environment.

**Boundary:** Checking that references are present does not independently prove they are accurate.

### 2. LangGraph / multi-agent research: handoff acceptance

**Exists today:** [LangGraph and LangChain documentation](https://docs.langchain.com/oss/python/learn) describes multi-agent patterns, subagent delegation, routing and customer-support handoffs.

**Example:** A coordinator delegates a data analysis step to a specialist agent and requires a specified output schema, a summary and an evidence bundle.

**Where ADP could fit:** The coordinator could establish acceptance criteria at delegation time and request an ADP outcome when the specialist submits its result.

**Implementation work needed:** Build a bridge between LangGraph's state/tool workflow and the authorized ADP interface, including state persistence and decisions for rejected deliveries.

**Boundary:** ADP is not LangGraph and is not a replacement for orchestration, human review or model evaluation.

### 3. GitHub Actions: coding-agent delivery gates

**Exists today:** [GitHub status checks](https://docs.github.com/en/pull-requests/reference/status-checks) record validation results on pull requests and can be required before merging.

**Example:** A coding agent promises to change an API endpoint while keeping test results, a changelog entry and deployment notes in the delivered package.

**Where ADP could fit:** An independently written bridge could establish agreed deliverables, attach build/test artifacts, and use an ADP verification outcome as **one input** to an existing pull-request review and check workflow.

**Implementation work needed:** Build and permission a GitHub integration; bind the right commit to the delivery; validate evidence and configure branch protection/required checks as appropriate.

**Boundary:** ADP does not replace CI, security scanning or human code review; passing a checklist does not prove that a change is safe.

### 4. Zendesk: customer-service action checks

**Exists today:** [Zendesk AI agents](https://support.zendesk.com/hc/en-us/articles/6970583409690-About-AI-agents) handle support conversations and can perform actions in authorized systems.

**Example:** A support agent requests an internal fulfillment action and expects a structured confirmation with an order reference and a proof-of-completion field.

**Where ADP could fit:** The action's agreed evidence could be verified before the business workflow marks the requested operation as completed.

**Implementation work needed:** A separately developed and authorized integration with Zendesk's action or API mechanisms plus ADP; careful handling of customer privacy and existing permissions.

**Boundary:** ADP itself does not verify customer identity, refund eligibility or the truth of the underlying fulfillment event without appropriate independent evidence checks.

### 5. Shopify Flow: content and catalog operations

**Exists today:** [Shopify Flow](https://help.shopify.com/de/manual/shopify-flow) uses triggers, conditions and actions to automate store processes across apps. Some outbound HTTP features depend on the Shopify plan.

**Example:** An external agent is asked to produce structured product metadata for 20 synthetic products, each with required language, fields and approved formatting.

**Where ADP could fit:** A connector could evaluate delivery completeness against fixed acceptance criteria before the merchant's existing publication process proceeds.

**Implementation work needed:** An authorized adapter and appropriate Shopify/API/Flow permissions and plan capabilities.

**Boundary:** Structural acceptance does not establish regulatory compliance, factual product claims or rights clearance. A merchant must retain publication controls.

### 6. HubSpot: CRM and marketing workflow deliverables

**Exists today:** [HubSpot workflows](https://developers.hubspot.com/changelog/may-2026-rollup) support custom code actions, including a 2026 update to generate and test workflow actions with Breeze Assistant.

**Example:** A marketing agent prepares a lead-enrichment package or campaign brief with agreed fields, source references and language requirements.

**Where ADP could fit:** A workflow-specific adapter could obtain a verification outcome for the deliverable before updating records or initiating a later action.

**Implementation work needed:** Custom code or an approved integration, API permission checks, secure data handling and ADP onboarding.

**Boundary:** An eligible structural result is not proof that lead data is correct, consent exists or privacy requirements are met.

---

## What an actual pilot would test

A credible pilot should **not** claim full vendor integration on day one. Start with a synthetic handoff:

1. Pick **one** existing orchestrator (for example, an n8n flow or a LangGraph demo).
2. Define a fixed synthetic task and its acceptance criteria.
3. Complete the task in the existing tool, outside ADP.
4. Send permitted delivery information and evidence through an **authorized** ADP integration.
5. Inspect successful and unsuccessful verification outcomes.
6. Only then decide whether a production adapter is warranted.

No vendor partnership, certification, instant setup or automatic payment is claimed here.

## Which industries might care?

| Industry / team | Candidate handoff | What could be objectively checked |
| --- | --- | --- |
| Software development | Coding agent -> reviewer | Required files, specified tests, artifact references |
| Marketing / agencies | Content producer -> campaign manager | File count, format, requested sections, handoff evidence |
| E-commerce | Catalog agent -> store workflow | Product field structure, required assets, delivery completeness |
| Customer support | Support action agent -> operations | Presence of agreed reference fields and action evidence |
| Research / analytics | Research agent -> requester | Required sections, sources provided, schema and file structure |
| Enterprise operations | Process agent -> approver | Required documents and evidence fields before an approval decision |

**Important:** Checkability depends on the actual agreement and the verification capabilities configured in the authorized ADP environment. Presence of a field or reference is not equivalent to independent verification of its underlying truth.

## Want to propose a real pilot?

[Open an evaluation-interest request](https://github.com/artavares79-hash/skelo-adp-developers/issues/new?template=integration-interest.yml) and describe a **synthetic, non-sensitive** workflow. Requests do not guarantee access; the public self-service sandbox is not enabled.

[Back to SKELO ADP](../README.md) · [MCP integration](mcp-integration.md) · [Synthetic examples](examples.md)
