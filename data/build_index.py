# -*- coding: utf-8 -*-
# 裏ページ data/index.html を「図」中心で作り直す（v3＝2026-09-27 の7点の指摘を反映）。骨組みは news.html から写す。表は各章の「表で見る」に畳む。
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
D = 'D:/tas9_labo/web/notes/'
src = io.open(D + 'news.html', encoding='utf-8', newline='').read().replace('\r\n', '\n')

def block(start, end_tag):
    i = src.index(start); j = src.index(end_tag, i) + len(end_tag)
    return src[i:j]

toc = block('<nav class="toc"', '</nav>'); hero = block('<div class="hero-bg page"', '</div>')
head = block('<header class="top">', '</header>'); by = block('<footer class="by">', '</footer>')
fonts = block('<link rel="preconnect" href="https://fonts.googleapis.com">', 'display=swap">'); icon = block('<link rel="icon"', '">')
ver = re.search(r'style\.css\?v=([0-9a-z]+)', src).group(1)

def relink(s):
    for a, b in [('href="index.html"', 'href="../index.html"'), ('href="industry.html"', 'href="../industry.html"'), ('href="dev.html"', 'href="../dev.html"'),
                 ('href="news.html" aria-current="page"', 'href="../news.html"'), ('href="news.html"', 'href="../news.html"'), ('src="hero.jpg', 'src="../hero.jpg')]:
        s = s.replace(a, b)
    return s
toc, hero, head = relink(toc), relink(hero), relink(head)
head = head.replace('>追う</p>', '>台帳</p>').replace('<h1>気になる News</h1>', '<h1>データ台帳</h1>')
head = re.sub(r'<p class="lead">.*?</p>', '<p class="lead">台帳の数字を、図で読むための裏の窓。サイトからはリンクしていない。<br>原本は同じフォルダの CSV と <a href="README.md">README.md</a>。図の下の「表で見る」で数字そのものも確かめられる。</p>', head, flags=re.S)

