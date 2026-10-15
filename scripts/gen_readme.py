#!/usr/bin/env python3
"""Regenerate README.md from data/bookmarks.json + data/meta.json."""
import json,os,datetime,collections,re
root=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
B=json.load(open(os.path.join(root,'data','bookmarks.json'),encoding='utf-8'))
M=json.load(open(os.path.join(root,'data','meta.json'),encoding='utf-8'))
tz=datetime.timezone(datetime.timedelta(hours=8))
dt=lambda s:datetime.datetime.fromisoformat(s.replace('Z','+00:00')).astimezone(tz)
g=collections.defaultdict(list)
for b in B:g[b['category']].append(b)
cs=sorted(g,key=lambda c:(-len(g[c]),c))
esc=lambda s:re.sub(r'([\[\]|*_`<>])',r'\\\1',str(s or ''))
o=['# X 书签可视化','','🔗 在线浏览（支持分类筛选与全文搜索）：**https://jiapeiyang.github.io/x-bookmarks/**','',
   f"共 **{M['total']}** 条书签 · 最后更新：{dt(M['updated_at']).strftime('%Y-%m-%d %H:%M')}（北京时间）",'','## 目录','']
o+=[f'- [{c}](#cat-{n}) — {len(g[c])} 条' for n,c in enumerate(cs)]
for n,c in enumerate(cs):
    o+=['',f'<a id="cat-{n}"></a>','',f'## {c}（{len(g[c])}）','']
    for b in sorted(g[c],key=lambda b:b['created_at'],reverse=True):
        o.append(f"- **[{esc(b['title'])}]({b['url']})** — {esc(b['summary'])}  \n  @{b.get('author_username','')} · {dt(b['created_at']).date()}")
o+=['','## 如何更新','','1. 准备 `new.json`（JSON 数组，必填字段 `id,url,title,summary,category,created_at`，可选 `author_username,author_name,text,bookmarked_order`）。',
    '2. 运行 `python3 scripts/merge.py new.json`：按 id 合并新书签、更新 `data/meta.json`，并自动重新生成本 README。',
    '3. `git add -A && git commit -m update && git push`，GitHub Pages 会自动更新网站。','']
open(os.path.join(root,'README.md'),'w',encoding='utf-8').write('\n'.join(o))
print('README regenerated')
