#!/usr/bin/env python3
"""Regenerate README.md from data/bookmarks.json + data/meta.json."""
import json,os,datetime,collections,re
root=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
B=[b for b in json.load(open(os.path.join(root,'data','bookmarks.json'),encoding='utf-8')) if not b.get('removed_at')]
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
o+=['','## 如何更新','','1. 准备 `new.json`（JSON 数组）。新书签必填 `id,url,title,summary,category,created_at`，可选 `author_username,author_name,text,bookmarked_order`；`category` 必须是 `data/categories.json` 里的一项。已有 id 只覆盖给出的字段（如只给 `id,text` 用于回填）。',
    '2. 运行 `python3 scripts/merge.py new.json --current current_ids.json`：按 id 合并、记录 `first_seen_at`；`current_ids.json` 是本次 X 接口返回的书签 id，必须保持接口原始顺序（新→旧，按翻页顺序拼接，不排序）。接口只返回最近一段，列表最后一条是其中最早收藏的；比它更新、却不在列表里的标记 `removed_at` 并在网页隐藏（数据保留，单次超过 30% 会拒绝）；更老的视为超出接口范围，保持不变。列表里的书签按接口顺序排，重新收藏的老帖会回到最前。翻页不完整时省略 `--current`。无变化时不写任何文件。',
    '3. 有改动时 `git add -A && git commit -m update && git push`，GitHub Pages 会自动更新网站。','']
open(os.path.join(root,'README.md'),'w',encoding='utf-8').write('\n'.join(o))
print('README regenerated')
