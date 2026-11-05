"""Opt-in external verification application profile. The frozen ADP core is unchanged."""
import base64
import copy
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from adp import models
from adp.canonical import object_hash
from adp.crypto import sign_object
import runtime_state

PROFILE = 'adp.external-verifier/1'
POLICY = 'adp.external-verifier.settlement/1'
ID = re.compile(r'^[A-Za-z0-9_.:-]{1,80}$')
HASH = re.compile(r'^[0-9a-f]{64}$')


def error(code, message, status=400):
    return {'error': message, 'code': code, 'status': status}


def profile(deal):
    return (deal or {}).get('externalVerification')


def is_external(deal_id):
    import playground_logic as pg
    return bool(profile(pg._DEALS.get(deal_id)))


def blocked_legacy_path(path):
    match = re.match(r'^/api/playground/(?:custom-)?deals/([^/?]+)', path)
    return bool(match and is_external(match[1]))


def mcp_rejection(data, authenticated, grant_id):
    if not isinstance(data, dict) or data.get('method') != 'tools/call':
        return None
    params = data.get('params') or {}
    if not isinstance(params, dict):
        return error('INVALID_ARGUMENTS', 'params must be an object.')
    args = params.get('arguments') or {}
    if not isinstance(args, dict):
        return error('INVALID_ARGUMENTS', 'arguments must be an object.')
    name = params.get('name')
    import playground_logic as pg
    deal_id = args.get('deal_id') or args.get('dealId')
    existing_deal = pg._DEALS.get(deal_id) if isinstance(deal_id, str) else None
    existing = profile(existing_deal)
    creating = name == 'adp_create_deal' and 'externalVerifier' in args
    if not (creating or existing or name == 'adp_submit_verification'):
        return None
    if not authenticated:
        return error('AUTHENTICATION_REQUIRED', 'External verification is available only through the authenticated MCP/API.', 401)
    # Existing static API credential is the operator credential. OAuth clients require explicit registry grants.
    if grant_id:
        binding = args.get('externalVerifier') if creating else existing
        try:
            registry = json.loads(Path(os.environ.get('ADP_EXTERNAL_VERIFIERS_PATH', '')).read_text(encoding='utf-8-sig'))
            entry = registry['verifiers'][binding['verifierId']]
            roles = ['verifierGrantIds'] if name == 'adp_submit_verification' else ['creatorGrantIds'] if creating or name in ('adp_acknowledge_deal', 'adp_submit_delivery') else ['creatorGrantIds', 'verifierGrantIds']
            allowed = approved(binding['verifierId'], binding['publicKey'], binding['scope']) and any(
                grant_id in entry.get(role, []) and (role == 'verifierGrantIds' or creating or existing_deal.get('externalOwnerGrantId') == grant_id)
                for role in roles)
            if creating and binding.get('supersedesDealId'):
                previous = pg._DEALS.get(binding['supersedesDealId']) or {}
                allowed = allowed and previous.get('externalOwnerGrantId') == grant_id
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            allowed = False
        if not allowed:
            return error('FORBIDDEN', 'OAuth grant is not authorized for this external-verifier operation.', 403)
    return None


def bind_mcp_context(data, grant_id):
    """Overwrite caller-supplied ownership using the authenticated server context."""
    if isinstance(data, dict) and data.get('method') == 'tools/call':
        params = data.get('params') or {}
        args = params.get('arguments') or {}
        if params.get('name') == 'adp_create_deal' and 'externalVerifier' in args:
            data = copy.deepcopy(data)
            data['params']['arguments']['_externalCreatorGrantId'] = grant_id
    return data


def public_tools(response):
    response = copy.deepcopy(response)
    tools = response.get('result', {}).get('tools', [])
    response['result']['tools'] = [tool for tool in tools if tool.get('name') != 'adp_submit_verification']
    for tool in response['result']['tools']:
        if tool.get('name') == 'adp_create_deal':
            tool['inputSchema']['properties'].pop('externalVerifier', None)
    return response


