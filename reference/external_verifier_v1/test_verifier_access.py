"""Fail-closed TEST grant authorization. No private keys, payment rails or public enrollment API."""
import contextlib,copy,hashlib,hmac,json,os,secrets,threading,time,uuid
from pathlib import Path
from urllib.parse import urlsplit

PROFILE='adp.test-verifier/1'
MARKER={'version':'adp.synthetic-test/1','synthetic':True,'settlement':'TEST_ONLY_NO_PAYMENT'}
TOOLS=frozenset(('adp_read_deal','adp_get_verification','adp_submit_verification'))
PREFIX='adp-test-hop_'
_local=threading.local()
_lock=threading.RLock()
_hops={}

class Denied(Exception):pass

def denied():return {'error':'TEST authorization denied. A valid TEST profile, allowed tool and explicitly approved signed synthetic deal are required.','code':'TEST_AUTHORIZATION_DENIED','status':403}

def _json(path):
    try:
        value=json.loads(Path(path).read_text(encoding='utf-8-sig'))
        if not isinstance(value,dict) or value.get('version')!=1:raise Denied()
        return value
    except Exception:raise Denied() from None

def _registry():return _json(os.environ.get('ADP_EXTERNAL_VERIFIERS_PATH',''))

def _record(gid):
    import oauth_server as oauth
    if not gid:return None
    try:
        with oauth._lock:return oauth._db.execute('SELECT verifier_id,profile FROM test_verifier_grant_profiles WHERE grant_id=?',(gid,)).fetchone()
    except Exception:raise Denied() from None

def restricted(gid):
    if not gid:return False
    if _record(gid) is not None:return True
    # Incomplete enrollment cannot downgrade a registry-declared TEST principal to a legacy principal.
    try:
        for entry in _registry().get('verifiers',{}).values():
            if entry.get('testOnly') is True and gid in (entry.get('creatorGrantIds',[])+entry.get('verifierGrantIds',[])):return True
    except Denied:pass
    return False

def context(gid):
    row=_record(gid)
    if not row or row[1]!=PROFILE:raise Denied()
    policy=_json(os.environ.get('ADP_TEST_VERIFIER_POLICY_PATH',''))
    if policy.get('enabled') is not True:raise Denied()
    item=policy.get('grants',{}).get(gid)
    required={'enabled','profile','verifierId','publicKey','tools','apiActions','dealIds'}
    if not isinstance(item,dict) or set(item)!=required or item['enabled'] is not True or item['profile']!=PROFILE or item['verifierId']!=row[0]:raise Denied()
    tools=item['tools'];ids=item['dealIds']
    if not isinstance(tools,list) or not tools or any(not isinstance(t,str) for t in tools) or len(tools)!=len(set(tools)) or not set(tools)<=TOOLS or item['apiActions']!=[]:raise Denied()
    if not isinstance(ids,list) or len(ids)>100 or any(not isinstance(d,str) or str(uuid.UUID(d))!=d for d in ids) or len(ids)!=len(set(ids)):raise Denied()
    entry=_registry().get('verifiers',{}).get(row[0])
    if not isinstance(entry,dict) or entry.get('testOnly') is not True or entry.get('enabled') is not True or entry.get('publicKey')!=item['publicKey'] or gid not in entry.get('verifierGrantIds',[]):raise Denied()
    return policy,item

