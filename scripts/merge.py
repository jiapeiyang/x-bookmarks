#!/usr/bin/env python3
"""Merge categorized bookmarks into data/bookmarks.json by id.
Usage: python3 scripts/merge.py new.json [--current current_ids.json]
new.json: JSON array of objects.
  - New id: required id,url,title,summary,category,created_at; optional
    author_username,author_name,text,bookmarked_order. New ones are put first
    (newest bookmarks), orders renumbered, first_seen_at set to today.
  - Existing id: only the fields given are overwritten (e.g. {id,text} to
    backfill expanded links); bookmarked_order/first_seen_at are kept.
  category must be one of data/categories.json.
--current: JSON array of ALL ids bookmarked on X right now (only pass it when
  pagination fully succeeded). Missing ones get removed_at and are hidden on
  the site (data kept); ones bookmarked again are restored. Refuses to hide
  more than 30% of active bookmarks at once.
Writes nothing when nothing changed; otherwise updates meta.json and
regenerates README."""
import json,sys,datetime,os,argparse,subprocess
here=os.path.dirname(os.path.abspath(__file__));root=os.path.join(here,'..')
bp=os.path.join(root,'data','bookmarks.json');mp=os.path.join(root,'data','meta.json')
ap=argparse.ArgumentParser();ap.add_argument('new');ap.add_argument('--current');a=ap.parse_args()
old=json.load(open(bp,encoding='utf-8'));new=json.load(open(a.new,encoding='utf-8'))
cats=json.load(open(os.path.join(root,'data','categories.json'),encoding='utf-8'))
tz=datetime.timezone(datetime.timedelta(hours=8));now=datetime.datetime.now(tz);today=now.date().isoformat()
by={b['id']:b for b in old};req=['id','url','title','summary','category','created_at']
upd_keys=('url','title','summary','category','created_at','author_username','author_name','text')
add=[];upd=0
for b in new:
    if 'id' not in b: sys.exit(f"missing id: {b}")
    b['id']=str(b['id'])
    if 'category' in b and b['category'] not in cats: sys.exit(f"unknown category {b['category']!r} in {b['id']}, allowed: {cats}")
    o=by.get(b['id'])
    if o:
        ch={k:b[k] for k in upd_keys if k in b and b[k]!=o.get(k)}
        if ch: o.update(ch);upd+=1
    else:
        miss=[k for k in req if k not in b]
        if miss: sys.exit(f"missing field in {b['id']}: {miss}")
        b['first_seen_at']=today;by[b['id']]=b;add.append(b)
rm=back=0
if a.current:
    cur={str(i) for i in json.load(open(a.current,encoding='utf-8'))}
    for b in old:
        if b.get('removed_at') and b['id'] in cur: del b['removed_at'];back+=1
    act=[b for b in old if not b.get('removed_at')]
    gone=[b for b in act if b['id'] not in cur]
    # 翻页不完整时 current 会缺一大片，宁可报错也不批量隐藏
    if len(gone)>0.3*len(act): sys.exit(f"refusing to hide {len(gone)}/{len(act)} bookmarks (>30%), current ids look incomplete")
    for b in gone: b['removed_at']=today;rm+=1
if not (add or upd or rm or back):
    print('no changes');sys.exit(0)
add.sort(key=lambda b:b.get('bookmarked_order',0))
allb=add+sorted(old,key=lambda b:b.get('bookmarked_order',0))
for n,b in enumerate(allb):
    b['bookmarked_order']=n
    for k in ('author_username','author_name','text'): b.setdefault(k,'')
json.dump(allb,open(bp,'w',encoding='utf-8'),ensure_ascii=False,indent=1)
total=sum(1 for b in allb if not b.get('removed_at'))
json.dump({'total':total,'updated_at':now.isoformat(timespec='seconds')},open(mp,'w',encoding='utf-8'),ensure_ascii=False)
print(f"added {len(add)}, updated {upd}, removed {rm}, restored {back}, total {total}")
subprocess.run([sys.executable,os.path.join(here,'gen_readme.py')],check=True)
