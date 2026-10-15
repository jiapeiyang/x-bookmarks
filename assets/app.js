const $=s=>document.querySelector(s);let all=[],cat='全部';
const esc=s=>String(s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const day=s=>new Date(s).toLocaleDateString('sv-SE',{timeZone:'Asia/Shanghai'});
const hl=(s,q)=>{s=esc(s);if(!q)return s;const r=q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');return s.replace(new RegExp(r,'gi'),m=>`<mark>${m}</mark>`)};
function cats(){const c={};all.forEach(b=>c[b.category]=(c[b.category]||0)+1);
 const L=[['全部',all.length],...Object.entries(c).sort((a,b)=>b[1]-a[1])];
 $('#cats').innerHTML=L.map(([n,k])=>`<button class="chip${n==cat?' on':''}" data-c="${esc(n)}">${esc(n)}<b>${k}</b></button>`).join('');
 document.querySelectorAll('.chip').forEach(e=>e.onclick=()=>{cat=e.dataset.c;cats();render()})}
function render(){const q=$('#q').value.trim().toLowerCase(),s=$('#sort').value;
 let r=all.filter(b=>(cat=='全部'||b.category==cat)&&(!q||[b.title,b.summary,b.text,b.author_username,b.author_name].join(' ').toLowerCase().includes(q)));
 r.sort(s=='bm'?(a,b)=>a.bookmarked_order-b.bookmarked_order:s=='new'?(a,b)=>b.created_at.localeCompare(a.created_at):(a,b)=>a.created_at.localeCompare(b.created_at));
 $('#count').textContent=`显示 ${r.length} 条`;
 $('#list').innerHTML=r.map(b=>`<article class="card"><span class="tag">${esc(b.category)}</span><h3>${hl(b.title,q)}</h3><p>${hl(b.summary,q)}</p><div class="foot"><span>${hl((b.author_name||'')+' @'+b.author_username,q)} · ${day(b.created_at)}</span><a href="${esc(b.url)}" target="_blank" rel="noopener">原帖 ↗</a></div></article>`).join('')||'<p class="muted">没有匹配的书签</p>'}
Promise.all([fetch('data/bookmarks.json').then(r=>r.json()),fetch('data/meta.json').then(r=>r.json())]).then(([b,m])=>{all=b;
 $('#meta').textContent=`共 ${m.total} 条 · 最后更新 ${new Date(m.updated_at).toLocaleString('zh-CN',{timeZone:'Asia/Shanghai',hour12:false})}（北京时间）`;cats();render()});
$('#q').oninput=render;$('#sort').onchange=render;
