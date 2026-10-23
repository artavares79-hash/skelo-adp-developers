# Where SKELO ADP could fit in existing AI workflows

**Real platforms already automate tasks. SKELO ADP could bind a signed, deal-specific acceptance agreement *before* an agent performs work, require the provider to acknowledge it, and verify the later delivery against those same frozen terms *before* a downstream decision.**

The examples below reference documented products that exist today. They are **proposed integration designs**, not implemented, certified or tested integrations with those vendors. SKELO has not announced partnerships with them. **No public self-service ADP MCP sandbox is available**; external integration requires authorization and may require a custom connector.

## The pattern in one picture

```text
Existing platform commissions a task
                |
                v
ADP: signed acceptance spec + deal-bound policy
                |
                v
Provider acknowledges the exact bound terms
                |
                v
Agent does the work OUTSIDE ADP
                |
                v
Delivery + evidence must match original agreement
                |
                v
ADP: verify agreed conditions -> signed outcome / eligibility
                |
                v
External workflow authenticates the outcome
and decides whether to accept, release or ask for correction
```

**Why this is different from adding a validator afterward:** The provider cannot silently substitute a looser specification after submitting an incomplete delivery, and the requester cannot quietly make up stricter terms after the result arrives. The acceptance basis is established in advance.

**Integration boundary:** ADP does not execute tasks, independently prove arbitrary factual truth or transfer money. An external release or payment must be actively gated by the integrating system; ADP cannot prevent actions that bypass the gate.

## Six practical opportunities

### 1. n8n: AI-assisted business automations