css = r'''
/* 図の色：色弱でも隣り合う色が見分けられる組み合わせを検証済み（README 参照）。文字は必ず文字色、色は印にだけ */
:root{--k-jp:#4f7d12;--k-us:#1160c9;--k-cn:#c2562a;--k-kr:#0a93a8;--k-eu:#6b5bd2;--k-ot:#8a919c;--k-dim:#c9ced6;
  --s1:#93b95a;--s2:#7aa63f;--s3:#639327;--s4:#4f7f16;--s5:#3d680c;--o1:#93b95a;--o2:#476f10;--up:#1160c9;--down:#c2562a;--grid:#e3e6ec;--on-mark:#fff}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--k-jp:#6e9c3a;--k-us:#3d86e0;--k-cn:#d86a2f;--k-kr:#1f97aa;--k-eu:#7d6fd0;--k-ot:#6f7680;--k-dim:#3a3f47;
  --s1:#4a5f2c;--s2:#5f7f30;--s3:#78a13a;--s4:#9bc25b;--s5:#bfdc8e;--o1:#78a13a;--o2:#bfdc8e;--up:#3d86e0;--down:#d86a2f;--grid:#262a31;--on-mark:#0a0b0d}}
:root[data-theme="dark"]{--k-jp:#6e9c3a;--k-us:#3d86e0;--k-cn:#d86a2f;--k-kr:#1f97aa;--k-eu:#7d6fd0;--k-ot:#6f7680;--k-dim:#3a3f47;
  --s1:#4a5f2c;--s2:#5f7f30;--s3:#78a13a;--s4:#9bc25b;--s5:#bfdc8e;--o1:#78a13a;--o2:#bfdc8e;--up:#3d86e0;--down:#d86a2f;--grid:#262a31;--on-mark:#0a0b0d}
section.ch{min-width:0}
.lg-kpi{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-top:22px}
.lg-tile{background:var(--node);border:1px solid var(--line);border-radius:16px;padding:16px 18px;min-width:0}
.lg-tile .l{font-size:12px;color:var(--sub);line-height:1.5}
.lg-tile .v{margin-top:6px;font-size:28px;font-weight:600;letter-spacing:-.02em;line-height:1.15}
.lg-tile .v small{font-size:14px;font-weight:500;color:var(--sub);margin-left:2px}
.lg-tile .d{margin-top:6px;font-size:12px;color:var(--sub);line-height:1.6}
.lg-tile .d b{color:var(--ink);font-weight:600}
.lg-meter{margin-top:10px;height:8px;border-radius:4px;background:color-mix(in srgb,var(--k-jp) 18%,var(--node));overflow:hidden}
.lg-meter i{display:block;height:100%;border-radius:4px;background:var(--k-jp)}
.lg-legend{display:flex;flex-wrap:wrap;gap:6px 14px;margin-top:18px;font-size:12px;color:var(--sub)}
.lg-legend span{display:inline-flex;align-items:center;gap:6px}
.lg-legend i{width:12px;height:12px;border-radius:3px;background:var(--c)}
.lg-legend i.ln{width:16px;height:2px;border-radius:1px}
.lg-lists{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px 28px;margin-top:14px}
.lg-lst h3{margin:14px 0 8px;font-size:14px;font-weight:600;display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
.lg-lst h3 small{font-weight:400;color:var(--sub);font-size:12px}
.lg-lst .lg-share{margin-left:auto;font-family:var(--mono);font-size:12px;color:var(--sub);font-variant-numeric:tabular-nums}
.lg-lst .lg-share b{font-size:16px;color:var(--ink)}
.lg-srow{display:grid;grid-template-columns:44px minmax(0,1fr) 56px;align-items:center;gap:10px;margin-top:8px;font-size:12px;color:var(--sub)}
.lg-srow .lg-bar{display:flex;gap:2px;height:20px}
.lg-srow .lg-seg{position:relative;height:100%;border-radius:3px;background:var(--c);min-width:2px;display:flex;align-items:center;justify-content:center;
  font-family:var(--mono);font-size:11px;font-weight:600;color:var(--on-mark);outline:none}
.lg-srow .lg-seg:first-child{border-top-left-radius:4px;border-bottom-left-radius:4px}
.lg-srow .lg-seg:last-child{border-top-right-radius:4px;border-bottom-right-radius:4px}
.lg-srow .lg-seg:hover,.lg-srow .lg-seg:focus-visible{filter:brightness(1.12)}
.lg-srow .lg-n{font-family:var(--mono);font-variant-numeric:tabular-nums;text-align:right}
.lg-ctl{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin-top:20px}
.lg-segctl{display:inline-flex;border:1px solid var(--line);border-radius:980px;padding:2px;background:var(--card)}
.lg-segctl button{font:inherit;font-size:13px;line-height:1.4;padding:5px 14px;border-radius:980px;border:0;background:transparent;color:var(--sub);cursor:pointer}
.lg-segctl button[aria-pressed="true"]{background:var(--tonal);color:var(--ink);font-weight:500}
.lg-ctl .lg-hint{font-size:12px;color:var(--sub)}
.fig{margin-top:18px}
svg.viz{display:block;width:100%;height:auto;overflow:visible}
svg.viz text{font-family:"Inter","Noto Sans JP",system-ui,sans-serif;fill:var(--ink)}
svg.viz .ax text{fill:var(--sub);font-size:11px;font-family:var(--mono)}
svg.viz .grid line{stroke:var(--grid);stroke-width:1}
svg.viz .ax line,svg.viz .ax path{stroke:var(--line);stroke-width:1}
svg.viz .lab{font-size:11px;fill:var(--sub)}
svg.viz .lab.ink{fill:var(--ink);font-weight:600}
svg.viz .mono{font-family:var(--mono);font-variant-numeric:tabular-nums}
svg.viz .hit{fill:transparent;pointer-events:all;outline:none}
.lg-smulti{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:14px 18px;margin-top:8px}
.lg-sm{background:var(--node);border:1px solid var(--line);border-radius:14px;padding:12px 12px 8px;min-width:0}
.lg-sm h4{margin:0;font-size:13px;font-weight:600;display:flex;justify-content:space-between;gap:8px}
.lg-sm h4 small{font-weight:400;color:var(--sub);font-size:11px}
.lg-sm .lg-vals{display:flex;gap:12px;margin-top:2px;font-size:11px;color:var(--sub)}
.lg-sm .lg-vals b{font-family:var(--mono);color:var(--ink);font-weight:600;font-variant-numeric:tabular-nums}
.lg-two{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:18px 32px}
.lg-hbars{margin-top:8px}
.lg-row{display:grid;grid-template-columns:minmax(120px,170px) minmax(0,1fr) 64px;align-items:center;gap:10px;padding:5px 0;font-size:13px;line-height:1.35}
.lg-row .lg-nm{min-width:0;word-break:auto-phrase}
.lg-row .lg-nm small{display:block;font-size:11px;color:var(--sub)}
.lg-row .lg-tr{position:relative;height:14px}
.lg-row .lg-tr i{position:absolute;top:0;height:100%;border-radius:0 4px 4px 0;background:var(--k-jp)}
.lg-row .lg-tr i.lg-neg{border-radius:4px 0 0 4px;background:var(--down)}
.lg-row .lg-tr i.lg-pos{background:var(--up)}
.lg-row .lg-tr i.lg-est{background:repeating-linear-gradient(135deg,var(--k-jp) 0 6px,color-mix(in srgb,var(--k-jp) 45%,var(--node)) 6px 10px)}
.lg-row .lg-tr .lg-ref{position:absolute;top:-4px;bottom:-4px;width:1px;background:var(--sub)}
.lg-row .lg-tr .lg-zero{position:absolute;top:-3px;bottom:-3px;width:1px;background:var(--sub)}
.lg-row .lg-vl{font-family:var(--mono);font-size:12px;text-align:right;font-variant-numeric:tabular-nums}
.lg-row .lg-tr i:hover,.lg-row .lg-tr i:focus-visible{filter:brightness(1.12);outline:none}
.lg-tv{margin-top:20px}
.lg-tv summary{cursor:pointer;font-size:13px;color:var(--sub);list-style:none;display:inline-flex;align-items:center;gap:6px;padding:6px 12px;border:1px solid var(--line);border-radius:980px}
.lg-tv summary::-webkit-details-marker{display:none}
.lg-tv[open] summary{color:var(--ink)}
.lg-tv .lg-scroll{margin-top:12px;overflow-x:auto;border:1px solid var(--line);border-radius:14px;background:var(--node)}
table.lg-tbl{width:100%;border-collapse:collapse;font-size:12px;line-height:1.5;min-width:560px}
.lg-tbl th,.lg-tbl td{padding:7px 10px;border-bottom:1px solid var(--line);text-align:left;white-space:nowrap;vertical-align:top}
.lg-tbl th{font-size:11px;font-weight:600;letter-spacing:.06em;color:var(--sub);background:var(--tonal)}
.lg-tbl td.num,.lg-tbl th.num{text-align:right;font-family:var(--mono);font-variant-numeric:tabular-nums}
.lg-tbl tr:last-child td{border-bottom:0}
.lg-note{margin-top:12px;font-size:12px;color:var(--sub);line-height:1.7}
#tip{position:fixed;z-index:50;pointer-events:none;background:var(--ink);color:var(--bg);border-radius:10px;padding:8px 11px;font-size:12px;line-height:1.5;max-width:280px;box-shadow:var(--shadow);display:none}
#tip .h{font-weight:600;margin-bottom:2px}
#tip .r{display:flex;gap:8px;justify-content:space-between}
#tip .r b{font-family:var(--mono);font-weight:600;font-variant-numeric:tabular-nums}
#tip .k{display:inline-block;width:10px;height:2px;vertical-align:middle;margin-right:5px;background:var(--c)}
#tip ul{margin:4px 0 0;padding-left:14px}
.lg-empty{margin-top:16px;font-size:14px;color:var(--sub)}
.lg-three{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px 26px;margin-top:6px}
.lg-crow{display:grid;grid-template-columns:96px minmax(0,1fr) 34px;align-items:center;gap:8px;padding:4px 0;font-size:13px}
.lg-crow .lg-ctr{height:12px;position:relative}
.lg-crow .lg-ctr i{position:absolute;left:0;top:0;height:100%;border-radius:0 4px 4px 0;background:var(--k-ot)}
.lg-crow.jp .lg-ctr i{background:var(--k-jp)}
.lg-crow .lg-cn{font-family:var(--mono);font-size:12px;text-align:right;font-variant-numeric:tabular-nums}
.lg-crow.jp .lg-cnm{font-weight:600}
.lg-crow .lg-ctr i:hover,.lg-crow .lg-ctr i:focus-visible{filter:brightness(1.12);outline:none}
.lg-sig{display:flex;flex-wrap:wrap;gap:4px 6px;margin-top:8px;font-size:11px;color:var(--sub)}
.lg-sig span{display:inline-flex;align-items:center;gap:4px;background:var(--tonal);border-radius:6px;padding:2px 7px;white-space:nowrap}
.lg-sig b{font-family:var(--mono);font-weight:700;color:var(--ink);font-variant-numeric:tabular-nums}
.lg-sig b.lg-up{color:var(--up)}.lg-sig b.lg-dn{color:var(--down)}
.lg-share2{display:grid;grid-template-columns:minmax(120px,170px) minmax(0,1fr) 76px;align-items:center;gap:10px;padding:7px 0;font-size:13px;line-height:1.35}
.lg-share2 .lg-nm{min-width:0}
.lg-share2 .lg-nm small{display:block;font-size:11px;color:var(--sub)}
.lg-share2 .lg-trk{position:relative;height:20px}
.lg-share2 .lg-trk .lg-mid{position:absolute;left:50%;top:-4px;bottom:-4px;width:1px;background:var(--sub)}
.lg-share2 .lg-trk .lg-span{position:absolute;top:8px;height:4px;background:var(--k-dim);border-radius:2px}
.lg-share2 .lg-trk .lg-dot{position:absolute;top:3px;width:14px;height:14px;margin-left:-7px;border-radius:50%;box-sizing:border-box;outline:none}
.lg-share2 .lg-trk .lg-dot.old{border:2px solid var(--k-ot);background:var(--node)}
.lg-share2 .lg-trk .lg-dot.new{background:var(--k-jp);border:2px solid var(--node)}
.lg-share2 .lg-trk .lg-dot:hover,.lg-share2 .lg-trk .lg-dot:focus-visible{filter:brightness(1.12)}
.lg-share2 .lg-vl{font-family:var(--mono);font-size:12px;text-align:right;font-variant-numeric:tabular-nums}
.lg-share2 .lg-vl small{display:block;font-size:10px;color:var(--sub)}
.lg-axis{display:grid;grid-template-columns:minmax(120px,170px) minmax(0,1fr) 76px;gap:10px;font-size:11px;color:var(--sub);font-family:var(--mono)}
.lg-axis .lg-ax{display:flex;justify-content:space-between}
.lg-caveat{margin-top:16px;padding:10px 14px;border-left:3px solid var(--k-cn);background:var(--tonal);border-radius:0 10px 10px 0;font-size:12.5px;line-height:1.75;color:var(--ink)}
.lg-caveat b{font-weight:600}
#mileBox{overflow-x:auto}
#mileBox svg.viz{min-width:600px}
@media (max-width:720px){.lg-share2,.lg-axis{grid-template-columns:minmax(96px,120px) minmax(0,1fr) 62px}.lg-crow{grid-template-columns:80px minmax(0,1fr) 30px}}
@media (max-width:720px){.lg-row{grid-template-columns:minmax(96px,120px) minmax(0,1fr) 56px}.lg-srow{grid-template-columns:36px minmax(0,1fr) 50px}}
'''

