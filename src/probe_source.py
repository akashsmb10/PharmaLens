"""Source research probe: retain responses to verify NHSBSA filter semantics."""
import json
import urllib.parse
import urllib.request
from .common import ROOT, CONFIG, write_json

def main():
    meta = json.loads((ROOT / 'data/raw/source_metadata.json').read_text())['result']
    resource = next(r for r in meta['resources'] if r['name'] == 'PCA_202301')
    probes = {
        'known_string': {'filters': json.dumps({'BNF_CHEMICAL_SUBSTANCE_CODE': '0101010J0'})},
        'known_list': {'filters': json.dumps({'BNF_CHEMICAL_SUBSTANCE_CODE': ['0101010J0']})},
        'atorvastatin_name': {'filters': json.dumps({'BNF_CHEMICAL_SUBSTANCE': 'Atorvastatin'})},
        'atorvastatin_list': {'filters': json.dumps({'BNF_CHEMICAL_SUBSTANCE': ['Atorvastatin']})},
    }
    for label, extra in probes.items():
        url = CONFIG['api_base'] + 'datastore_search?' + urllib.parse.urlencode({'resource_id': resource['id'], 'limit': 3, **extra})
        try:
            with urllib.request.urlopen(url, timeout=60) as response:
                body = response.read()
            (ROOT / f'data/raw/probe_{label}.json').write_bytes(body)
            d = json.loads(body)
            print(label, d.get('success'), d.get('result', {}).get('records'), flush=True)
        except Exception as exc:
            print(label, str(exc), flush=True)

if __name__ == '__main__':
    main()