**Exists today:** [n8n](https://docs.n8n.io/) builds workflows across apps; its documented [MCP Client node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.mcpClient) can call tools exposed by an external MCP server. The MCP Client Tool node is intended for use by an AI Agent.

**Example:** An automation delegates a competitor research brief to an AI agent. The agreement calls for four specified sections, required fields and attached source references.

**Where ADP could fit:** An authorized n8n integration could **first create a deal-bound acceptance specification and obtain the research provider's acknowledgement**. After execution, it could send the tied delivery and evidence for verification *before* any approval or downstream handoff.

**Implementation work needed:** Configure an authorized MCP connection and the workflow's deal lifecycle, payload mapping, authentication and result-handling steps. Availability of individual ADP tools must be established in the authorized environment.

**Boundary:** Checking that references are present does not independently prove they are accurate.

### 2. LangGraph / multi-agent research: handoff acceptance

**Exists today:** [LangGraph and LangChain documentation](https://docs.langchain.com/oss/python/learn) describes multi-agent patterns, subagent delegation, routing and customer-support handoffs.

**Example:** A coordinator delegates a data analysis step to a specialist agent and requires a specified output schema, a summary and an evidence bundle.

**Where ADP could fit:** The coordinator could **bind the specialist's exact deliverables and verification policy at delegation time** and require acknowledgement. When the specialist submits its result, ADP could evaluate it against those unchanged conditions.

**Implementation work needed:** Build a bridge between LangGraph's state/tool workflow and the authorized ADP interface, including state persistence and decisions for rejected deliveries.

**Boundary:** ADP is not LangGraph and is not a replacement for orchestration, human review or model evaluation.

### 3. GitHub Actions: coding-agent delivery gates

**Exists today:** [GitHub status checks](https://docs.github.com/en/pull-requests/reference/status-checks) record validation results on pull requests and can be required before merging.

**Example:** A coding agent promises to change an API endpoint while keeping test results, a changelog entry and deployment notes in the delivered package.

**Where ADP could fit:** A bridge could **bind the agreed deliverables and test-evidence requirements before the coding agent starts**, obtain acknowledgement, attach authorized build/test artifacts later and use ADP eligibility as **one input** to existing pull-request checks.

**Implementation work needed:** Build and permission a GitHub integration; bind the right commit to the delivery; validate evidence and configure branch protection/required checks as appropriate.

**Boundary:** ADP does not replace CI, security scanning or human code review; passing a checklist does not prove that a change is safe.

### 4. Zendesk: customer-service action checks

**Exists today:** [Zendesk AI agents](https://support.zendesk.com/hc/en-us/articles/6970583409690-About-AI-agents) handle support conversations and can perform actions in authorized systems.

**Example:** A support agent requests an internal fulfillment action and expects a structured confirmation with an order reference and a proof-of-completion field.

**Where ADP could fit:** A secure adapter could **bind the requested action and required proof before delegation**, obtain the responsible provider's acknowledgement and verify the returned evidence against that original agreement before another business step proceeds.

**Implementation work needed:** A separately developed and authorized integration with Zendesk's action or API mechanisms plus ADP; careful handling of customer privacy and existing permissions.

**Boundary:** ADP itself does not verify customer identity, refund eligibility or the truth of the underlying fulfillment event without appropriate independent evidence checks.

### 5. Shopify Flow: content and catalog operations

**Exists today:** [Shopify Flow](https://help.shopify.com/de/manual/shopify-flow) uses triggers, conditions and actions to automate store processes across apps. Some outbound HTTP features depend on the Shopify plan.

**Example:** An external agent is asked to produce structured product metadata for 20 synthetic products, each with required language, fields and approved formatting.

**Where ADP could fit:** A connector could **freeze the required catalog-data specification before commissioning the agent**, obtain acknowledgement and evaluate the delivered package against the bound criteria before the merchant's publication workflow proceeds.

**Implementation work needed:** An authorized adapter and appropriate Shopify/API/Flow permissions and plan capabilities.

**Boundary:** Structural acceptance does not establish regulatory compliance, factual product claims or rights clearance. A merchant must retain publication controls.

### 6. HubSpot: CRM and marketing workflow deliverables

**Exists today:** [HubSpot workflows](https://developers.hubspot.com/changelog/may-2026-rollup) support custom code actions, including a 2026 update to generate and test workflow actions with Breeze Assistant.

**Example:** A marketing agent prepares a lead-enrichment package or campaign brief with agreed fields, source references and language requirements.

**Where ADP could fit:** A workflow-specific adapter could **bind the expected lead-enrichment or briefing requirements in advance**, require provider acknowledgement and obtain a delivery-specific verification outcome before updating records or initiating a later action.

**Implementation work needed:** Custom code or an approved integration, API permission checks, secure data handling and ADP onboarding.

**Boundary:** An eligible structural result is not proof that lead data is correct, consent exists or privacy requirements are met.

---

## What an actual pilot would test

A credible pilot should **not** claim full vendor integration on day one. Start with a synthetic handoff:

1. Pick **one** existing orchestrator (for example, an n8n flow or a LangGraph demo).
2. Before work, create an authorized **signed, deal-bound acceptance specification and policy** for a fixed synthetic task.
3. Have the provider acknowledge the **exact** bound conditions; test that a missing acknowledgement is rejected.
4. Complete the task in the existing tool, outside ADP, and submit a delivery tied to the **original** specification.
5. Test successful and failed criteria, and a submission referencing **different** terms. Distinguish supported evidence checks from unverifiable claims.
6. Measure whether the **external workflow** correctly enforces an authorization/release gate; only then consider a production adapter.

No vendor partnership, certification, instant setup or automatic payment is claimed here.

## Which industries might care?

| Industry / team | Candidate handoff | What could be objectively checked |
| --- | --- | --- |
| Software development | Coding agent -> reviewer | Required files, specified tests, artifact references |
| Marketing / agencies | Content producer -> campaign manager | File count, format, requested sections, handoff evidence |
| E-commerce | Catalog agent -> store workflow | Product field structure, required assets, delivery completeness |
| Customer support | Support action agent -> operations | Presence of agreed reference fields and action evidence |
| Research / analytics | Research agent -> requester | Required sections, sources provided, schema and file structure |
| Enterprise operations | Process agent -> approver | Pre-agreed required documents and evidence before an approval decision |
| Insurance (illustrative) | External claims-document service -> insurer | Pre-agreed package format, evidence and provider acknowledgement; claims decision remains with insurer |

**Important:** Checkability depends on the actual agreement and the verification capabilities configured in the authorized ADP environment. Presence of a field or reference is not equivalent to independent verification of its underlying truth.

## Want to propose a real pilot?

[Open an evaluation-interest request](https://github.com/artavares79-hash/skelo-adp-developers/issues/new?template=integration-interest.yml) and describe a **synthetic, non-sensitive** workflow. Requests do not guarantee access; the public self-service sandbox is not enabled.

[Back to SKELO ADP](../README.md) · [MCP integration](mcp-integration.md) · [Synthetic examples](examples.md)
