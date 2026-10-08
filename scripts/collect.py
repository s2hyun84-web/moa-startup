#!/usr/bin/env python3
"""Collect public Bizinfo announcements only. Never print API URLs or credentials."""
import argparse
import datetime as dt
import html
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.parse import urlencode, urljoin, urlparse
from urllib.request import Request, urlopen

ENDPOINT = 'https://www.bizinfo.go.kr/uss/rss/bizinfoApi.do'
ROOT = Path(__file__).resolve().parents[1]

def text(value, limit=10000):
    return html.unescape(re.sub(r'<[^>]*>', ' ', str(value or ''))).strip()[:limit]

def date(value):
    try:
        result = dt.datetime.strptime(value, '%Y%m%d').date().isoformat()
        return result
    except ValueError:
        return ''

def dates(value):
    matches = re.findall(r'(?<!\d)(\d{4})[.\-/]?(\d{2})[.\-/]?(\d{2})(?!\d)', value)
    parsed = [date(''.join(m)) for m in matches]
    if len(parsed) == 2 and all(parsed) and parsed[0] <= parsed[1]:
        return parsed[0], parsed[1]
    return '', ''  # Budget exhaustion, ongoing or ambiguous periods have no invented deadline.

def category(raw, title):
    if re.search('경진|공모전|대회', title): return '경진대회'
    if raw == '기술' or re.search(r'R&D|연구개발', title, re.I): return 'R&D·기술'
    if re.search('교육|멘토링|컨설팅', title): return '교육·멘토링'
    return {'창업':'창업·사업화','금융':'금융','수출':'판로·수출','내수':'판로·수출','인력':'인력'}.get(raw, '기타')

def normalize(item):
    identifier = text(item.get('pblancId') or item.get('seq'), 180)
    if not re.fullmatch(r'[A-Za-z0-9_.:-]{1,180}', identifier): raise ValueError('invalid id')
    title = text(item.get('pblancNm') or item.get('title'), 200)
    if not title: raise ValueError('missing title')
    url = urljoin('https://www.bizinfo.go.kr', text(item.get('pblancUrl') or item.get('link'), 2000))
    parsed = urlparse(url)
    if parsed.scheme not in ('http','https') or parsed.hostname not in ('bizinfo.go.kr','www.bizinfo.go.kr') or parsed.username or parsed.password:
        raise ValueError('invalid official link')
    if not (item.get('pblancUrl') or item.get('link')): raise ValueError('missing official link')
    target = text(item.get('trgetNm'), 500)
    classification = title + ' ' + target
    eligibility=[]
    if re.search(r'예비\s*창업', classification): eligibility.append('예비창업자')
    if re.search(r'초기\s*창업|창업\s*초기', classification): eligibility.append('초기창업자')
    if re.search(r'여성\s*(창업|기업)', classification): eligibility.append('여성창업자')
    if '중소기업' in target: eligibility.append('중소기업')
    period=text(item.get('reqstBeginEndDe') or item.get('reqstDt'), 200)
    start, deadline=dates(period)
    description=text(item.get('bsnsSumryCn') or item.get('description'), 9000)
    if target: description += '\n\n공식 지원대상: ' + target
    return {'id':'bizinfo:'+identifier,'title':title,'organization':text(item.get('jrsdInsttNm') or item.get('author'),200),
            'category':category(text(item.get('pldirSportRealmLclasCodeNm') or item.get('lcategory')),title),
            'eligibility':eligibility or ['확인 필요'],'start':start,'deadline':deadline,'url':url,
            'description':description,'source':'bizinfo','periodText':period,
            'publishedAt':text(item.get('creatPnttm') or item.get('pubDate'),50),'tags':text(item.get('hashTags'),500)}

def unpack(payload):
    if not isinstance(payload,dict) or 'jsonArray' not in payload: raise ValueError('unexpected API response')
    container=payload['jsonArray']
    if isinstance(container,dict) and 'item' in container: rows=container['item']
    elif isinstance(container,list): rows=container
    else: raise ValueError('unexpected API schema')
    if isinstance(rows,dict): rows=[rows]
    if not isinstance(rows,list): raise ValueError('unexpected API items')
    totals=[int(r['totCnt']) for r in rows if isinstance(r,dict) and str(r.get('totCnt','')).isdigit()]
    if totals and max(totals)>len(rows): raise ValueError('incomplete API response')
    return list({r['id']:r for r in map(normalize,rows)}.values())

def fetch(key):
    query=urlencode({'crtfcKey':key,'dataType':'json','searchCnt':'0'})
    request=Request(ENDPOINT+'?'+query,headers={'Accept':'application/json','User-Agent':'MoaPersonalDesk/1.0'})
    for attempt in range(3):
        try:
            with urlopen(request,timeout=45) as response:
                # Hard cap avoids runaway responses without truncating silently.
                body=response.read(30*1024*1024+1)
                if len(body)>30*1024*1024: raise ValueError('response too large')
            return unpack(json.loads(body.decode('utf-8-sig')))
        except Exception:
            if attempt==2: raise RuntimeError('Official API collection failed: check key permissions, service availability, and response schema.') from None
            time.sleep(2**attempt)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT/'site/data/announcements.json');args=parser.parse_args()
    key=os.environ.get('BIZINFO_API_KEY','').strip()
    if not key:
        print('BIZINFO_API_KEY is missing. Set an Actions secret. No files were changed.',file=sys.stderr);return 1
    try:
        items=fetch(key)
        payload={'version':1,'source':'bizinfo','fetchedAt':dt.datetime.now(dt.timezone.utc).isoformat(),'items':items}
        args.output.parent.mkdir(parents=True,exist_ok=True)
        temporary=args.output.with_suffix('.tmp')
        temporary.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        temporary.replace(args.output)
        print(f'Collected {len(items)} public announcements. No personal records included.')
        return 0
    except Exception:
        # Do not log the exception: urllib errors can contain the secret query string.
        print('Collection failed. Existing data retained. Check API key, availability, and schema. Details intentionally redacted.',file=sys.stderr)
        return 1
if __name__=='__main__':sys.exit(main())
