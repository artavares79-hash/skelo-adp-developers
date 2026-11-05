# External Verifier V1 reference application extension

Publication snapshot: **v1-staging-2026-11-05**. The ADP specification remains **v0.1.2 draft**; wire objects remain `adp-acceptance/0.1` and `adp-verification/0.1`. This snapshot does not activate any hosted backend feature.

`external_verifier_v1/external_verification.py` and `test_verifier_access.py` are the actual tested staging modules, unchanged. `adp/` contains only the existing canonicalization, Ed25519, object-model and settlement primitives they use, not the full core implementation or all v0.1.2 conformance features. Source hashes are in `SOURCE-PROVENANCE.json`.

These are **host-bound application modules**, not a standalone production server. The private hosted backend, its deployment files and key material are not included. A host must bind the interfaces below before importing the modules. `tests/conftest.py` is an explicitly synthetic in-memory contract fixture; it is not a production persistence/authentication implementation. Public tests cover these actual modules against the fixture. Full HTTP/OAuth/MCP integration evidence from the separate staging host is documented separately, not claimed to run inside this fixture.

## Required host contracts

- `runtime_state.LOCK`: reentrant mutation lock; `durable` must atomically persist deal/results, acknowledgments, nonce and owner state with rollback before returning success. The fixture's in-memory lock is not sufficient for production.
- `playground_logic`: canonical `_DEALS`, independently pinned `_requester_kp`, internal `_verifier_kp` for typed gate receipts, and the existing `_engine` SettlementEngine.
- `playground_v2`: `verify_custom_deal(..., _external_structure=True)` returns actual structural checks without internally signing a professional verdict; `has_provider_ack` verifies the existing signed agreement/policy receipt. Creation, immutable delivery and authenticated read hooks use the existing v2 host.
- `oauth_server`: live `_db`, `_lock`, `h`, `validate_access`. Its existing grants/tokens are reused. TEST enrollment adds only `test_verifier_grant_profiles` and uses fresh unused grants; normal grants are not relabeled.
- HTTP host: `Handler.do_GET/do_POST`, `_send_json`, request method/path, parsed body, exact request headers and peer address; existing `_external_auth_ok`. Install `test_verifier_access.install(app)` after existing OAuth middleware and before serving traffic.

## Essential host wiring (pseudocode)

```python
# Authenticate and validate the MCP session first using existing middleware.
denied = external.mcp_rejection(request, authenticated, grant_id)
denied = denied or test_access.mcp_check(request, grant_id)
if denied:
    return mcp_tool_error(denied)
request = external.bind_mcp_context(request, grant_id)
with test_access.mcp_token(request, grant_id, headers, operator_token) as token:
    response = existing_mcp_adapter.handle_jsonrpc(request, token)
return test_access.filter_tools(response, grant_id)

# REST POST: after parsing JSON, BEFORE executing any operation:
denied = test_access.body_check(handler, parsed_json)
if denied:
    return http_error(denied)
```

Do not omit the HTTP guard or parsed-body check: TEST MCP calls receive one-use, method/path/body-bound loopback credentials instead of the operator token. Direct TEST REST credentials are denied. Existing legacy playground routes must refuse external-profile deal IDs; creation passes the operator-only `syntheticTest` flag to `external.create`. Reads, verification and immutable delivery must keep the V1 gate hooks. See the complete [integration contract](../docs/external-verifier-v1.md).

TEST policy and registry are operator-controlled, non-public files. They are fail-closed, pinned to signed synthetic deal/spec/delivery identities. Sample shapes in the documentation contain placeholders only. No registry is activated by importing this repository or running its tests.

## Run public checks

```sh
python -m pip install -r requirements-dev.txt
python -B -m pytest -q
python examples/python/external_verifier_client.py --self-test
```

Tests use generated in-memory synthetic identities only, never service credentials, Windows DPAPI, fixed private keys or live network endpoints. License/usage terms remain those stated in the repository README; publication does not introduce an open-source license or represent an independent security audit.