js = r'''
(function(){
  // 確認用：?theme=dark / light で配色を固定できる（通常は端末の設定に追従）
  var th=(location.search.match(/[?&]theme=(dark|light)/)||[])[1];if(th)document.documentElement.setAttribute('data-theme',th);
  // ---------- 読み込み ----------
  function parse(t){if(t.charCodeAt(0)===0xFEFF)t=t.slice(1);t=t.replace(/\r\n/g,'\n');var rows=[],row=[],cell='',q=false;
    for(var i=0;i<t.length;i++){var c=t[i];if(q){if(c==='"'){if(t[i+1]==='"'){cell+='"';i++;}else q=false;}else cell+=c;}
      else if(c==='"')q=true;else if(c===','){row.push(cell);cell='';}else if(c==='\n'){row.push(cell);rows.push(row);row=[];cell='';}else cell+=c;}
    if(cell!==''||row.length){row.push(cell);rows.push(row);}var h=rows.shift();
    return rows.filter(function(r){return r.some(function(x){return x.trim()!=='';});}).map(function(r){var o={};h.forEach(function(k,i){o[k.trim()]=(r[i]||'').trim();});return o;});}
  function load(f){return fetch(f+'?c='+Date.now()).then(function(r){if(!r.ok)throw new Error(f);return r.text();}).then(parse);}
  var $=function(id){return document.getElementById(id);};
  var T,M,R,I,DEF,ENT,byId={},entName={},entGroup={},cpi={};
  var SHORT={'square-enix-hd':'スクエニHD','bandai-namco-hd':'バンナムHD','sega-sammy-hd':'セガサミーHD','konami-group':'コナミG','koei-tecmo-hd':'コーエーテクモHD',gungho:'ガンホー','nippon-ichi':'日本一','silicon-studio':'シリコンスタジオ'};
  var nm=function(e){return SHORT[e.entity]||e.name_ja;};
  var GROUPS=[['JP','日本'],['US','米国'],['CN','中国'],['KR','韓国'],['EU','欧州'],['OT','その他']];
  var EU={SE:1,NO:1,CZ:1,AT:1,FR:1,DE:1,GB:1,PL:1,NL:1,FI:1,DK:1,ES:1,IT:1};
  var CN_NAME={JP:'日本',US:'米国',CN:'中国',KR:'韓国',SE:'スウェーデン',NO:'ノルウェー',CZ:'チェコ',AT:'オーストリア',AU:'オーストラリア',SG:'シンガポール',CA:'カナダ',GB:'英国',FR:'フランス',DE:'ドイツ'};
  function grp(c){if(!c)return 'OT';if(c==='JP'||c==='US'||c==='CN'||c==='KR')return c;if(EU[c])return 'EU';return 'OT';}
  var fmtInt=function(n){return Math.round(Number(n)).toLocaleString('ja-JP');};
  function fmtYen(v){v=Number(v);var a=Math.abs(v),s=v<0?'−':'';if(a>=1e12){var cho=Math.floor(a/1e12),oku=Math.round((a-cho*1e12)/1e8);return s+cho+'兆'+(oku?fmtInt(oku)+'億':'')+'円';}
    if(a>=1e10)return s+fmtInt(a/1e8)+'億円';if(a>=1e8)return s+(a/1e8).toFixed(1).replace(/\.0$/,'')+'億円';if(a>=1e4)return s+fmtInt(a/1e4)+'万円';return s+fmtInt(a)+'円';}
  function fmtUnits(v){v=Number(v);if(v>=1e8)return (v/1e8).toFixed(2).replace(/\.?0+$/,'')+'億';if(v>=1e4)return (v/1e4).toFixed(v>=1e6?0:1).replace(/\.0$/,'')+'万';return fmtInt(v);}
  function h(tag,attrs,kids){var e=document.createElement(tag);if(attrs)Object.keys(attrs).forEach(function(k){if(k==='text')e.textContent=attrs[k];else if(k==='style')e.style.cssText=attrs[k];else e.setAttribute(k,attrs[k]);});
    (kids||[]).forEach(function(k){if(k==null)return;e.appendChild(typeof k==='string'?document.createTextNode(k):k);});return e;}
  var NS='http://www.w3.org/2000/svg';
  function s(tag,attrs,kids){var e=document.createElementNS(NS,tag);if(attrs)Object.keys(attrs).forEach(function(k){if(k==='text')e.textContent=attrs[k];else e.setAttribute(k,attrs[k]);});(kids||[]).forEach(function(k){if(k)e.appendChild(k);});return e;}
  function mount(id,el){var b=$(id);b.textContent='';b.appendChild(el);}
  // ---------- ツールチップ（値が主・名前は従。文字は textContent） ----------
  var tip=$('tip');
  function showTip(ev,title,rows,list){tip.textContent='';tip.appendChild(h('div',{class:'h',text:title}));
    (rows||[]).forEach(function(r){var d=h('div',{class:'r'});var l=h('span');if(r.c){l.appendChild(h('i',{class:'k',style:'--c:'+r.c}));}l.appendChild(document.createTextNode(r.k));d.appendChild(l);d.appendChild(h('b',{text:r.v}));tip.appendChild(d);});
    if(list&&list.length){var ul=h('ul');list.slice(0,12).forEach(function(x){ul.appendChild(h('li',{text:x}));});if(list.length>12)ul.appendChild(h('li',{text:'…ほか '+(list.length-12)+' 本'}));tip.appendChild(ul);}
    tip.style.display='block';moveTip(ev);}
  function moveTip(ev){var x=(ev.clientX||0)+14,y=(ev.clientY||0)+14,w=tip.offsetWidth,hh=tip.offsetHeight;if(x+w>innerWidth-8)x=ev.clientX-w-14;if(y+hh>innerHeight-8)y=ev.clientY-hh-14;tip.style.left=x+'px';tip.style.top=y+'px';}
  function hideTip(){tip.style.display='none';}
  function hover(node,fn){node.setAttribute('tabindex','0');node.addEventListener('pointerenter',function(e){var a=fn();showTip(e,a[0],a[1],a[2]);});node.addEventListener('pointermove',moveTip);node.addEventListener('pointerleave',hideTip);
    node.addEventListener('focus',function(){var a=fn();var r=node.getBoundingClientRect();showTip({clientX:r.left+r.width/2,clientY:r.top},a[0],a[1],a[2]);});node.addEventListener('blur',hideTip);}
  // ---------- 共通：表で見る ----------
  function table(heads,rows){var tb=h('table',{class:'lg-tbl'});var tr=h('tr');heads.forEach(function(x){tr.appendChild(h('th',{text:x[0],class:x[1]||''}));});tb.appendChild(h('thead',null,[tr]));var tbody=h('tbody');
    rows.forEach(function(r){var e=h('tr');r.forEach(function(c,i){e.appendChild(h('td',{text:c==null?'—':String(c),class:heads[i][1]||''}));});tbody.appendChild(e);});tb.appendChild(tbody);return h('div',{class:'lg-scroll'},[tb]);}
  function tv(id,heads,rows){mount(id,table(heads,rows));}
  function latest(ind,ent){var xs=I.filter(function(r){return r.indicator_id===ind&&r.entity===ent;}).sort(function(a,b){return b.period_end.localeCompare(a.period_end);});return xs[0];}
  function series(ind,ent){var m={};I.filter(function(r){return r.indicator_id===ind&&r.entity===ent;}).forEach(function(r){var y=r.period_end.slice(0,4);if(!m[y]||r.period_end>m[y].period_end)m[y]=r;});return m;}

  // ---------- 00 KPI ----------
  function drawKpi(){
    var w=latest('market_size_world_jpy','world'),wg=latest('market_growth_world_jpy_pct','world'),wc=latest('market_growth_world_const_currency_pct','world');
    var j=latest('market_size_japan_jpy','japan'),gp=latest('game_population_japan','japan'),pop=latest('population_japan','japan');
    var bk=I.filter(function(r){return r.indicator_id==='bankruptcies_smartphone_game';}).sort(function(a,b){return a.period_end.localeCompare(b.period_end);});
    var box=$('kpi');box.textContent='';
    function tile(l,v,unit,d,extra){var t=h('div',{class:'lg-tile'},[h('div',{class:'l',text:l}),h('div',{class:'v'},[v,h('small',{text:unit})]),h('div',{class:'d'},d)]);if(extra)t.appendChild(extra);return t;}
    if(w){box.appendChild(tile('世界のゲーム市場（'+w.period_end.slice(0,4)+'年）',(Number(w.value)/1e12).toFixed(1),'兆円',[h('b',{text:(wg?'+'+wg.value+'%':'')}),' 円建て　',h('b',{text:(wc?'+'+wc.value+'%':'')}),' 同一通貨 ＝ 為替を除いた伸び']));}
    if(j){var jg=latest('market_growth_japan_jpy_pct','japan');box.appendChild(tile('国内のゲーム市場（'+j.period_end.slice(0,4)+'年）',(Number(j.value)/1e12).toFixed(2),'兆円',[h('b',{text:(jg&&jg.period_end.slice(0,4)===j.period_end.slice(0,4)?'+'+jg.value+'%':'—')}),' 前年比。',h('span',{text:'Switch 2 の発売年'})]));}
    if(gp&&pop){var pct=Number(gp.value)/Number(pop.value)*100;var m=h('div',{class:'lg-meter'},[h('i',{style:'width:'+pct.toFixed(1)+'%'})]);
      box.appendChild(tile('国内のゲーム人口（'+gp.period_end.slice(0,4)+'年）',(Number(gp.value)/1e4).toLocaleString('ja-JP'),'万人',[h('b',{text:pct.toFixed(0)+'%'}),' ＝ 人口 '+(Number(pop.value)/1e4).toLocaleString('ja-JP')+'万人に対する割合'],m));}
    if(bk.length){var last=bk[bk.length-1];var prevs=bk.slice(0,-1).map(function(r){return r.period_end.slice(0,4)+'年 '+r.value+'件';}).join('・');
      box.appendChild(tile('スマホゲーム事業者の倒産',last.value,'件',[h('b',{text:last.note||''}),' ',h('span',{text:prevs?('比較：'+prevs):''})]));}
  }

  // ---------- 01 誰の作品が選ばれたか（積み上げ帯） ----------
  var LISTS=[['famitsu-annual-jp-2025','国内 家庭用','ファミ通 年間 TOP10（パッケージ）'],['sensortower-jp-mobile-revenue-2025','国内 スマホ','Sensor Tower 収益 TOP10（推計）'],
             ['steam-best-of-2025-top-sellers','世界 PC','Steam 年間ベスト トップセラー プラチナ12'],['steam-best-of-2025-new-releases','世界 PC（新作）','Steam 年間ベスト 新作 プラチナ12']];
  var LENS=[['ip_country','IP'],['dev_country','開発'],['pub_country','運営']];
  function drawShare(){
    var lg=$('shareLegend');lg.textContent='';GROUPS.forEach(function(g){lg.appendChild(h('span',null,[h('i',{style:'--c:var(--k-'+g[0].toLowerCase()+')'}),g[1]]));});
    var box=$('shareBox');box.textContent='';var trows=[];
    LISTS.forEach(function(L){var rows=R.filter(function(r){return r.list_id===L[0];}).sort(function(a,b){return +a.rank-+b.rank;});if(!rows.length)return;
      var n=rows.length,jp=rows.filter(function(r){return (byId[r.title_id]||{}).ip_country==='JP';}).length;
      var lst=h('div',{class:'lg-lst'},[h('h3',null,[L[1],h('small',{text:L[2]}),h('span',{class:'lg-share'},['日本 IP ',h('b',{text:jp+'/'+n})])])]);
      LENS.forEach(function(len){var cnt={},names={};GROUPS.forEach(function(g){cnt[g[0]]=0;names[g[0]]=[];});
        rows.forEach(function(r){var t=byId[r.title_id]||{};var g=grp(t[len[0]]);cnt[g]++;names[g].push((t.title_ja||r.title_id)+(t[len[0]]&&g!==t[len[0]]?'（'+t[len[0]]+'）':''));});
        var bar=h('div',{class:'lg-bar'});GROUPS.forEach(function(g){if(!cnt[g[0]])return;var w=cnt[g[0]]/n*100;var seg=h('div',{class:'lg-seg',style:'--c:var(--k-'+g[0].toLowerCase()+');flex:0 0 calc('+w.toFixed(3)+'% - 2px)','role':'img','aria-label':g[1]+' '+cnt[g[0]]+'本'});
          if(w>=14)seg.textContent=(g[0]==='OT'?'他':g[0])+' '+cnt[g[0]];hover(seg,function(){return [L[1]+'・'+len[1]+'：'+g[1],[{k:'本数',v:cnt[g[0]]+'/'+n},{k:'割合',v:Math.round(cnt[g[0]]/n*100)+'%'}],names[g[0]]];});bar.appendChild(seg);});
        lst.appendChild(h('div',{class:'lg-srow'},[h('span',{text:len[1]}),bar,h('span',{class:'lg-n',text:'JP '+cnt.JP+'/'+n})]));
        trows.push([L[1],len[1]].concat(GROUPS.map(function(g){return cnt[g[0]];})));});
      box.appendChild(lst);});
    tv('shareTv',[['表'],['見方']].concat(GROUPS.map(function(g){return [g[1],'num'];})),trows);
  }

  // ---------- 02 世界のどこの会社か（国別の本数・3つの見方を並べる） ----------
  var LENS_NAME={ip_country:'IP の持ち主',dev_country:'開発の拠点',pub_country:'販売・運営'};
  function drawCountries(){
    var ids={};R.forEach(function(r){if(LISTS.some(function(L){return L[0]===r.list_id;}))ids[r.title_id]=1;});
    var box=$('mapBox');box.textContent='';var trows=[];var total=Object.keys(ids).length;
    LENS.forEach(function(len){var cnt={},names={};Object.keys(ids).forEach(function(id){var t=byId[id]||{};var c=t[len[0]]||'複数の国';cnt[c]=(cnt[c]||0)+1;(names[c]=names[c]||[]).push(t.title_ja||id);});
      var keys=Object.keys(cnt).sort(function(a,b){return cnt[b]-cnt[a]||a.localeCompare(b);});var max=cnt[keys[0]]||1;
      var col=h('div',{class:'lg-lst'},[h('h3',null,[LENS_NAME[len[0]],h('small',{text:'日本 '+(cnt.JP||0)+'/'+total})])]);
      keys.forEach(function(c){var row=h('div',{class:'lg-crow'+(c==='JP'?' jp':'')});var tr=h('div',{class:'lg-ctr'});
        var bar=h('i',{style:'width:'+(cnt[c]/max*100).toFixed(1)+'%','role':'img','aria-label':(CN_NAME[c]||c)+' '+cnt[c]+'本'});
        hover(bar,function(){return [(CN_NAME[c]||c)+'（'+LENS_NAME[len[0]]+'）',[{k:'本数',v:cnt[c]+'/'+total}],names[c]];});tr.appendChild(bar);
        row.appendChild(h('span',{class:'lg-cnm',text:(CN_NAME[c]||c)}));row.appendChild(tr);row.appendChild(h('span',{class:'lg-cn',text:String(cnt[c])}));col.appendChild(row);
        trows.push([LENS_NAME[len[0]],CN_NAME[c]||c,cnt[c],(names[c]||[]).join('、')]);});
      box.appendChild(col);});
    $('mapNote').textContent='2025年の4つの表に出た作品（重複を除く '+total+' 本）を、IP の持ち主・開発の拠点・販売運営の会社の国で数え直した。3つの棒の長さが違う国は、権利・作業・売上の行き先が分かれている国。開発の拠点が最も散らばる。「複数の国」＝開発が複数の国のスタジオにまたがり1つに決められない作品。';
    tv('mapTv',[['見方'],['国'],['本数','num'],['作品']],trows);
  }

  // ---------- 03 勢い（小さな折れ線を並べる・指数） ----------
  function drawTrend(){
    var real=$('realChk').checked;var box=$('trendBox');box.textContent='';var trows=[];
    var Y0=2016,Y1=2026,years=[];for(var y=Y0;y<=Y1;y++)years.push(String(y));
    var panels=[];
    ENT.forEach(function(e){var sv=series('net_sales_consolidated',e.entity),em=series('employees_consolidated',e.entity);
      var ys=years.filter(function(y){return sv[y]&&em[y];});if(ys.length<3)return;var b=ys[0];
      var sales=function(y){var v=Number(sv[y].value);return real&&cpi[y]?v/(cpi[y]/100):v;};
      var a=ys.map(function(y){return [y,sales(y)/sales(b)*100];}),c=ys.map(function(y){return [y,Number(em[y].value)/Number(em[b].value)*100];});
      panels.push({e:e,ys:ys,a:a,c:c,sv:sv,em:em,sales:sales});});
    var W=220,H=110,pl=6,pr=6,pt=8,pb=18;
    panels.forEach(function(p){
      var vals=p.a.concat(p.c).map(function(d){return d[1];});var lo=Math.min(80,Math.floor(Math.min.apply(null,vals)/20)*20),hi=Math.max(120,Math.ceil(Math.max.apply(null,vals)/20)*20);
      var x=function(y){return pl+(Number(y)-Y0)/(Y1-Y0)*(W-pl-pr);},yy=function(v){return pt+(hi-v)/(hi-lo)*(H-pt-pb);};
      var svg=s('svg',{class:'viz',viewBox:'0 0 '+W+' '+H,role:'img','aria-label':p.e.name_ja+' の売上高と従業員数の指数'});
      var grid=s('g',{class:'grid'});[100].forEach(function(v){grid.appendChild(s('line',{x1:pl,x2:W-pr,y1:yy(v),y2:yy(v)}));});svg.appendChild(grid);
      var ax=s('g',{class:'ax'});ax.appendChild(s('text',{x:pl,y:H-4,text:p.ys[0]}));ax.appendChild(s('text',{x:W-pr,y:H-4,'text-anchor':'end',text:p.ys[p.ys.length-1]}));ax.appendChild(s('text',{x:pl,y:yy(100)-3,text:'100',style:'font-size:9px'}));svg.appendChild(ax);
      function path(d,col){return s('path',{d:d.map(function(q,i){return (i?'L':'M')+x(q[0]).toFixed(1)+' '+yy(q[1]).toFixed(1);}).join(' '),style:'fill:none;stroke:'+col+';stroke-width:2;stroke-linejoin:round;stroke-linecap:round'});}
      svg.appendChild(path(p.c,'var(--k-ot)'));svg.appendChild(path(p.a,'var(--k-jp)'));
      var la=p.a[p.a.length-1],lc=p.c[p.c.length-1];
      [[la,'var(--k-jp)'],[lc,'var(--k-ot)']].forEach(function(q){svg.appendChild(s('circle',{cx:x(q[0][0]),cy:yy(q[0][1]),r:4,style:'fill:'+q[1]+';stroke:var(--node);stroke-width:2'}));});
      var cross=s('line',{x1:0,x2:0,y1:pt,y2:H-pb,style:'stroke:var(--sub);stroke-width:1;display:none'});svg.appendChild(cross);
      var hit=s('rect',{x:0,y:0,width:W,height:H,class:'hit'});svg.appendChild(hit);
      function at(ev){var r=svg.getBoundingClientRect();var fx=(ev.clientX-r.left)/r.width*W;var best=p.ys[0],bd=1e9;p.ys.forEach(function(y){var d=Math.abs(x(y)-fx);if(d<bd){bd=d;best=y;}});return best;}
      hit.addEventListener('pointermove',function(ev){var y=at(ev);cross.setAttribute('x1',x(y));cross.setAttribute('x2',x(y));cross.style.display='';
        showTip(ev,nm(p.e)+' '+y+'年'+(p.e.fy_end_month!=='12'?'（'+p.e.fy_end_month+'月期）':''),[{k:'売上高'+(real?'（実質）':''),v:fmtYen(p.sales(y)),c:'var(--k-jp)'},{k:'指数',v:(p.sales(y)/p.sales(p.ys[0])*100).toFixed(0)},{k:'従業員',v:fmtInt(p.em[y].value)+'人',c:'var(--k-ot)'},{k:'指数',v:(Number(p.em[y].value)/Number(p.em[p.ys[0]].value)*100).toFixed(0)}]);});
      hit.addEventListener('pointerleave',function(){cross.style.display='none';hideTip();});
      // 信号：直近3年の年率（売上・人数）と、営業利益率の3年前との差。しきい値は注記に明記（成績の一文字は付けない）
      var yl=p.ys[p.ys.length-1],y3=p.ys[Math.max(0,p.ys.length-4)],n3=Number(yl)-Number(y3);
      var gS=n3>0?(Math.pow(p.sales(yl)/p.sales(y3),1/n3)-1)*100:null,gE=n3>0?(Math.pow(Number(p.em[yl].value)/Number(p.em[y3].value),1/n3)-1)*100:null;
      var opS=series('operating_income_consolidated',p.e.entity),mL=(opS[yl]&&p.sv[yl])?Number(opS[yl].value)/Number(p.sv[yl].value)*100:null,m3=(opS[y3]&&p.sv[y3])?Number(opS[y3].value)/Number(p.sv[y3].value)*100:null;
      var dM=(mL!=null&&m3!=null)?mL-m3:null;
      function sig(label,val,unit,th){if(val==null)return h('span',null,[label+' —']);var cls=val>=th?'lg-up':(val<=-th?'lg-dn':'');var ar=val>=th?'↑':(val<=-th?'↓':'→');
        return h('span',null,[label+' ',h('b',{class:cls,text:ar+' '+(val>=0?'+':'')+val.toFixed(0)+unit})]);}
      var sigs=h('div',{class:'lg-sig'},[sig('売上',gS,'%/年',5),sig('人',gE,'%/年',5),sig('利益率',dM,'pt',3)]);
      var panel=h('div',{class:'lg-sm'},[h('h4',null,[nm(p.e),h('small',{text:p.e.group})]),h('div',{class:'lg-vals'},[h('span',null,['売上 ',h('b',{text:la[1].toFixed(0)})]),h('span',null,['人 ',h('b',{text:lc[1].toFixed(0)})]),h('span',null,['利益率 ',h('b',{text:mL!=null?mL.toFixed(0)+'%':'—'})])]),svg,sigs]);
      box.appendChild(panel);
      trows.push([p.e.name_ja,p.ys[0],fmtYen(p.sales(p.ys[0])),fmtYen(p.sales(p.ys[p.ys.length-1])),la[1].toFixed(0),fmtInt(p.em[p.ys[0]].value),fmtInt(p.em[p.ys[p.ys.length-1]].value),lc[1].toFixed(0)]);});
    $('trendNote').textContent='最初の年を 100 とした指数。売上高は'+(real?'消費者物価指数で割った実質値':'名目値')+'（右上の切り替え）。縦の目盛りは会社ごと（100 の線が基準）なので、傾きの大きさは会社どうしで比べず、上の数字で比べる。下の3つの札は「信号」：売上と人は直近3年の平均伸び率（年率 ±5% を境に ↑→↓）、利益率は営業利益÷売上高の3年前との差（±3ポイントを境に ↑→↓）。A〜E のような一文字の成績は付けない＝重み付けが作る側の主観になり、当たり作1本で跳ねる小さな会社を誤読させるため。';
    tv('trendTv',[['会社'],['起点'],['売上 起点'],['売上 最新'],['指数','num'],['従業員 起点','num'],['従業員 最新','num'],['指数','num']],trows);
  }

  // ---------- 04 弾込め：研究開発費÷売上高の推移（小さな折れ線）と、作りかけのゲームの残高の前年比 ----------
  function drawInvest(){
    // (1) 研究開発費÷売上高（%）の推移
    var rbox=$('rdBox');rbox.textContent='';var trows=[],skipped=[];var W=220,H=96,pl=6,pr=6,pt=8,pb=18;
    ENT.forEach(function(e){var rd=series('rd_expense',e.entity),sv=series('net_sales_consolidated',e.entity);var ys=Object.keys(rd).filter(function(y){return sv[y];}).sort();if(ys.length<3){skipped.push(nm(e));return;}
      var pts=ys.map(function(y){return [y,Number(rd[y].value)/Number(sv[y].value)*100];});var hi=Math.max(5,Math.ceil(Math.max.apply(null,pts.map(function(q){return q[1];}))/5)*5);
      var x=function(y){return pl+(Number(y)-Number(ys[0]))/Math.max(1,Number(ys[ys.length-1])-Number(ys[0]))*(W-pl-pr);},yy=function(v){return pt+(hi-v)/hi*(H-pt-pb);};
      var svg=s('svg',{class:'viz',viewBox:'0 0 '+W+' '+H,role:'img','aria-label':nm(e)+' の研究開発費の売上比'});
      var grid=s('g',{class:'grid'});grid.appendChild(s('line',{x1:pl,x2:W-pr,y1:yy(0),y2:yy(0)}));grid.appendChild(s('line',{x1:pl,x2:W-pr,y1:yy(hi),y2:yy(hi)}));svg.appendChild(grid);
      var ax=s('g',{class:'ax'});ax.appendChild(s('text',{x:pl,y:H-4,text:ys[0]}));ax.appendChild(s('text',{x:W-pr,y:H-4,'text-anchor':'end',text:ys[ys.length-1]}));ax.appendChild(s('text',{x:pl,y:yy(hi)-2,text:hi+'%',style:'font-size:9px'}));svg.appendChild(ax);
      svg.appendChild(s('path',{d:pts.map(function(q,i){return (i?'L':'M')+x(q[0]).toFixed(1)+' '+yy(q[1]).toFixed(1);}).join(' '),style:'fill:none;stroke:var(--k-jp);stroke-width:2;stroke-linejoin:round;stroke-linecap:round'}));
      var last=pts[pts.length-1];svg.appendChild(s('circle',{cx:x(last[0]),cy:yy(last[1]),r:4,style:'fill:var(--k-jp);stroke:var(--node);stroke-width:2'}));
      var hit=s('rect',{x:0,y:0,width:W,height:H,class:'hit'});svg.appendChild(hit);
      hit.addEventListener('pointermove',function(ev){var r=svg.getBoundingClientRect();var fx=(ev.clientX-r.left)/r.width*W;var best=pts[0];pts.forEach(function(q){if(Math.abs(x(q[0])-fx)<Math.abs(x(best[0])-fx))best=q;});
        showTip(ev,nm(e)+' '+best[0]+'年'+(e.fy_end_month!=='12'?'（'+e.fy_end_month+'月期）':''),[{k:'研究開発費',v:fmtYen(rd[best[0]].value)},{k:'売上高',v:fmtYen(sv[best[0]].value)},{k:'売上比',v:best[1].toFixed(1)+'%'}]);});hit.addEventListener('pointerleave',hideTip);
      rbox.appendChild(h('div',{class:'lg-sm'},[h('h4',null,[nm(e),h('small',{text:e.group})]),h('div',{class:'lg-vals'},[h('span',null,['最新 ',h('b',{text:last[1].toFixed(1)+'%'})]),h('span',null,[ys[0]+'年 ',h('b',{text:pts[0][1].toFixed(1)+'%'})])]),svg]));
      trows.push([nm(e),ys[0],pts[0][1].toFixed(1)+'%',ys[ys.length-1],last[1].toFixed(1)+'%']);});
    tv('rdTv',[['会社'],['起点'],['売上比','num'],['最新'],['売上比','num']],trows);
    $('rdNote').textContent='3年分以上そろう会社だけ。'+(skipped.length?'出ない会社（研究開発費の開示が無いか年数が足りない）：'+skipped.join('・')+'。':'')+'値は有価証券報告書の「研究開発活動」の金額÷連結売上高。';
    // (2) 作りかけのゲームの残高：前年比の発散棒
    var rows=[];ENT.forEach(function(e){var m=series('game_wip',e.entity),ys=Object.keys(m).sort();if(ys.length<2)return;var y0=ys[ys.length-2],y1=ys[ys.length-1],v0=Number(m[y0].value),v1=Number(m[y1].value);if(!v0)return;rows.push({name:nm(e),y0:y0,y1:y1,v0:v0,v1:v1,pct:(v1/v0-1)*100});});
    rows.sort(function(a,b){return b.pct-a.pct;});var box=$('wipBox');box.textContent='';var maxp=Math.max.apply(null,rows.map(function(r){return Math.abs(r.pct);}).concat([10]));
    rows.forEach(function(r){var w=Math.min(50,Math.abs(r.pct)/maxp*50);var tr=h('div',{class:'lg-tr'});tr.appendChild(h('span',{class:'lg-zero',style:'left:50%'}));
      var bar=h('i',{class:r.pct>=0?'lg-pos':'lg-neg',style:(r.pct>=0?'left:50%;':'right:50%;')+'width:'+w.toFixed(2)+'%','role':'img','aria-label':r.name+' '+r.pct.toFixed(1)+'%'});
      hover(bar,function(){return [r.name+'：作りかけの残高',[{k:r.y0,v:fmtYen(r.v0)},{k:r.y1,v:fmtYen(r.v1)},{k:'増減',v:(r.pct>=0?'+':'')+r.pct.toFixed(1)+'%'}],[]];});tr.appendChild(bar);
      box.appendChild(h('div',{class:'lg-row'},[h('span',{class:'lg-nm'},[r.name,h('small',{text:r.y1+'年'})]),tr,h('span',{class:'lg-vl',text:(r.pct>=0?'+':'')+r.pct.toFixed(1)+'%'})]));});
    tv('wipTv',[['会社'],['前年'],['最新'],['増減','num']],rows.map(function(r){return [r.name,fmtYen(r.v0)+'（'+r.y0+'）',fmtYen(r.v1)+'（'+r.y1+'）',(r.pct>=0?'+':'')+r.pct.toFixed(1)+'%'];}));
  }

  // ---------- 05 労働の取り分：給与 ÷（給与＋1人あたり営業利益）の2時点 ----------
  var OPERATING={nintendo:1,capcom:1,gungho:1,mixi:1,colopl:1,'nippon-ichi':1,tose:1,cave:1,edia:1,'silicon-studio':1};
  function shareAt(ent,y){var sal=series('avg_salary_parent',ent)[y],op=series('operating_income_consolidated',ent)[y],em=series('employees_consolidated',ent)[y];if(!sal||!op||!em)return null;
    var s1=Number(sal.value),pe=Number(op.value)/Number(em.value);return {sal:s1,pe:pe,share:pe>=0?s1/(s1+pe)*100:null};}
  function drawLabor(){
    var rows=[];ENT.forEach(function(e){if(!OPERATING[e.entity])return;var ys=Object.keys(series('avg_salary_parent',e.entity)).sort();if(!ys.length)return;
      var y1=ys[ys.length-1],a1=shareAt(e.entity,y1);if(!a1)return;var y0=null,a0=null;
      for(var i=0;i<ys.length;i++){var gap=Number(y1)-Number(ys[i]);if(gap>=3&&gap<=5){var t=shareAt(e.entity,ys[i]);if(t){y0=ys[i];a0=t;break;}}}
      rows.push({e:e,y1:y1,a1:a1,y0:y0,a0:a0});});
    rows.sort(function(a,b){return (b.a1.share==null?-1:b.a1.share)-(a.a1.share==null?-1:a.a1.share);});
    var box=$('laborBox');box.textContent='';
    box.appendChild(h('div',{class:'lg-axis'},[h('span'),h('span',{class:'lg-ax'},[h('span',{text:'0%'}),h('span',{text:'50%'}),h('span',{text:'100%'})]),h('span')]));
    rows.forEach(function(r){var trk=h('div',{class:'lg-trk'});trk.appendChild(h('span',{class:'lg-mid'}));
      var v1=r.a1.share,v0=r.a0?r.a0.share:null;
      if(v1!=null&&v0!=null){var lo=Math.min(v0,v1),hi=Math.max(v0,v1);trk.appendChild(h('span',{class:'lg-span',style:'left:'+lo+'%;width:'+(hi-lo)+'%'}));}
      if(v0!=null){var d0=h('span',{class:'lg-dot old',style:'left:'+v0+'%','role':'img','aria-label':r.y0+'年 '+v0.toFixed(0)+'%'});
        hover(d0,function(){return [nm(r.e)+' '+r.y0+'年',[{k:'給与の取り分',v:v0.toFixed(0)+'%'},{k:'平均給与',v:fmtYen(r.a0.sal)},{k:'1人あたり営業利益',v:fmtYen(r.a0.pe)}],[]];});trk.appendChild(d0);}
      if(v1!=null){var d1=h('span',{class:'lg-dot new',style:'left:'+v1+'%','role':'img','aria-label':r.y1+'年 '+v1.toFixed(0)+'%'});
        hover(d1,function(){return [nm(r.e)+' '+r.y1+'年',[{k:'給与の取り分',v:v1.toFixed(0)+'%'},{k:'平均給与',v:fmtYen(r.a1.sal)},{k:'1人あたり営業利益',v:fmtYen(r.a1.pe)}],[]];});trk.appendChild(d1);}
      var vl=h('span',{class:'lg-vl'},[v1!=null?v1.toFixed(0)+'%':'赤字',h('small',{text:(v0!=null?r.y0+'年 '+v0.toFixed(0)+'%':(r.a0?r.y0+'年 赤字':''))})]);
      box.appendChild(h('div',{class:'lg-share2'},[h('span',{class:'lg-nm'},[nm(r.e),h('small',{text:r.e.group+'・'+r.y1+'年'})]),trk,vl]));});
    tv('laborTv',[['会社'],['年度'],['平均給与'],['1人あたり営業利益'],['給与の取り分','num'],['比較年'],['取り分','num']],rows.map(function(r){return [r.e.name_ja,r.y1,fmtYen(r.a1.sal),fmtYen(r.a1.pe),r.a1.share!=null?r.a1.share.toFixed(1)+'%':'赤字',r.y0||'—',(r.a0&&r.a0.share!=null)?r.a0.share.toFixed(1)+'%':(r.a0?'赤字':'—')];}));
  }

  // ---------- 06 資本の所在（横棒） ----------
  function drawOwn(){
    var rows=[];ENT.forEach(function(e){var r=latest('foreign_ownership_pct',e.entity);if(r)rows.push({e:e,v:Number(r.value),y:r.period_end.slice(0,4)});});rows.sort(function(a,b){return b.v-a.v;});
    var box=$('ownBox');box.textContent='';
    rows.forEach(function(r){var tr=h('div',{class:'lg-tr'});tr.appendChild(h('span',{class:'lg-ref',style:'left:50%'}));var bar=h('i',{style:'left:0;width:'+r.v+'%','role':'img','aria-label':r.e.name_ja+' '+r.v+'%'});
      hover(bar,function(){return [r.e.name_ja+'（'+r.y+'年）',[{k:'外国法人等の持株比率',v:r.v.toFixed(1)+'%'},{k:'区分',v:r.e.group}],[]];});tr.appendChild(bar);
      box.appendChild(h('div',{class:'lg-row'},[h('span',{class:'lg-nm'},[nm(r.e),h('small',{text:r.e.group})]),tr,h('span',{class:'lg-vl',text:r.v.toFixed(1)+'%'})]));});
    tv('ownTv',[['会社'],['区分'],['年'],['外国法人等の持株比率','num']],rows.map(function(r){return [r.e.name_ja,r.e.group,r.y,r.v.toFixed(2)+'%'];}));
  }

  // ---------- 07 節目：100万本までの日数（日数の軸に点） ----------
  function drawMile(){
    var rows=[];T.forEach(function(t){if(!t.release_date)return;var ms=M.filter(function(m){return m.id===t.id&&/^units/.test(m.metric)&&m.scope==='world'&&+m.value>=1e6;}).sort(function(a,b){return a.as_of.localeCompare(b.as_of);});
      if(!ms.length)return;var m=ms[0];if(+m.value>5e6)return;var days=Math.round((new Date(m.as_of)-new Date(t.release_date))/864e5);if(days<0)return;rows.push({t:t,m:m,days:days,upper:m.precision==='exact'});});
    rows.sort(function(a,b){return a.days-b.days;});
    var W=660,rowH=26,pl=236,pr=70,pt=28,pb=6,H=pt+rows.length*rowH+pb;var maxD=Math.max.apply(null,rows.map(function(r){return r.days;}).concat([1]));var max=Math.max(120,Math.ceil(maxD/30)*30);if(maxD>240)max=Math.max(max,390);
    var X=function(d){return pl+d/max*(W-pl-pr);};
    var svg=s('svg',{class:'viz',viewBox:'0 0 '+W+' '+H,role:'img','aria-label':'100万本までの日数'});
    var grid=s('g',{class:'grid'}),ax=s('g',{class:'ax'});
    grid.appendChild(s('line',{x1:X(0),x2:X(0),y1:pt-6,y2:H-pb,style:'stroke:var(--sub)'}));ax.appendChild(s('text',{x:X(0),y:pt-10,'text-anchor':'middle',style:'font-family:inherit',text:'発売'}));
    [[30,'1か月'],[100,'100日'],[365,'1年']].forEach(function(rf){if(rf[0]>max)return;grid.appendChild(s('line',{x1:X(rf[0]),x2:X(rf[0]),y1:pt-6,y2:H-pb}));ax.appendChild(s('text',{x:X(rf[0]),y:pt-10,'text-anchor':'middle',style:'font-family:inherit',text:rf[1]}));});
    svg.appendChild(grid);svg.appendChild(ax);
    rows.forEach(function(r,i){var y=pt+i*rowH+rowH/2;var name=r.t.title_ja.length>20?r.t.title_ja.slice(0,19)+'…':r.t.title_ja;
      svg.appendChild(s('line',{x1:X(0),x2:X(r.days),y1:y,y2:y,style:'stroke:var(--k-dim);stroke-width:2'}));
      svg.appendChild(s('text',{x:pl-12,y:y+4,'text-anchor':'end',class:'lab ink',style:'font-weight:500',text:name}));
      svg.appendChild(s('circle',{cx:X(r.days),cy:y,r:5,style:r.upper?'fill:var(--node);stroke:var(--k-jp);stroke-width:2':'fill:var(--k-jp);stroke:var(--node);stroke-width:2'}));
      svg.appendChild(s('text',{x:W-pr+10,y:y+4,class:'lab mono',style:'fill:var(--ink)',text:(r.upper?'≤':'')+r.days+'日'}));
      var hit=s('rect',{x:0,y:y-rowH/2,width:W,height:rowH,class:'hit'});hover(hit,function(){return [r.t.title_ja,[{k:'発売',v:r.t.release_date},{k:'確認できた日',v:r.m.as_of},{k:'その時点',v:fmtUnits(r.m.value)+'本'+(r.m.precision==='at_least'?'以上':'')},{k:'日数',v:r.days+'日'+(r.upper?'以内':'')}],[]];});svg.appendChild(hit);});
    mount('mileBox',svg);
    $('mileNote').textContent='世界の販売・出荷本数が100万本以上と確認できた最初の時点までの日数（'+rows.length+'作品）。塗りの点＝「100万本突破」の発表日。白抜きの点＝IR の一覧など四半期末の値で「その日までに」（実際はもっと早い）。最初の記録が500万本を超えていた作品（マリオカート ワールド・モンスターハンターワイルズ・バイオハザード レクイエム・ELDEN RING）は、100万本の時点が分からないので載せていない。';
    tv('mileTv',[['作品'],['発売日'],['確認日'],['本数','num'],['日数','num']],rows.map(function(r){return [r.t.title_ja,r.t.release_date,r.m.as_of,fmtUnits(r.m.value)+'本'+(r.m.precision==='at_least'?'以上':''),(r.upper?'≤':'')+r.days];}));
  }

  Promise.all([load('titles.csv'),load('milestones.csv'),load('rankings.csv'),load('indicators.csv'),load('indicator_defs.csv'),load('entities.csv')]).then(function(a){
    T=a[0];M=a[1];R=a[2];I=a[3];DEF=a[4];ENT=a[5];T.forEach(function(t){byId[t.id]=t;});ENT.forEach(function(e){entName[e.entity]=e.name_ja;entGroup[e.entity]=e.group;});
    I.filter(function(r){return r.indicator_id==='cpi_all_items_2020base';}).forEach(function(r){cpi[r.period_end.slice(0,4)]=Number(r.value);});
    drawKpi();drawShare();drawCountries();drawTrend();drawInvest();drawLabor();drawOwn();drawMile();
    $('realChk').addEventListener('change',drawTrend);
    $('counts').textContent='作品 '+T.length+'・数字 '+M.length+'・順位 '+R.length+'・指標 '+I.length+' 行';
  }).catch(function(e){document.querySelectorAll('[data-box]').forEach(function(b){b.innerHTML='';b.appendChild(h('p',{class:'lg-empty',text:'CSV を読めなかった（'+e.message+'）。file:// では開けないので、サーバー経由か公開 URL で開く。'}));});});
})();
'''