def approved(verifier_id, key, scope):
    """Operator-owned allowlist; caller cannot nominate an arbitrary trust root."""
    path = os.environ.get('ADP_EXTERNAL_VERIFIERS_PATH', '')
    try:
        registry = json.loads(Path(path).read_text(encoding='utf-8-sig'))
        entry = registry['verifiers'][verifier_id]
        return (registry.get('version') == 1 and entry.get('enabled') is True
                and entry.get('publicKey') == key
                and set(s['id'] for s in scope) <= set(entry.get('scopeIds', [])))
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return False


def normalize(value):
    if not isinstance(value, dict) or set(value) - {'verifierId', 'publicKey', 'scope', 'supersedesDealId'}:
        raise ValueError('externalVerifier requires verifierId, publicKey and scope; unknown fields are rejected.')
    kid, key, scope = value.get('verifierId'), value.get('publicKey'), value.get('scope')
    if not isinstance(kid, str) or not ID.fullmatch(kid) or not isinstance(key, str):
        raise ValueError('Invalid verifierId or publicKey.')
    raw = base64.b64decode(key + '=' * (-len(key) % 4), altchars=b'-_', validate=True)
    if len(raw) != 32 or base64.urlsafe_b64encode(raw).decode().rstrip('=') != key:
        raise ValueError('publicKey must be canonical base64url Ed25519 public-key bytes.')
    if not isinstance(scope, list) or not 1 <= len(scope) <= 10:
        raise ValueError('scope must contain 1 to 10 mandatory criteria.')
    ids = []
    for item in scope:
        if (not isinstance(item, dict) or set(item) != {'id', 'description'}
                or not isinstance(item['id'], str) or not ID.fullmatch(item['id'])
                or not isinstance(item['description'], str) or not 1 <= len(item['description'].strip()) <= 500):
            raise ValueError('Each scope entry requires a unique id and a nonempty description (max 500 characters).')
        ids.append(item['id'])
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate scope ids.')
    if not approved(kid, key, scope):
        raise ValueError('Verifier/key/scope is not enabled in the server trust registry.')
    result = {'version': PROFILE, 'verifierId': kid, 'publicKey': key, 'scope': copy.deepcopy(scope)}
    if 'supersedesDealId' in value:
        import playground_logic as pg
        import playground_v2 as v2
        previous = value['supersedesDealId']
        old = pg._DEALS.get(previous) if isinstance(previous, str) else None
        if not old or not v2._valid_deal_id(previous) or not profile(old) or not old.get('externalResults'):
            raise ValueError('supersedesDealId must reference an existing external review with a recorded result.')
        result['supersedesDealId'] = previous
    return result


@runtime_state.durable
def create(criteria, value, creator_grant_id=None, synthetic_test=False):
    import playground_logic as pg
    import playground_v2 as v2
    if os.environ.get('ADP_EXTERNAL_VERIFIER_CREATE_ENABLED', '').lower() != 'true':
        return error('EXTERNAL_PROFILE_DISABLED', 'New external-verifier deals are disabled.', 503)
    try:
        binding = normalize(value)
        if not isinstance(criteria, dict) or any(criteria.get(k) for k in ('claims', 'claimsRequired', 'customRequirement')):
            raise ValueError('Put mandatory professional criteria in externalVerifier.scope; legacy claims/customRequirement cannot be mixed into this profile.')
    except (ValueError, TypeError):
        return error('INVALID_EXTERNAL_VERIFIER', 'Invalid or unapproved externalVerifier. Supply an approved Ed25519 key and unique mandatory scope; use scope instead of legacy claim criteria.')
    import test_verifier_access as tv
    denied = tv.prepare_test_binding(binding, synthetic_test)
    if denied:
        return denied
    created = v2.create_custom_deal('External verifier deal; mandatory professional scope is signed in AcceptanceSpec.', criteria)
    if not created.get('dealId'):
        return error('INVALID_CRITERIA', 'At least one structural acceptance criterion is required.')
    deal = pg._DEALS[created['dealId']]
    deal['externalOwnerGrantId'] = creator_grant_id
    spec = copy.deepcopy(deal['spec'])
    spec['verifierAuthorization'] = {'mode': 'designated-key', 'verifierKeyId': binding['verifierId'], 'verifierPubKey': binding['publicKey']}
    spec['acceptanceCondition']['externalVerification'] = binding
    spec['verificationMethod']['description'] = 'Structural checks plus mandatory signed external criterion attestations with matching evidence artifacts.'
    spec['evidenceRequirements'] = ['external-criterion-attestation-v1']
    spec = models.sign_acceptance_spec(spec, pg._requester_kp)
    deal['spec'], deal['specHash'], deal['externalVerification'] = spec, models.acceptance_spec_hash(spec), binding
    policy = {'version': POLICY, 'acceptanceSpecHash': deal['specHash'], 'profile': binding,
              'rule': 'Structural PASS AND every mandatory external criterion PASS with signed bound evidence; otherwise NOT ELIGIBLE.',
              'conflictRule': 'Any distinct valid signed result after the first latches CONFLICT. Identical canonical retries are idempotent.',
              'reviewRule': 'No in-place review cycles. Create and acknowledge a new linked deal with a changed delivery.',
              'legacyCriteriaPolicyVersion': v2.VERIFICATION_SETTLEMENT_POLICY_VERSION}
    deal['verificationSettlementPolicy'] = {**policy, 'policyHash': object_hash(policy)}
    deal['externalResults'] = []
    return v2.external_get_deal(created['dealId'])


