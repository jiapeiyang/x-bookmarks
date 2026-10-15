#!/usr/bin/env python3
"""Merge new categorized bookmarks into data/bookmarks.json by id.
Usage: python3 scripts/merge.py new.json
new.json: JSON array of objects with fields
  id,url,title,summary,category,author_username,author_name,created_at,text
  (bookmarked_order optional). Existing ids are kept unchanged; new ones are
  put first (newest bookmarks) and orders renumbered. meta.json is updated."""
import json,sys,datetime,os
root=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
bp=os.path.join(root,'data','bookmarks.json');mp=os.path.join(root,'data','meta.json')
old=json.load(open(bp,encoding='utf-8'));new=json.load(open(sys.argv[1],encoding='utf-8'))
ids={b['id'] for b in old};req=['id','url','title','summary','category','created_at']
add=[]
for b in new:
    if any(k not in b for k in req): sys.exit(f"missing field in {b.get('id')}: {req}")
    if b['id'] not in ids: ids.add(b['id']);add.append(b)
add.sort(key=lambda b:b.get('bookmarked_order',0))
allb=add+sorted(old,key=lambda b:b.get('bookmarked_order',0))
for n,b in enumerate(allb):
    b['bookmarked_order']=n
    for k in ('author_username','author_name','text'): b.setdefault(k,'')
json.dump(allb,open(bp,'w',encoding='utf-8'),ensure_ascii=False,indent=1)
tz=datetime.timezone(datetime.timedelta(hours=8))
json.dump({'total':len(allb),'updated_at':datetime.datetime.now(tz).isoformat(timespec='seconds')},open(mp,'w',encoding='utf-8'),ensure_ascii=False)
print(f"added {len(add)}, total {len(allb)}")