def sec(no, id, title, sub, inner):
    return ('<section class="ch" id="' + id + '">\n  <div class="ch-head"><span class="ch-no">' + no + '</span></div>\n  <h2>' + title + '</h2>\n  <p class="sub">' + sub + '</p>\n' + inner + '\n</section>\n')

body = ''
body += sec('00', 'kpis', '市場と人口 ── いまの大きさ', '世界と国内の市場、遊ぶ人の数、いちばん下の層の倒産。数字は台帳の最新値。', '  <div class="lg-kpi" data-box="1" id="kpi"></div>')
body += sec('01', 'share', '誰の作品が選ばれたか', '市場ごとの年間上位を、作品の国籍で塗り分けた帯。上から IP の持ち主・開発した拠点・販売や運営の会社の国。',
            '  <div class="lg-caveat"><b>この景色は日本に寄っている。</b>4つの表のうち2つは日本国内の売れ行き（自国の作品が強いのは当然）で、世界の側は PC（Steam）だけ。米国の家庭用・中国・世界のスマホは未収録。国内家庭用はパッケージ中心の集計で、ダウンロード比率の高い海外作品が実態より下に出る。「日本 IP 9/10」を世界の姿と読まないこと。</div>\n  <div class="lg-legend" id="shareLegend"></div>\n  <div class="lg-lists" data-box="1" id="shareBox"></div>\n  <p class="lg-note">Steam の帯は順位の無い「上位12本」。国籍の決め方は README の「順位表」。米国家庭用（Circana）・世界スマホ（Sensor Tower）の年間表は、出典が取れ次第足す。</p>\n  <details class="lg-tv"><summary>表で見る</summary><div id="shareTv"></div></details>')