def read_extension(deal):
    if not profile(deal):
        return {}
    return {'externalVerifier': copy.deepcopy(profile(deal)), 'signedAcceptanceSpec': copy.deepcopy(deal['spec']),
            'canonicalDelivery': copy.deepcopy(deal.get('delivery')), 'deliveryHashFull': deal.get('deliveryHash'),
            'externalVerificationStatus': current(deal['spec']['dealId']) if deal.get('delivery') else 'DELIVERY_REQUIRED'}


def delivery_guard(deal, submission_hash):
    previous = (profile(deal) or {}).get('supersedesDealId')
    if previous:
        import playground_logic as pg
        if pg._DEALS[previous].get('deliverySubmissionHash') == submission_hash:
            return error('UNCHANGED_REVIEW_DELIVERY', 'A linked review requires changed delivery content.', 409)
    return None


def canonical_delivery_guard(deal, delivery):
    """Transport extras and server timestamps are not a new professional delivery."""
    previous = (profile(deal) or {}).get('supersedesDealId')
    if not previous:
        return None
    import playground_logic as pg
    def content(value):
        value = copy.deepcopy(value)
        for field in ('asOf', 'disclaimer'):
            value.pop(field, None)
        for source in value.get('sources', []):
            source.pop('retrievedAt', None)
        return value
    if object_hash(content(delivery)) == object_hash(content(pg._DEALS[previous]['delivery'])):
        return error('UNCHANGED_REVIEW_DELIVERY', 'A linked review requires changed canonical delivery content; timestamps or ignored fields do not count.', 409)
    return None


def now_valid(deal):
    try:
        now = datetime.now(timezone.utc)
        validity = deal['spec']['validity']
        return datetime.fromisoformat(validity['notBefore'].replace('Z', '+00:00')) <= now <= datetime.fromisoformat(validity['notAfter'].replace('Z', '+00:00'))
    except (ValueError, TypeError, KeyError):
        return False


