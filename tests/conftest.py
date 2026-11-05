"""Portable synthetic host CONTRACT fixture, not the private HTTP/SQLite production host."""
import copy,datetime,functools,hashlib,importlib,json,secrets,sqlite3,sys,threading,types,uuid
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'reference'))
sys.path.insert(0,str(ROOT/'examples'/'python'))
from adp import models
from adp.canonical import object_hash
from adp.crypto import Keypair

@pytest.fixture
def host(monkeypatch,tmp_path):
    runtime=types.ModuleType('runtime_state');runtime.LOCK=threading.RLock()
    def durable(fn):
        @functools.wraps(fn)
        def call(*args,**kwargs):
            with runtime.LOCK:return fn(*args,**kwargs)
        return call
    runtime.durable=durable
    pg=types.ModuleType('playground_logic');pg._DEALS={};pg._requester_kp=Keypair.generate('synthetic-issuer');pg._verifier_kp=Keypair.generate('synthetic-gate')
    from adp.settlement import SettlementEngine
    pg._engine=SettlementEngine();v2=types.ModuleType('playground_v2');acks=set()
    v2.has_provider_ack=lambda did:did in acks
    v2.VERIFICATION_SETTLEMENT_POLICY_VERSION='adp.verification-settlement/4'
    def structural(did,**_):
        deal=pg._DEALS[did];valid=models.acceptance_spec_hash(deal['spec'])==deal['specHash'] and models.verify_acceptance_spec_signature_with_key(deal['spec'],pg._requester_kp.public_key_b64u)
        return {'checks':[{'name':'signedSpec','status':'PASS' if valid else 'FAIL'},{'name':'itemCount','status':'PASS' if len(deal['delivery']['items'])==1 else 'FAIL'}]}
    v2.verify_custom_deal=structural
    v2._valid_deal_id=lambda did:str(uuid.UUID(did))==did
    oauth=types.ModuleType('oauth_server');oauth._lock=threading.RLock();oauth._db=sqlite3.connect(':memory:',check_same_thread=False,isolation_level=None)
    oauth._db.executescript('CREATE TABLE grants(id TEXT PRIMARY KEY,revoked INTEGER,valid_until INTEGER); CREATE TABLE tokens(access_hash TEXT PRIMARY KEY,grant_id TEXT);')
    oauth.h=lambda value:hashlib.sha256(value.encode()).hexdigest()
    def validate(token):
        row=oauth._db.execute('SELECT g.id,g.revoked,g.valid_until FROM tokens t JOIN grants g ON g.id=t.grant_id WHERE t.access_hash=?',(oauth.h(token),)).fetchone()
        return row[0] if row and not row[1] and row[2]>datetime.datetime.now().timestamp() else None
    oauth.validate_access=validate
    for mod in (runtime,pg,v2,oauth):monkeypatch.setitem(sys.modules,mod.__name__,mod)
    for name in ('external_verifier_v1.external_verification','external_verifier_v1.test_verifier_access'):sys.modules.pop(name,None)
    ev=importlib.import_module('external_verifier_v1.external_verification');tv=importlib.import_module('external_verifier_v1.test_verifier_access')
    # Actual modules intentionally import this name in the documented host wiring.
    monkeypatch.setitem(sys.modules,'external_verification',ev);monkeypatch.setitem(sys.modules,'test_verifier_access',tv)
    class Handler:
        def do_GET(self):self.authAtExecution=app._external_auth_ok(self.headers);self.status=200
        def do_POST(self):self.status=200
        def _send_json(self,status,body):self.status=status;self.body=body
    app=types.SimpleNamespace(Handler=Handler,_external_auth_ok=lambda _:False)
    tv.install(app)
    external=Keypair.generate('synthetic-specialist');gid='synthetic-review-grant';token=secrets.token_urlsafe(32)
    oauth._db.execute('INSERT INTO grants VALUES(?,?,?)',(gid,0,(datetime.datetime.now()+datetime.timedelta(hours=1)).timestamp()))
    registry={'version':1,'verifiers':{external.kid:{'enabled':True,'publicKey':external.public_key_b64u,'scopeIds':['total'],'creatorGrantIds':[],'verifierGrantIds':[gid],'testOnly':True}}}
    registry_path=tmp_path/'registry.json';registry_path.write_text(json.dumps(registry));monkeypatch.setenv('ADP_EXTERNAL_VERIFIERS_PATH',str(registry_path))
    tv.register_test_grant(gid,external.kid);oauth._db.execute('INSERT INTO tokens VALUES(?,?)',(oauth.h(token),gid))
    policy={'version':1,'enabled':True,'grants':{gid:{'enabled':True,'profile':tv.PROFILE,'verifierId':external.kid,'publicKey':external.public_key_b64u,'tools':sorted(tv.TOOLS),'apiActions':[],'dealIds':[]}},'deals':{}}
    policy_path=tmp_path/'policy.json';monkeypatch.setenv('ADP_TEST_VERIFIER_POLICY_PATH',str(policy_path))
    def save():registry_path.write_text(json.dumps(registry));policy_path.write_text(json.dumps(policy))
    def deal(synthetic=True):
        did=str(uuid.uuid4());now=datetime.datetime.now(datetime.timezone.utc)
        binding={'version':ev.PROFILE,'verifierId':external.kid,'publicKey':external.public_key_b64u,'scope':[{'id':'total','description':'Synthetic invoice must equal EUR 200'}]}
        if synthetic:binding['syntheticTest']=copy.deepcopy(tv.MARKER)
        spec=models.build_acceptance_spec(deal_id=did,subject_hash=object_hash({'synthetic':True}),verification_method={'type':'sandboxed-test-suite'},acceptance_condition={'externalVerification':binding},verifier_authorization={'mode':'designated-key','verifierKeyId':external.kid,'verifierPubKey':external.public_key_b64u},not_before=(now-datetime.timedelta(minutes=1)).isoformat(),not_after=(now+datetime.timedelta(hours=1)).isoformat(),evidence_requirements=['external-criterion-attestation-v1'],issuer=pg._requester_kp.kid)
        spec=models.sign_acceptance_spec(spec,pg._requester_kp);delivery={'items':['SYNTHETIC EUR 200']};spec_hash=models.acceptance_spec_hash(spec)
        rule={'version':ev.POLICY,'acceptanceSpecHash':spec_hash,'profile':copy.deepcopy(binding)}
        value={'spec':spec,'specHash':spec_hash,'externalVerification':copy.deepcopy(binding),'delivery':delivery,'deliveryHash':object_hash(delivery),'verificationSettlementPolicy':{**rule,'policyHash':object_hash(rule)},'externalResults':[],'state':'DELIVERED'}
        pg._DEALS[did]=value;acks.add(did)
        policy['grants'][gid]['dealIds'].append(did);policy['deals'][did]={'synthetic':True,'acceptanceSpecHash':spec_hash,'deliveryHash':value['deliveryHash']};save();return did
    def read(did):
        d=pg._DEALS[did]
        return {'dealId':did,'externalVerifier':copy.deepcopy(d['externalVerification']),'acceptanceSpec':{'acceptanceSpecHashFull':d['specHash']},'canonicalDelivery':copy.deepcopy(d['delivery']),'deliveryHashFull':d['deliveryHash']}
    save()
    yield types.SimpleNamespace(ev=ev,tv=tv,pg=pg,oauth=oauth,app=app,external=external,gid=gid,token=token,registry=registry,policy=policy,policy_path=policy_path,save=save,deal=deal,read=read,acks=acks)
    oauth._db.close()