body += sec('02', 'map', '世界のどこの会社か', '2025年の4つの表に出た作品を国で数えた棒。左から IP の持ち主・開発の拠点・販売運営の会社。日本の棒だけ緑。',
            '  <div class="lg-three" data-box="1" id="mapBox"></div>\n  <p class="lg-note" id="mapNote"></p>\n  <details class="lg-tv"><summary>表で見る</summary><div id="mapTv"></div></details>')
body += sec('03', 'trend', '勢い ── 売上と人数はどう動いたか', '会社ごとに、売上高（緑）と従業員数（灰）を最初の年＝100 の指数で並べた。上へ行くほど伸びた。',
            '  <div class="lg-ctl"><span class="lg-legend" style="margin:0"><span><i class="ln" style="--c:var(--k-jp)"></i>売上高</span><span><i class="ln" style="--c:var(--k-ot)"></i>従業員数</span></span><label class="lg-hint" style="margin-left:auto"><input type="checkbox" id="realChk" checked> 売上は実質（2020年価格）</label></div>\n  <div class="lg-smulti" data-box="1" id="trendBox"></div>\n  <p class="lg-note" id="trendNote"></p>\n  <details class="lg-tv"><summary>表で見る</summary><div id="trendTv"></div></details>')
body += sec('04', 'invest', '弾込め ── 開発にお金を積んでいるか', '会社が公表する研究開発費を売上高で割った比率の推移（自分の売上の何%を開発に回しているか）と、作りかけのゲームの残高の前年比。',
            '  <div class="lg-caveat"><b>会社をまたいで金額は比べない。</b>研究開発費の中身は会社ごとに違う（任天堂はハードの研究も含む。スクエニはゲームの制作費を資産に積むので費用は小さく出る。コナミは全事業）。比べてよいのは「同じ会社の中の推移」と「売上比の向き」まで。</div>\n  <p class="fig-title" style="margin-top:18px">研究開発費 ÷ 売上高 <small>%・線の終点が最新・下線が 0%</small></p>\n  <div class="lg-smulti" data-box="1" id="rdBox"></div>\n  <p class="lg-note" id="rdNote"></p>\n  <p class="fig-title" style="margin-top:30px">作りかけのゲームの残高（前年比） <small>右（青）が増加・左（橙）が減少・自社比</small></p>\n  <div class="lg-hbars" data-box="1" id="wipBox" style="max-width:560px"></div>\n  <p class="lg-note">仕掛品の定義：カプコン＝ゲームソフト仕掛品、スクエニ＝コンテンツ制作勘定、バンナム＝連結の仕掛品（玩具等も含む）、セガサミー＝エンタテインメントコンテンツ事業の仕掛品。開発費をその場で費用にする会社はこの棒に出ない。</p>\n  <details class="lg-tv"><summary>表で見る</summary><div id="rdTv"></div><div id="wipTv"></div></details>')
