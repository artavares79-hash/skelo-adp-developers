import copy,json,uuid
import pytest
from external_verifier_client import build_submission

def packet(host,did,status='PASS'):
    result=build_submission(host.read(did),host.external,{'total':{'synthetic':True,'observedAmount':200 if status=='PASS' else 999}},{'total':status})
    return {'verificationResult':result['verification_result'],'evidence':result['evidence']}

@pytest.mark.parametrize('status,final,gate',[('PASS','PASS','ALLOWED'),('FAIL','FAIL','DENIED'),('NOT_VERIFIABLE','INCONCLUSIVE','DENIED')])
def test_signed_criterion_outcomes(host,status,final,gate):
    did=host.deal();result=host.ev.submit(did,packet(host,did,status));assert (result['finalResult'],result['settlementDecision'])==(final,gate)

def test_missing_and_structure_fail_closed(host):
    did=host.deal();assert host.ev.current(did)['settlementDecision']=='DENIED'
    host.pg._DEALS[did]['delivery']['items']=[]
    from adp.canonical import object_hash
    host.pg._DEALS[did]['deliveryHash']=object_hash(host.pg._DEALS[did]['delivery'])
    assert host.ev.submit(did,packet(host,did))['settlementDecision']=='DENIED'

@pytest.mark.parametrize('attack',['signature','deal','spec','delivery','verifier','artifact','scope','missing'])
def test_invalid_attestations_not_saved(host,attack):
    from adp import models
    did=host.deal();p=packet(host,did);vr=p['verificationResult']
    if attack=='signature':vr['signature']['sig']='A'*86
    elif attack in ('deal','spec','delivery','verifier'):
        vr[{'deal':'dealId','spec':'acceptanceSpecHash','delivery':'deliveryHash','verifier':'verifierId'}[attack]]='wrong';p['verificationResult']=models.sign_verification_result(vr,host.external)
    elif attack=='artifact':p['evidence'][0]['artifact']['observedAmount']=999
    elif attack=='scope':vr['evidenceRefs'][0]['criterionId']='not-agreed';p['verificationResult']=models.sign_verification_result(vr,host.external)
    elif attack=='missing':p['evidence']=[]
    assert host.ev.submit(did,p)['code']=='INVALID_VERIFICATION';assert not host.pg._DEALS[did]['externalResults']

def test_conflict_and_identical_retry(host):
    did=host.deal();first=packet(host,did,'FAIL');host.ev.submit(did,first)
    assert host.ev.submit(did,first)['idempotent']
    assert host.ev.submit(did,packet(host,did))['professionalStatus']=='CONFLICT'
    assert host.ev.current(did)['settlementDecision']=='DENIED' and len(host.pg._DEALS[did]['externalResults'])==2

def test_nonce_replay_denied(host):
    from adp import models
    did=host.deal();first=packet(host,did,'FAIL');host.ev.submit(did,first)
    second=packet(host,did);second['verificationResult']['nonce']=first['verificationResult']['nonce'];second['verificationResult']=models.sign_verification_result(second['verificationResult'],host.external)
    assert host.ev.submit(did,second)['code']=='REPLAY'

@pytest.mark.parametrize('attack',['result','delivery','evidence','policy','ack','revocation'])
def test_later_integrity_and_revocation_rechecked(host,attack):
    did=host.deal();host.ev.submit(did,packet(host,did));d=host.pg._DEALS[did]
    if attack=='result':d['externalResults'][0]['result']['signature']['sig']='invalid'
    if attack=='delivery':d['delivery']['items']=['changed']
    if attack=='evidence':d['externalResults'][0]['evidence'][0]['artifact']['observedAmount']=999
    if attack=='policy':d['verificationSettlementPolicy']['rule']='changed'
    if attack=='ack':host.acks.remove(did)
    if attack=='revocation':host.registry['verifiers'][host.external.kid]['enabled']=False;host.save()
    assert host.ev.current(did)['settlementDecision']=='DENIED'

