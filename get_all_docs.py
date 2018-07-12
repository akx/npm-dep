import requests
import tqdm
import json

params = {
    'limit': 5000,
    'include_docs': 'true',
}

seen_ids = set()
with open('all_docs.jsonl', 'w') as outf:
    with requests.session() as s:
        with tqdm.tqdm(unit='pkg', unit_scale=True) as pbar:
            while True:
                resp = s.get('https://replicate.npmjs.com/registry/_all_docs', params=params)
                if resp.status_code > 200:
                    print(resp.content)
                    resp.raise_for_status()
                data = resp.json()
                pbar.total = data['total_rows']
                if not data.get('rows'):
                    break
                last_id = None
                for row in data['rows']:
                    if row['id'] in seen_ids:
                        continue
                    outf.write(json.dumps(row, ensure_ascii=False))
                    outf.write('\n')
                    seen_ids.add(row['id'])
                    last_id = row['id']
                params['startkey_docid'] = last_id
                pbar.set_description(last_id or '')
                pbar.update(len(seen_ids) - pbar.n)
                if last_id is None:  # No new rows!
                    break
