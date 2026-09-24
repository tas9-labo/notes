// 共通の振る舞い（index.html と dev.html で共用）：用語のポップアップ・注釈・印刷時の展開・上の目次
(function(){
  // 用語のポップアップ：用語集の dl を辞書にして、各章で最初に出てきた用語に点線を付ける
  var defs={},canon={};
  document.querySelectorAll('#terms .terms > div').forEach(function(d){
    var dt=d.querySelector('dt').cloneNode(true),sm=dt.querySelector('small'),alias=sm?sm.textContent.trim():'';
    if(sm)dt.removeChild(sm);
    var k=dt.textContent.trim();
    defs[k]=d.querySelector('dd').textContent;canon[k]=k;
    if(alias==='開発会社'||alias==='基本無料'){canon[alias]=k;}   // 本文でこの呼び方でも出てくるもの
  });
  var keys=Object.keys(canon).sort(function(a,b){return b.length-a.length;});
  function findTerm(text,k){
    if(!/^[A-Za-z0-9]+$/.test(k))return text.indexOf(k);
    var m=new RegExp('(^|[^A-Za-z0-9])'+k+'(?![A-Za-z0-9])').exec(text);   // 英字の用語は単語の途中に当てない
    return m?m.index+m[1].length:-1;
  }
  function wrapTerms(node,used){
    var text=node.nodeValue,best=-1,bk=null;
    keys.forEach(function(k){
      if(used[canon[k]])return;
      var i=findTerm(text,k);
      if(i>=0&&(best<0||i<best)){best=i;bk=k;}
    });
    if(!bk)return;
    var hit=node.splitText(best),rest=hit.splitText(bk.length),s=document.createElement('span');
    s.className='term';s.tabIndex=0;s.setAttribute('role','button');s.setAttribute('data-term',canon[bk]);s.textContent=bk;
    hit.parentNode.replaceChild(s,hit);
    used[canon[bk]]=true;
    wrapTerms(rest,used);
  }
  document.querySelectorAll('section.ch').forEach(function(sec){
    if(sec.id==='terms'||sec.id==='src'||sec.id==='sum')return;
    var used={},list=[],w=document.createTreeWalker(sec,NodeFilter.SHOW_TEXT,{acceptNode:function(n){
      var p=n.parentElement;
      return (!p||p.closest('a,button,summary,h2,svg,script,.tag,.ch-no,.axes,.models,.jc,.bands,.memo,.srcline,.point,.fig-title,.way-h,.chain,.type-cap,.people,.term'))?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_ACCEPT;
    }});
    while(w.nextNode())list.push(w.currentNode);
    list.forEach(function(n){wrapTerms(n,used);});
  });
  var pop=document.createElement('div');pop.id='pop';pop.hidden=true;pop.setAttribute('role','tooltip');document.body.appendChild(pop);
  function showPop(el,title,body){
    if(!pop.hidden&&pop._for===el){pop.hidden=true;return;}   // 同じものをもう一度押したら閉じる
    var b=document.createElement('b');b.textContent=title;
    pop.textContent='';pop.appendChild(b);
    String(body).split('\n').forEach(function(line){var q=document.createElement('p');q.textContent=line;pop.appendChild(q);});
    pop.hidden=false;pop._for=el;
    var r=el.getBoundingClientRect(),pw=pop.offsetWidth,vw=document.documentElement.clientWidth,
        x=Math.min(Math.max(8,r.left+r.width/2-pw/2),vw-pw-8);
    pop.style.left=(x+window.scrollX)+'px';pop.style.top=(r.bottom+window.scrollY+8)+'px';
  }
  function showTerm(el){var k=el.getAttribute('data-term');showPop(el,k,defs[k]);}
  function showNote(el){var t=el.querySelector('.nt');showPop(el,t?t.textContent:el.getAttribute('data-title'),el.getAttribute('data-note'));}
  document.addEventListener('click',function(e){
    var c=e.target.closest?e.target:null,t=c&&c.closest('.term'),n=c&&c.closest('[data-note]');
    if(t){showTerm(t);}else if(n){showNote(n);}else if(!(c&&c.closest('#pop'))){pop.hidden=true;}
  });
  document.addEventListener('keydown',function(e){
    if(e.key==='Escape'){pop.hidden=true;return;}
    if((e.key==='Enter'||e.key===' ')&&e.target.classList&&e.target.classList.contains('term')){e.preventDefault();showTerm(e.target);}
  });
  window.addEventListener('scroll',function(){pop.hidden=true;},{passive:true});

  // 印刷の前に、畳んである部分（問い・補足）を開く。終わったら元に戻す
  var reopened=[];
  window.addEventListener('beforeprint',function(){
    document.querySelectorAll('details:not([open])').forEach(function(d){d.open=true;reopened.push(d);});
  });
  window.addEventListener('afterprint',function(){reopened.forEach(function(d){d.open=false;});reopened=[];});

  // 上の目次：いま読んでいる章を強調する
  var links={},navUl=document.querySelector('nav.toc ul');
  document.querySelectorAll('nav.toc ul a').forEach(function(a){links[a.getAttribute('href').slice(1)]=a;});
  if('IntersectionObserver' in window){
    var spy=new IntersectionObserver(function(es){
      es.forEach(function(en){
        if(!en.isIntersecting)return;
        Object.keys(links).forEach(function(id){links[id].removeAttribute('aria-current');});
        var a=links[en.target.id];if(!a)return;
        a.setAttribute('aria-current','true');
        navUl.scrollLeft=a.offsetLeft-(navUl.clientWidth-a.offsetWidth)/2;
      });
    },{rootMargin:'-45% 0px -50% 0px'});
    Object.keys(links).forEach(function(id){var s=document.getElementById(id);if(s)spy.observe(s);});
  }

  // 入口カードが見えなくなったら、上に目次を出す
  var nav=document.querySelector('nav.toc'),hero=document.getElementById('chapters');
  if(!nav||!hero)return;
  if('IntersectionObserver' in window){
    new IntersectionObserver(function(e){
      nav.classList.toggle('show',!e[0].isIntersecting&&e[0].boundingClientRect.top<0);
    }).observe(hero);
  }
})();

/* アクセス記録（自前・analytics.gs の受け口へ送る）。送るのは ページ・参照元・訪問者の印（乱数）・タイムゾーン・言語・画面幅・UA だけ。
   自分の端末を数えない：一度だけ ?nocount=1 を付けて開くと、そのブラウザは以後送らない（localStorage に印を持つ）。 */
(function(){
  var ANALYTICS_URL='';
  try{
    if(!ANALYTICS_URL)return;
    if(location.protocol==='file:')return;
    if(/[?&]nocount=1/.test(location.search)){localStorage.setItem('nocount','1');}
    if(localStorage.getItem('nocount')==='1')return;
    var vid=localStorage.getItem('vid');
    if(!vid){vid=Math.random().toString(36).slice(2,10)+Date.now().toString(36);localStorage.setItem('vid',vid);}
    var tz='';try{tz=Intl.DateTimeFormat().resolvedOptions().timeZone||'';}catch(e){}
    var body=JSON.stringify({p:location.pathname,r:document.referrer,v:vid,tz:tz,l:navigator.language,w:screen.width,ua:navigator.userAgent});
    if(navigator.sendBeacon){navigator.sendBeacon(ANALYTICS_URL,body);}
    else{fetch(ANALYTICS_URL,{method:'POST',mode:'no-cors',body:body,keepalive:true});}
  }catch(e){}
})();