def test_signed_gate_receipt_pinned(host):
    from adp.crypto import verify_object_signature
    did=host.deal();result=host.ev.submit(did,packet(host,did));receipt=result['decisionReceipt']
    assert receipt['publicKey']==host.pg._verifier_kp.public_key_b64u
    assert verify_object_signature(receipt['decision'],receipt['signature'],host.pg._verifier_kp.public_key_b64u)

def test_allowed_test_tool_and_unmarked_history(host):
    did=host.deal();data={'method':'tools/call','params':{'name':'adp_read_deal','arguments':{'deal_id':did}}}
    assert host.tv.mcp_check(data,host.gid) is None
    old=host.deal(synthetic=False);data['params']['arguments']['deal_id']=old
    before=copy.deepcopy(host.pg._DEALS[old]);assert host.tv.mcp_check(data,host.gid)['status']==403;assert host.pg._DEALS[old]==before

@pytest.mark.parametrize('tool',['adp_create_deal','adp_acknowledge_deal','adp_submit_delivery','unknown'])
def test_forbidden_test_tools(host,tool):
    did=host.deal();assert host.tv.mcp_check({'method':'tools/call','params':{'name':tool,'arguments':{'deal_id':did}}},host.gid)['status']==403

@pytest.mark.parametrize('attack',['profile','tools','api','deal','grant','disabled','missing_file'])
def test_missing_manipulated_policy_never_downgrades(host,attack):
    did=host.deal();p=host.policy['grants'][host.gid]
    if attack=='profile':p.pop('profile')
    if attack=='tools':p['tools'].append('adp_create_deal')
    if attack=='api':p['apiActions']=['*']
    if attack=='deal':p['dealIds']=[]
    if attack=='grant':host.policy['grants']={}
    if attack=='disabled':host.policy['enabled']=False
    host.save()
    if attack=='missing_file':host.policy_path.unlink()
    assert host.tv.restricted(host.gid)
    assert host.tv.mcp_check({'method':'tools/call','params':{'name':'adp_read_deal','arguments':{'deal_id':did}}},host.gid)['status']==403

def handler(host,method,path,token,api=False):
    from email.message import Message
    h=host.app.Handler();h.headers=Message();h.headers['x-api-key' if api else 'Authorization']=token if api else 'Bearer '+token
    h.command=method;h.path=path;h.client_address=('127.0.0.1',12345);return h

@pytest.mark.parametrize('path',['/api/playground/deals','/api/playground/external/deals','/mcp-public','/api/demo/start'])
def test_direct_test_credentials_rejected_by_actual_guard(host,path):
    h=handler(host,'POST',path,host.token);h.do_POST();assert h.status==403

def test_api_key_rejected_and_normal_client_unchanged(host):
    h=handler(host,'POST','/mcp',host.token,api=True);h.do_POST();assert h.status==403
    h=handler(host,'POST','/mcp','synthetic-unrelated-client');h.do_POST();assert h.status==200

def test_one_time_request_bound_internal_hop(host):
    from email.message import Message
    did=host.deal();headers=Message();headers['Authorization']='Bearer '+host.token
    data={'method':'tools/call','params':{'name':'adp_read_deal','arguments':{'deal_id':did}}}
    with host.tv.mcp_token(data,host.gid,headers,'never-forward-operator-placeholder') as token:
        h=handler(host,'GET','/api/playground/external/deals/'+did,token);h.do_GET();assert h.status==200 and h.authAtExecution
        assert not host.app._external_auth_ok(h.headers) # request-local authority was cleared
        h=handler(host,'GET','/api/playground/external/deals/'+did,token);h.do_GET();assert h.status==403

def test_verifier_cannot_self_mark_or_use_unknown_deal(host):
    with pytest.raises(host.tv.Denied):host.tv.register_test_grant('unknown-grant',host.external.kid)
    assert host.tv.mcp_check({'method':'tools/call','params':{'name':'adp_read_deal','arguments':{'deal_id':str(uuid.uuid4())}}},host.gid)['status']==403
