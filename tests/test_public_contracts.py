import hashlib,importlib.util,json,re
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]

def test_published_source_hashes_match_provenance():
    data=json.loads((ROOT/'reference'/'SOURCE-PROVENANCE.json').read_text())
    for name,entry in data['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==entry['sha256']

def test_real_candidate_mcp_and_api_schema():
    data=json.loads((ROOT/'schemas'/'external-verifier-v1-mcp.json').read_text());assert len(data['tools'])==6
    submit=next(t for t in data['tools'] if t['name']=='adp_submit_verification')['inputSchema']
    assert submit['required']==['deal_id','verification_result','evidence']
    assert set(submit['properties']['verification_result']['required'])=={'resultVersion','dealId','acceptanceSpecHash','deliveryHash','verifierId','result','evidenceRefs','timestamp','nonce','signature'}
    api=json.loads((ROOT/'schemas'/'external-verifier-v1.openapi.json').read_text())
    assert api['openapi']=='3.1.0' and set(api['paths']['/api/playground/external/deals/{deal_id}/verification'])=={'parameters','get','post'}
    assert 'not active' in data['availability'].lower()

def test_example_uses_matching_key_and_delivery(host):
    from external_verifier_client import build_submission
    from adp.crypto import Keypair
    did=host.deal();data=host.read(did)
    with pytest.raises(ValueError):build_submission(data,Keypair.generate('unapproved'),{'total':{'synthetic':True}},{'total':'PASS'})
    data['deliveryHashFull']='0'*64
    with pytest.raises(ValueError):build_submission(data,host.external,{'total':{'synthetic':True}},{'total':'PASS'})

def test_markdown_links_resolve_and_no_local_paths():
    for path in ROOT.rglob('*.md'):
        if '.git' in path.parts or '.pytest_cache' in path.parts:continue
        text=path.read_text(encoding='utf8');assert not re.search(r'[A-Z]:\\',text),str(path)
        for url in re.findall(r'\]\(([^)]+)\)',text):
            target=url.split('#')[0]
            if not target or '://' in target or target.startswith('mailto:'):continue
            assert (path.parent/target).exists(),(str(path),url)

def test_publication_is_staging_not_hosted_activation():
    readme=(ROOT/'README.md').read_text(encoding='utf8')
    assert 'Not enabled on the hosted production service' in readme
    assert not any(ROOT.rglob('*.pem')) and not any(ROOT.rglob('*.dpapi')) and not any(ROOT.rglob('*.sqlite3'))