def _deal(gid,did,tool):
    from adp import models
    from adp.canonical import object_hash
    import playground_logic as pg,playground_v2 as v2
    policy,item=context(gid)
    if tool not in item['tools'] or did not in item['dealIds']:raise Denied()
    approval=policy.get('deals',{}).get(did)
    if not isinstance(approval,dict) or set(approval)!={'synthetic','acceptanceSpecHash','deliveryHash'} or approval['synthetic'] is not True:raise Denied()
    with __import__('runtime_state').LOCK:
        deal=pg._DEALS.get(did)
        if not isinstance(deal,dict):raise Denied()
        spec=deal['spec'];binding=spec['acceptanceCondition']['externalVerification']
        if binding.get('syntheticTest')!=MARKER or deal.get('externalVerification')!=binding:raise Denied()
        if binding['verifierId']!=item['verifierId'] or binding['publicKey']!=item['publicKey']:raise Denied()
        if spec['verifierAuthorization']!={'mode':'designated-key','verifierKeyId':item['verifierId'],'verifierPubKey':item['publicKey']}:raise Denied()
        if models.acceptance_spec_hash(spec)!=approval['acceptanceSpecHash'] or deal['specHash']!=approval['acceptanceSpecHash'] or not models.verify_acceptance_spec_signature_with_key(spec,pg._requester_kp.public_key_b64u):raise Denied()
        if not deal.get('delivery') or object_hash(deal['delivery'])!=approval['deliveryHash'] or deal['deliveryHash']!=approval['deliveryHash'] or not v2.has_provider_ack(did):raise Denied()
        if not __import__('external_verification').approved(binding['verifierId'],binding['publicKey'],binding['scope']):raise Denied()
        if not __import__('external_verification').now_valid(deal):raise Denied()
    return item

def prepare_test_binding(binding,synthetic_test):
    try:entry=_registry()['verifiers'][binding['verifierId']]
    except Exception:
        # Existing non-TEST normalization already rejects unavailable/unapproved registries.
        return denied()
    if entry.get('testOnly') is True and synthetic_test is not True:
        return {'error':'TEST verifier requires an operator-created synthetic test agreement.','code':'TEST_DEAL_REQUIRED','status':403}
    if synthetic_test is True:binding['syntheticTest']=copy.deepcopy(MARKER)
    return None

def register_test_grant(gid,verifier_id):
    """Operator-only local helper. Not exposed over HTTP/MCP. Use a fresh unused grant."""
    import oauth_server as oauth
    with oauth._lock:
        grant=oauth._db.execute('SELECT revoked,valid_until FROM grants WHERE id=?',(gid,)).fetchone()
        if not grant or grant[0] or grant[1]<=time.time() or oauth._db.execute('SELECT count(*) FROM tokens WHERE grant_id=?',(gid,)).fetchone()[0]:raise Denied()
        entry=_registry().get('verifiers',{}).get(verifier_id,{})
        if entry.get('testOnly') is not True or gid not in entry.get('verifierGrantIds',[]):raise Denied()
        oauth._db.execute('INSERT INTO test_verifier_grant_profiles(grant_id,verifier_id,profile) VALUES(?,?,?)',(gid,verifier_id,PROFILE))

def mcp_check(data,gid):
    try:
        if not restricted(gid):return None
        context(gid)
        method=data.get('method')
        if method in ('initialize','tools/list','ping','notifications/initialized','notifications/cancelled'):return None
        if method!='tools/call':raise Denied()
        params=data.get('params');args=params.get('arguments') if isinstance(params,dict) else None
        if not isinstance(args,dict):raise Denied()
        tool=params.get('name');allowed={'deal_id','verification_result','evidence'} if tool=='adp_submit_verification' else {'deal_id'}
        if tool not in TOOLS or set(args)-allowed or not isinstance(args.get('deal_id'),str):raise Denied()
        _deal(gid,args['deal_id'],tool)
        return None
    except Exception:return denied()

def filter_tools(response,gid):
    if not restricted(gid) or not isinstance(response,dict) or 'tools' not in response.get('result',{}):return response
    try:_,item=context(gid)
    except Exception:return {'jsonrpc':'2.0','id':response.get('id'),'result':{'isError':True,'content':[{'type':'text','text':json.dumps(denied())}]}}
    result=copy.deepcopy(response);result['result']['tools']=[tool for tool in result['result']['tools'] if tool['name'] in item['tools']]
    return result

def _request(data):
    params=data['params'];args=params['arguments'];did=args['deal_id'];tool=params['name']
    if tool=='adp_read_deal':return 'GET','/api/playground/external/deals/'+did,None
    if tool=='adp_get_verification':return 'GET','/api/playground/external/deals/'+did+'/verification',None
    if tool=='adp_submit_verification':return 'POST','/api/playground/external/deals/'+did+'/verification',{'verificationResult':args.get('verification_result'),'evidence':args.get('evidence')}
    raise Denied()