def current(deal_id):
    import playground_logic as pg
    import playground_v2 as v2
    with runtime_state.LOCK:
        deal = pg._DEALS.get(deal_id)
        if not profile(deal):
            return error('EXTERNAL_PROFILE_REQUIRED', 'Deal does not use external verification.', 409)
        if not deal.get('delivery'):
            return error('DELIVERY_REQUIRED', 'Submit and bind the delivery before verification.', 409)
        structure = v2.verify_custom_deal(deal_id, _external_structure=True)
        checks = structure.get('checks', [])
        structural = 'PASS' if checks and all(c.get('status') == 'PASS' for c in checks) else 'FAIL'
        records = deal.get('externalResults', [])
        integrity = True
        try:
            if profile(deal) != deal['spec']['acceptanceCondition']['externalVerification']:
                raise ValueError('Profile differs from signed agreement.')
            if object_hash(deal['delivery']) != deal['deliveryHash'] or not v2.has_provider_ack(deal_id):
                raise ValueError('Delivery or acknowledgment binding failed.')
            policy = deal['verificationSettlementPolicy']
            if object_hash({k: v for k, v in policy.items() if k != 'policyHash'}) != policy['policyHash']:
                raise ValueError('Policy binding failed.')
            for record in records:
                vr = record['result']
                if object_hash(vr) != record['hash'] or vr['dealId'] != deal_id:
                    raise ValueError('Stored result binding failed.')
                validate_evidence(deal, vr, record['evidence'])
                decision = pg._engine.evaluate(spec=deal['spec'], issuer_pubkey_b64u=pg._requester_kp.public_key_b64u,
                    vr=vr, bound_acceptance_spec_hash=deal['specHash'], actual_delivery_hash=deal['deliveryHash'], register_nonce=False)
                if vr['result'] == 'PASS' and decision.decision.value != 'ALLOWED':
                    raise ValueError('Core release gate failed.')
        except Exception:
            integrity = False
        professional = 'NOT_VERIFIABLE'
        if not integrity:
            professional = 'NOT_VERIFIABLE'
        elif deal.get('externalConflict') or len(records) > 1:
            professional = 'CONFLICT'
        elif records:
            states = [r['status'] for r in records[0]['result']['evidenceRefs']]
            professional = 'FAIL' if 'FAIL' in states else 'PASS' if all(s == 'PASS' for s in states) else 'NOT_VERIFIABLE'
        p = profile(deal)
        authorized = approved(p['verifierId'], p['publicKey'], p['scope'])
        valid = now_valid(deal)
        eligible = structural == professional == 'PASS' and authorized and valid and integrity
        final = 'PASS' if eligible else 'FAIL' if structural == 'FAIL' or professional == 'FAIL' else 'INCONCLUSIVE'
        result = {'dealId': deal_id, 'profile': PROFILE, 'structuralStatus': structural,
                  'professionalStatus': professional, 'finalResult': final,
                  'settlementStatus': 'ELIGIBLE' if eligible else 'NOT ELIGIBLE',
                  'settlementDecision': 'ALLOWED' if eligible else 'DENIED',
                  'verifierCurrentlyAuthorized': authorized, 'withinValidity': valid, 'evidenceIntegrityValid': integrity,
                  'acceptanceSpecHash': deal['specHash'], 'deliveryHash': deal['deliveryHash'],
                  'policyHash': deal['verificationSettlementPolicy']['policyHash'],
                  'resultHashes': [r['hash'] for r in records], 'checks': checks}
        # Separate, explicitly typed application decision receipt; never forge the external signature.
        result['decisionReceipt'] = {'type': 'adp.external-gate/1', 'decision': copy.deepcopy(result),
                                     'signature': sign_object(result, pg._verifier_kp),
                                     'publicKey': pg._verifier_kp.public_key_b64u}
        return result


def validate_evidence(deal, vr, evidence):
    signature = vr.get('signature')
    if (not isinstance(signature, dict) or set(signature) != {'alg', 'kid', 'sig'}
            or signature['alg'] != 'EdDSA' or signature['kid'] != profile(deal)['verifierId']
            or not isinstance(signature['sig'], str)):
        raise ValueError('Signature envelope must identify the frozen verifier.')
    raw_signature = base64.b64decode(signature['sig'] + '=' * (-len(signature['sig']) % 4), altchars=b'-_', validate=True)
    if len(raw_signature) != 64 or base64.urlsafe_b64encode(raw_signature).decode().rstrip('=') != signature['sig']:
        raise ValueError('Signature encoding must be canonical Ed25519 base64url.')
    required = [s['id'] for s in profile(deal)['scope']]
    refs = vr.get('evidenceRefs')
    if not isinstance(refs, list) or len(refs) != len(required) or not isinstance(evidence, list) or len(evidence) != len(required):
        raise ValueError('One signed criterion result and one evidence artifact per mandatory criterion required.')
    if [r.get('criterionId') for r in refs if isinstance(r, dict)] != required:
        raise ValueError('Signed criterion results must match the frozen scope and order exactly.')
    if [e.get('criterionId') for e in evidence if isinstance(e, dict)] != required:
        raise ValueError('Evidence artifacts must match the frozen scope and order exactly.')
    for ref, item in zip(refs, evidence):
        if set(ref) != {'criterionId', 'status', 'evidenceHash'} or ref['status'] not in ('PASS', 'FAIL', 'NOT_VERIFIABLE'):
            raise ValueError('Invalid criterion result.')
        if set(item) != {'criterionId', 'artifact'} or not isinstance(item['artifact'], dict) or not item['artifact']:
            raise ValueError('A nonempty structured evidence artifact is required.')
        if not isinstance(ref['evidenceHash'], str) or not HASH.fullmatch(ref['evidenceHash']) or object_hash(item['artifact']) != ref['evidenceHash']:
            raise ValueError('Evidence artifact hash mismatch.')
    all_pass = all(r['status'] == 'PASS' for r in refs)
    if vr['result'] != ('PASS' if all_pass else 'FAIL'):
        raise ValueError('Signed overall result conflicts with mandatory criterion results.')


