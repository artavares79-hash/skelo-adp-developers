"""Candidate MCP client and signed submission builder. No automatic live calls or key files."""
import argparse, datetime, json, sys, urllib.error, urllib.request, uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'reference'))
from adp import models
from adp.canonical import object_hash
from adp.crypto import Keypair, verify_object_signature

def build_submission(deal, keypair, artifacts, statuses):
    """The caller supplies a protected signing object; do not serialize its private key."""
    binding=deal['externalVerifier'];scope=[entry['id'] for entry in binding['scope']]
    if keypair.kid!=binding['verifierId'] or keypair.public_key_b64u!=binding['publicKey']:
        raise ValueError('Signing identity does not match the frozen verifier')
    if set(artifacts)!=set(scope) or set(statuses)!=set(scope):
        raise ValueError('Provide exactly the frozen mandatory criteria')
    if any(statuses[item] not in ('PASS','FAIL','NOT_VERIFIABLE') for item in scope):
        raise ValueError('Unknown criterion status')
    if object_hash(deal['canonicalDelivery'])!=deal['deliveryHashFull']:
        raise ValueError('Canonical delivery hash mismatch')
    if any(not isinstance(artifacts[item],dict) or not artifacts[item] for item in scope):
        raise ValueError('Nonempty structured artifacts required')
    refs=[{'criterionId':item,'status':statuses[item],'evidenceHash':object_hash(artifacts[item])} for item in scope]
    vr=models.build_verification_result(deal_id=deal['dealId'],acceptance_spec_hash=deal['acceptanceSpec']['acceptanceSpecHashFull'],
        delivery_hash=deal['deliveryHashFull'],verifier_id=keypair.kid,result='PASS' if all(statuses[item]=='PASS' for item in scope) else 'FAIL',
        evidence_refs=refs,timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),nonce=str(uuid.uuid4()))
    return {'deal_id':deal['dealId'],'verification_result':models.sign_verification_result(vr,keypair),
            'evidence':[{'criterionId':item,'artifact':artifacts[item]} for item in scope]}

class VerifierClient:
    """Use only an explicitly authorized staging MCP URL and existing OAuth access token.
    OAuth discovery/PKCE enrollment is described in docs; no operator REST token belongs here.
    """
    def __init__(self,mcp_url,access_token):
        if not access_token:raise ValueError('Missing OAuth access token')
        self.url=mcp_url;self._token=access_token;self._session=None
    def _rpc(self,method,params=None,notification=False):
        data={'jsonrpc':'2.0','method':method,'params':params or {}}
        if not notification:data['id']=str(uuid.uuid4())
        headers={'Content-Type':'application/json','Authorization':'Bearer '+self._token}
        if self._session:headers['Mcp-Session-Id']=self._session
        try:
            with urllib.request.urlopen(urllib.request.Request(self.url,json.dumps(data).encode(),headers),timeout=15) as response:
                if method=='initialize':self._session=response.headers.get('Mcp-Session-Id')
                raw=response.read();body=json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:raise RuntimeError('MCP HTTP request rejected: '+str(exc.code)) from None
        if body.get('error'):raise RuntimeError('MCP protocol rejected request')
        return body.get('result',{})
    def initialize(self):
        result=self._rpc('initialize',{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'synthetic-external-verifier-example','version':'1'}})
        self._rpc('notifications/initialized',notification=True)
        return result
    def call(self,name,arguments):
        if name not in ('adp_read_deal','adp_get_verification','adp_submit_verification'):
            raise ValueError('Outside TEST verifier scope')
        result=self._rpc('tools/call',{'name':name,'arguments':arguments})
        payload=json.loads(result['content'][0]['text'])
        if result.get('isError'):raise RuntimeError('Tool rejected request: '+str(payload.get('code','ERROR')))
        return payload

def self_test():
    # Generated in-memory synthetic identity only. No key bytes, files or network operations.
    kp=Keypair.generate('synthetic-example-only')
    delivery={'items':['SYNTHETIC INVOICE EUR 200']}
    deal={'dealId':str(uuid.uuid4()),'externalVerifier':{'verifierId':kp.kid,'publicKey':kp.public_key_b64u,'scope':[{'id':'total'}]},
          'acceptanceSpec':{'acceptanceSpecHashFull':'0'*64},'canonicalDelivery':delivery,'deliveryHashFull':object_hash(delivery)}
    result=build_submission(deal,kp,{'total':{'synthetic':True,'observedAmount':200}},{'total':'PASS'})
    vr=result['verification_result'];assert verify_object_signature({k:v for k,v in vr.items() if k!='signature'},vr['signature'],kp.public_key_b64u)
    print('PASS: synthetic signing/envelope self-test; no network, key files or settlement')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--self-test',action='store_true');args=parser.parse_args()
    if args.self_test:self_test()
    else:parser.print_help()