def _digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

@contextlib.contextmanager
def mcp_token(data,gid,headers,operator_token):
    if not restricted(gid) or data.get('method')!='tools/call':
        yield operator_token;return
    if mcp_check(data,gid):raise Denied()
    method,path,body=_request(data)
    token=PREFIX+secrets.token_urlsafe(32)
    # Original OAuth credential stays only in memory, never enters a URL/log/response.
    auth=headers.get('Authorization','');parent=auth[7:] if auth[:7].lower()=='bearer ' else ''
    record={'grant':gid,'tool':data['params']['name'],'deal':data['params']['arguments']['deal_id'],'method':method,'path':path,'digest':_digest(body),'expires':time.monotonic()+20,'parent':parent}
    with _lock:
        for old in list(_hops):
            if _hops[old]['expires']<time.monotonic():_hops.pop(old,None)
        _hops[token]=record
    try:yield token
    finally:
        with _lock:_hops.pop(token,None)

def _consume(handler,body):
    import oauth_server as oauth
    token=getattr(handler,'_test_hop',None)
    if not token:return None
    with _lock:record=_hops.pop(token,None)
    try:
        if not record or record['expires']<time.monotonic() or handler.client_address[0] not in ('127.0.0.1','::1'):raise Denied()
        if record['method']!=handler.command or record['path']!=handler.path or not hmac.compare_digest(record['digest'],_digest(body)):raise Denied()
        if oauth.validate_access(record['parent'])!=record['grant']:raise Denied()
        _deal(record['grant'],record['deal'],record['tool'])
        _local.validated=token
        return None
    except Exception:return denied()

def body_check(handler,body):return _consume(handler,body)

def install(app):
    import oauth_server as oauth
    # Additive authority marker survives missing/disabled/replaced policy files and service reopen.
    with oauth._lock:oauth._db.execute('CREATE TABLE IF NOT EXISTS test_verifier_grant_profiles(grant_id TEXT PRIMARY KEY REFERENCES grants(id),verifier_id TEXT NOT NULL,profile TEXT NOT NULL)')
    H=app.Handler;old_get,old_post=H.do_GET,H.do_POST;old_auth=app._external_auth_ok
    def auth(headers):
        bearer=headers.get('Authorization','')
        token=bearer[7:] if bearer[:7].lower()=='bearer ' else ''
        return bool(token and getattr(_local,'validated',None)==token) or old_auth(headers)
    app._external_auth_ok=auth
    def guard(handler):
        handler._test_hop=None;_local.validated=None
        auths=handler.headers.get_all('Authorization',[]);api_keys=handler.headers.get_all('x-api-key',[])
        candidates=[v[7:] for v in auths if v[:7].lower()=='bearer ']+api_keys
        for token in candidates:
            if token.startswith(PREFIX):
                if len(candidates)!=1:raise Denied()
                handler._test_hop=token
                if handler.command=='GET':
                    if _consume(handler,None):raise Denied()
                else:
                    with _lock:
                        record=_hops.get(token)
                        if not record or record['expires']<time.monotonic() or record['method']!=handler.command or record['path']!=handler.path or handler.client_address[0] not in ('127.0.0.1','::1'):raise Denied()
                return
        for token in candidates:
            with oauth._lock:
                row=oauth._db.execute('SELECT grant_id FROM tokens WHERE access_hash=?',(oauth.h(token),)).fetchone()
            if row and restricted(row[0]):
                if len(candidates)!=1 or api_keys or handler.command!='POST' or handler.path!='/mcp' or oauth.validate_access(token)!=row[0]:raise Denied()
                context(row[0])
    def wrap(original):
        def call(handler):
            try:
                try:guard(handler)
                except Exception:return handler._send_json(403,denied())
                return original(handler)
            finally:_local.validated=None
        return call
    H.do_GET,H.do_POST=wrap(old_get),wrap(old_post)