@runtime_state.durable
def submit(deal_id, payload):
    import playground_logic as pg
    import playground_v2 as v2
    with runtime_state.LOCK:
        deal = pg._DEALS.get(deal_id)
        if not profile(deal):
            return error('EXTERNAL_PROFILE_REQUIRED', 'External profile deal not found.', 404)
        if not deal.get('delivery') or not v2.has_provider_ack(deal_id):
            return error('DELIVERY_REQUIRED', 'A confirmed agreement and immutable delivery are required.', 409)
        if not isinstance(payload, dict) or set(payload) != {'verificationResult', 'evidence'}:
            return error('INVALID_VERIFICATION', 'Expected verificationResult and evidence.')
        vr, evidence = payload['verificationResult'], payload['evidence']
        p = profile(deal)
        if not approved(p['verifierId'], p['publicKey'], p['scope']):
            return error('UNAUTHORIZED_VERIFIER', 'Verifier is not currently enabled.', 403)
        if not now_valid(deal):
            return error('EXPIRED', 'Deal validity has ended or has not begun.', 409)
        try:
            if not isinstance(vr, dict) or set(vr) != set(models.VERIFICATION_RESULT_REQUIRED_FIELDS) | {'signature'}:
                raise ValueError('Invalid VerificationResult fields.')
            if not isinstance(vr['nonce'], str) or not 1 <= len(vr['nonce']) <= 128:
                raise ValueError('Invalid nonce.')
            signed_at = datetime.fromisoformat(vr['timestamp'].replace('Z', '+00:00'))
            if (signed_at - datetime.now(timezone.utc)).total_seconds() > 60:
                raise ValueError('Result timestamp is in the future.')
            actual_hash = object_hash(deal['delivery'])
            if actual_hash != deal['deliveryHash']:
                raise ValueError('Stored delivery binding failed.')
            decision = pg._engine.evaluate(spec=deal['spec'], issuer_pubkey_b64u=pg._requester_kp.public_key_b64u,
                        vr=vr, bound_acceptance_spec_hash=deal['specHash'], actual_delivery_hash=actual_hash, register_nonce=False)
            if decision.decision.value != 'ALLOWED' and vr.get('result') != 'FAIL':
                raise ValueError('Core rejected result binding.')
            # A valid FAIL can still be DENIED for a wrong deal; do not persist that as an authorized conflict.
            if vr['dealId'] != deal_id:
                raise ValueError('Wrong dealId.')
            validate_evidence(deal, vr, evidence)
            digest = object_hash(vr)
        except Exception:
            return error('INVALID_VERIFICATION', 'Result signature, authorization, binding, validity or criterion evidence is invalid.')
        records = deal['externalResults']
        if any(record['hash'] == digest for record in records):
            return {**current(deal_id), 'idempotent': True}
        if len(records) >= 2:
            return error('REVIEW_LOCKED', 'Conflicting review is locked. Use a new linked deal and changed delivery.', 409)
        try:
            pg._engine.check_and_register_nonce(vr)
        except ValueError:
            return error('REPLAY', 'Nonce already used for another signed result.', 409)
        records.append({'hash': digest, 'result': copy.deepcopy(vr), 'evidence': copy.deepcopy(evidence),
                        'receivedAt': datetime.now(timezone.utc).isoformat()})
        if len(records) > 1:
            deal['externalConflict'] = True
        result = current(deal_id)
        deal['state'] = 'EXTERNAL_' + result['professionalStatus']
        return result
