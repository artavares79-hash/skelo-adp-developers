# What ADP does — and what your application must provide

ADP is a small protocol core: **objects, rules and a record**. It deliberately leaves everything around it to the application that embeds it. Use this page to plan an integration. (Normative version: [`spec/ADP-v0.1.2-EN.md`](../spec/ADP-v0.1.2-EN.md), §19.)

| Concern | ADP does | Your application must provide |
|---|---|---|
| **Agreement terms** | Defines the `AcceptanceSpec` (what counts as success, who may judge, until when, which proofs are required), its signature and hash, and freezes it before work starts | The business content of the job; showing the terms to both parties; deciding when to lock them |
| **Countersignature** | Defines `providerAck` and (payment-free profile) checks it cryptographically and against the agreement | Getting the provider to sign; knowing the provider's public key from a source you trust |
| **Transport** | Nothing. (An optional description of an A2A binding exists in the spec) | Moving messages and the delivered artifact between agents: HTTP, queue, A2A, MCP, files… including ordering, retries, size limits |
| **Identity** | References parties by `kid`/`issuer`; treats a key it cannot resolve as an invalid signature | Mapping `kid` → public key from a source the *verifier* trusts (key directory, agent card, DID, earlier contact); proving who a party really is |
| **Key management** | Ed25519 signing and verification | Generating, storing, rotating and revoking keys; reacting to a compromise. Never reuse the example keys |
| **Authorisation** | Provides a place to bind an authorisation in the record (`adp.owner_authorization` or `ap2.*`) | Deciding *who may authorise what*, the authorisation document itself, and its authenticity — ADP stores only its hash and never inspects the document |
| **Doing the work** | Nothing | The provider's actual performance |
| **Checking the work** | Defines the verdict object (`PASS`/`FAIL`), the evidence rules and the check that a verdict is bound to the terms and the delivery | The actual checking (compare hashes, run tests, human review…), choosing the verifier, and the verifier's honesty. ADP proves *who said what about which delivery under which terms*, not that it is true |
| **Release / follow-up** | Decides `ALLOWED` or `DENIED` and writes the closing record | Doing the follow-up action (hand over, approve, trigger a process — or a payment under a payment binding) **only after** `ALLOWED`, and handling `DENIED` |
| **Replay and double release** | Defines nonce uniqueness and one-time consumption; implementations may keep this state in memory or durably | Choosing durable storage for production, backups, and never marking a deal consumed before the release really happened — or using the claim → complete protocol |
| **Time** | Compares timestamps with the agreed validity window | Trustworthy clocks, RFC 3339 timestamps |
| **Records and privacy** | Builds the `DealRecord` and its `chainHash`; stores hashes only | Storing records and artifacts, protecting delivered content, retention and deletion rules |
| **Disputes** | Nothing (a FAIL is final for the deal) | Any dispute, arbitration or legal process |
| **Payments** | Nothing in the core (optional bindings for AP2/x402/ERC-8183 exist outside it) | If you want money to move, the payment system and its binding |

## Typical integration checklist
1. Pick your **transport** and send the proposal, the countersignature, the input, the delivery and the verdict through it.
2. Pick your **identity/key source** and make the verifier load the parties' public keys from it (not from the bundle).
3. Decide **who the verifier is** (the requester's service, an independent third party, a deterministic service) and what it checks.
4. Keep replay and one-time-release state **durable** in anything that restarts or runs more than one process.
5. Perform your follow-up **only after** `ALLOWED`, using the claim → complete protocol if the follow-up has side effects.
6. Keep every exchanged file: any third party can re-verify the agreement later with an independent verifier.