body += sec('05', 'labor', '労働の取り分 ── 稼ぎは人に回っているか', '1人が生んだ稼ぎを「本人の給与」と「会社に残る営業利益（1人あたり）」に分け、給与の側の割合を出した。50% なら同額。右ほど人に回っている。',
            '  <div class="lg-caveat"><b>読み方。</b>白抜きの点が3〜5年前、緑の点が最新。右へ動いていれば、利益より給与の方が速く増えた（人に回った）。左へ動いていれば、給与より利益の方が速く増えた（会社と株主に残った）。持株会社は給与が本社だけの値なので外してある。</div>\n  <div class="lg-hbars" data-box="1" id="laborBox"></div>\n  <p class="lg-note">給与＝提出会社（単体）の平均年間給与。1人あたり営業利益＝連結の営業利益÷連結の従業員数。本当の労働分配率（人件費の総額÷付加価値）は有報から取れないので、その代わりの物差し。営業赤字の年は「赤字」と表示し点を打たない。</p>\n  <details class="lg-tv"><summary>表で見る</summary><div id="laborTv"></div></details>')
body += sec('06', 'own', '資本の所在 ── 誰が株を持っているか', '日本の上場15社の、外国法人等の持株比率。縦線は半分。高いほど、配当と議決権の行き先が海外に寄る。',
            '  <div class="lg-hbars" data-box="1" id="ownBox"></div>\n  <p class="lg-note">これは「株を持たれている側」の数字で、多くは年金や投資信託などの機関投資家（経営権を取りに来る資本とは別）。逆向き＝日本の会社が海外のスタジオや IP を買う流れも同時にある（セガ→Rovio 2023、ソニー→Bungie 2022、任天堂→Shiver 2024 など）。その台帳はまだ無い＝次に足す。</p>\n  <details class="lg-tv"><summary>表で見る</summary><div id="ownTv"></div></details>')
