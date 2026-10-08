"""Only publish known app files and validated official public data."""
import json
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]
PUBLIC_FIELDS={'id','title','organization','category','eligibility','start','deadline','url','description','source','periodText','publishedAt','tags'}
def stage():
    payload=json.loads((ROOT/'site/data/announcements.json').read_text())
    assert set(payload)=={'version','source','fetchedAt','items'}
    assert payload['version']==1 and payload['source']=='bizinfo'
    for item in payload['items']:
        assert set(item)<=PUBLIC_FIELDS and item['id'].startswith('bizinfo:') and item['source']=='bizinfo'
    destination=ROOT/'dist'
    if destination.exists():shutil.rmtree(destination)
    (destination/'data').mkdir(parents=True)
    for name in ['index.html','styles.css','app.js','core.js','favicon.svg']:
        shutil.copy2(ROOT/'site'/name,destination/name)
    (destination/'data/announcements.json').write_text(json.dumps(payload,ensure_ascii=False),encoding='utf-8')
    (destination/'.nojekyll').touch()
    print('Staged only six allowlisted public files and .nojekyll.')
if __name__=='__main__':stage()
