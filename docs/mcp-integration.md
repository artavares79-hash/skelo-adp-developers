# MCP integration

## Availability

SKELO ADP provides an authenticated remote MCP integration. It is implemented and internally validated, but it is not a public self-service service.

## Integration approach

1. Request authorized integration access through SKELO.
2. Receive environment-specific endpoint and authentication instructions through an approved channel.
3. Initialize an MCP session with the supported protocol version.
4. Discover the tools exposed to the authenticated session.
5. Test only with synthetic, non-sensitive data before connecting a business workflow.

MCP gives compatible clients a structured discovery and invocation surface. ADP applies its agreement and verification rules; the client remains responsible for agent behavior, data handling, and settlement decisions.

This repository deliberately does not publish credentials, internal tool schemas, private test vectors, production configuration, or implementation details outside the approved public contract.