body += sec('07', 'mile', '節目 ── 100万本までの速さ', '発売日を左端に置き、100万本に届いたと確認できた日を点で打った。左にあるほど速い。縦線は1か月・100日・1年。',
            '  <div class="fig" data-box="1" id="mileBox"></div>\n  <p class="lg-note" id="mileNote"></p>\n  <details class="lg-tv"><summary>表で見る</summary><div id="mileTv"></div></details>\n  <p class="lg-note">原本：<a href="titles.csv">titles.csv</a>・<a href="milestones.csv">milestones.csv</a>・<a href="rankings.csv">rankings.csv</a>・<a href="indicators.csv">indicators.csv</a>・<a href="indicator_defs.csv">indicator_defs.csv</a>・<a href="entities.csv">entities.csv</a>　<span id="counts"></span></p>')

html = ('<!DOCTYPE html>\n<html lang="ja">\n<head>\n<meta charset="utf-8">\n<meta name="robots" content="noindex,nofollow">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        '<title>データ台帳 ｜ ゲーム業界の理解を深める地図</title>\n<meta name="description" content="台帳の数字を図で読む裏の窓。">\n' + icon + '\n'
        '<meta name="theme-color" content="#f7f8fa" media="(prefers-color-scheme: light)">\n<meta name="theme-color" content="#14161a" media="(prefers-color-scheme: dark)">\n' + fonts + '\n'
        '<link rel="stylesheet" href="../style.css?v=' + ver + '">\n<style>' + css + '</style>\n</head>\n<body>\n\n' + toc + '\n\n' + hero + '\n\n<div class="wrap">\n\n' + head + '\n\n' + body + '\n' + by +
        '\n\n</div>\n<div id="tip" role="status" aria-live="polite"></div>\n<script src="../common.js?v=' + ver + '"></script>\n<script>' + js + '</script>\n</body>\n</html>\n')
io.open(D + 'data/index.html', 'w', encoding='utf-8', newline='').write(html)
print('ok data/index.html', len(html), 'bytes')
