const $=s=>document.querySelector(s);let all=[],cat='全部',cur=null;
const esc=s=>String(s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const day=s=>new Date(s).toLocaleDateString('sv-SE',{timeZone:'Asia/Shanghai'});
const reEsc=s=>s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
const terms=()=>$('#q').value.trim().toLowerCase().split(/\s+/).filter(Boolean);
// 先在原文上切分再逐段转义，避免高亮命中 &amp; 之类的实体
const hl=(s,t)=>{s=String(s||'');if(!t.length)return esc(s);
 const re=new RegExp(`(${[...t].sort((a,b)=>b.length-a.length).map(reEsc).join('|')})`,'gi');
 return s.split(re).map((p,i)=>i%2?`<mark>${esc(p)}</mark>`:esc(p)).join('')};
const xurl=u=>/^https:\/\/(x|twitter)\.com\//.test(u)?u:'#';
const lnk=s=>esc(s).replace(/https?:\/\/[^\s<]+/g,u=>`<a href="${u}" target="_blank" rel="noopener">${u}</a>`);
const vis=b=>[b.title,b.summary,b.author_name,b.author_username].join(' ').toLowerCase();
// 命中词只出现在正文里时，截一段正文说明为什么匹配
function snip(b,t){const v=vis(b),w=t.find(w=>!v.includes(w));if(!w)return'';
 const tx=b.text.replace(/\s+/g,' '),i=tx.toLowerCase().indexOf(w);if(i<0)return'';
 const a=Math.max(0,i-30),z=Math.min(tx.length,i+w.length+60);
 return `<p class="snip">${a?'…':''}${hl(tx.slice(a,z),t)}${z<tx.length?'…':''}</p>`}
function save(){const p=new URLSearchParams(),q=$('#q').value.trim(),s=$('#sort').value;
 if(cat!='全部')p.set('c',cat);if(q)p.set('q',q);if(s!='bm')p.set('s',s);if(cur)p.set('id',cur);
 const h=p.toString();history.replaceState(null,'',h?'#'+h:location.pathname+location.search)}
function cats(){const c={};all.forEach(b=>c[b.category]=(c[b.category]||0)+1);
 const L=[['全部',all.length],...Object.entries(c).sort((a,b)=>b[1]-a[1])];
 $('#cats').innerHTML=L.map(([n,k])=>`<button class="chip${n==cat?' on':''}" data-c="${esc(n)}">${esc(n)}<b>${k}</b></button>`).join('');
 document.querySelectorAll('.chip').forEach(e=>e.onclick=()=>{cat=e.dataset.c;cats();render()})}
function render(){const t=terms(),s=$('#sort').value;
 let r=all.filter(b=>(cat=='全部'||b.category==cat)&&t.every(w=>b._h.includes(w)));
 r.sort(s=='bm'?(a,b)=>a.bookmarked_order-b.bookmarked_order:s=='new'?(a,b)=>b.created_at.localeCompare(a.created_at):(a,b)=>a.created_at.localeCompare(b.created_at));
 $('#count').textContent=`显示 ${r.length} 条`;
 $('#list').innerHTML=r.map(b=>`<article class="card"><span class="tag">${esc(b.category)}</span><h3><button class="open" data-id="${esc(b.id)}">${hl(b.title,t)}</button></h3><p>${hl(b.summary,t)}</p>${t.length?snip(b,t):''}<div class="foot"><span class="au">${hl((b.author_name||'')+' @'+b.author_username,t)}</span><span class="dt">· ${day(b.created_at)}</span><a href="${esc(xurl(b.url))}" target="_blank" rel="noopener">原帖 ↗</a></div></article>`).join('')||'<p class="muted">没有匹配的书签</p>';
 save()}
function openD(id){const b=all.find(b=>b.id==id);if(!b)return;cur=id;
 $('#dt').innerHTML=`<div class="dh"><span class="tag">${esc(b.category)}</span><button class="x" aria-label="关闭">✕</button></div><h2>${esc(b.title)}</h2><p class="muted">${esc((b.author_name||'')+' @'+b.author_username)} · ${day(b.created_at)}</p><p class="sum">${esc(b.summary)}</p><div class="txt">${lnk(b.text)}</div><a class="go" href="${esc(xurl(b.url))}" target="_blank" rel="noopener">在 X 打开原帖 ↗</a>`;
 $('#dt .x').onclick=()=>$('#dlg').close();
 if(!$('#dlg').open)$('#dlg').showModal();$('#dlg').scrollTop=0;save()}
Promise.all(['data/bookmarks.json','data/meta.json'].map(u=>fetch(u).then(r=>{if(!r.ok)throw r.status;return r.json()}))).then(([b,m])=>{
 all=b;all.forEach(b=>b._h=[b.title,b.summary,b.text,b.author_username,b.author_name].join(' ').toLowerCase());
 $('#meta').textContent=`共 ${m.total} 条 · 最后更新 ${new Date(m.updated_at).toLocaleString('zh-CN',{timeZone:'Asia/Shanghai',hour12:false})}（北京时间）`;
 const p=new URLSearchParams(location.hash.slice(1));
 if(all.some(b=>b.category==p.get('c')))cat=p.get('c');$('#q').value=p.get('q')||'';
 if(['new','old'].includes(p.get('s')))$('#sort').value=p.get('s');
 cats();render();if(p.get('id'))openD(p.get('id'))
}).catch(()=>{$('#meta').textContent='数据加载失败，请刷新重试';$('#list').innerHTML='<p class="muted">书签数据没有加载出来，可能是网络问题或数据文件异常。</p>'});
$('#q').oninput=render;$('#sort').onchange=render;
$('#list').onclick=e=>{const o=e.target.closest('.open');if(o)openD(o.dataset.id)};
$('#dlg').onclick=e=>{if(e.target==$('#dlg'))$('#dlg').close()};
$('#dlg').onclose=()=>{cur=null;save()};
