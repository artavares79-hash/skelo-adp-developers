# Optional Sui anchoring for Evidence Replay

## Status

Sui Mainnet, the production Sui publisher, Policy v5 and production Evidence Replay are not activated.

SKELO has tested optional Evidence Replay anchoring on **Sui Testnet** with synthetic data. It is not a Sui Mainnet service, a payment function, or a production availability claim. No wallet, token or blockchain access is needed to use the ADP protocol or its MCP tools.

The public test reference is:

- Network: Sui Testnet
- Transaction: [`9X3MukSDen2cgnaN1c9ijCSVxYGtEV3ZE1o13HNmL8L8`](https://suiscan.xyz/testnet/tx/9X3MukSDen2cgnaN1c9ijCSVxYGtEV3ZE1o13HNmL8L8)
- Confirmed batch root: `f32a2af1ff4a747815feef399eaa65fe71a0478b888b175e98c4f9cf693d1601`
- Publisher: `0xd310660a5ceac955dc8fedfbb9b27b634309177369118c969329757a73d5184f`
- Sui Testnet chain identifier: `69WiPg3DAQiwdxfncX6wYQ2siKwAe6L9BZthQea3JNMD`
- Test data: synthetic digests only

The transaction has been read through independent Sui Testnet GraphQL and gRPC paths. Its transaction digest, sender signature, successful checkpoint inclusion and batch marker were checked locally. Public full-node responses remain an infrastructure dependency; this implementation is not a Sui light client.

## Data flow

1. ADP freezes the deal conditions before execution.
2. Instrumented agent and tool boundaries can append events to Evidence Replay. Unobserved actions remain unobserved, and agent statements remain assertions.
3. The recorder builds a hash chain and signs a checkpoint containing the chain head, count and coverage statement.
4. An authorized publisher reduces one or more technical digests to a Merkle root.
5. The publisher submits a version tag and the root to Sui Testnet. Prompts, credentials, personal data and deal contents are never part of the transaction payload.
6. An offline verifier checks the replay hash chain and recorder signature. The Sui verifier additionally checks the Merkle proof, pinned network, publisher, transaction signature, payload and confirmed checkpoint.

The on-chain anchor adds an external timestamped commitment. It does not upgrade an agent assertion into proof, determine factual truth, establish complete observation, or change ADP's PASS, FAIL, INCONCLUSIVE or settlement policy.

## Independent verification model

A verifier needs four items delivered through a trusted release channel:

- the exported, redacted replay package;
- trusted historical recorder public keys;
- the batch record and Merkle proof for the replay digest;
- pinned Sui network, publisher and transaction identifiers.

Verification must fail closed when the replay is modified, the recorder signature is untrusted, the Merkle proof does not match, the transaction has another publisher or payload, or the chain cannot be reached. A chain outage is `CHAIN_UNAVAILABLE`, never a successful verification.

The transaction above anchors a synthetic test batch. The separate two-agent Evidence Replay exercise validated real instrumented agent/tool execution in an isolated environment, but it is not represented as the source of this transaction.

## Duplicate and freshness handling

The publisher ledger records an intent before submission and a completion marker only after chain verification. A root already confirmed by the pinned publisher is not submitted again during normal operation. Deliberate duplicate test transactions are reported rather than silently treated as one anchor.

An older valid anchor proves historical existence only. Applications that need the latest state must distribute a separately authenticated latest-anchor reference.

## Privacy and operational limits

Only fixed-size hashes and necessary technical metadata are published. Hashes are permanent and can be linkable through the publisher address, so retention and legal review are required before production enrolment. Replay exports remain access-controlled and are not public endpoints.

Production use still requires approved recorder and witness deployment, production key custody and rotation, off-host backup custody, retention values, monitoring, rollback rehearsal and independent security review. Mainnet would additionally require explicit authorization, real SUI for fees and a durable endpoint/archive strategy.

## Existing ADP interfaces

- Public synthetic MCP sandbox: `https://iamskelo.com/adp/mcp-public`
- Protected MCP integration: `https://iamskelo.com/adp/mcp`
- Integration information: `https://iamskelo.com/adp/connect.html`
- Public activity monitor: `https://iamskelo.com/adp/activity`

The Sui testnet work does not change these interfaces or their authentication rules.
