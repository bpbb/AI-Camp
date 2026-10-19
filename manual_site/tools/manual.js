(function(){
  var body=document.body;
  // ปุ่ม copy
  document.addEventListener('click',function(e){
    var b=e.target.closest('.copy'); if(!b) return;
    var text=b.getAttribute('data-code');
    function done(){var o=b.textContent;b.textContent='คัดลอกแล้ว ✓';b.classList.add('done');
      setTimeout(function(){b.textContent=o;b.classList.remove('done')},1500)}
    function fallback(){var t=document.createElement('textarea');t.value=text;t.style.position='fixed';t.style.opacity='0';
      document.body.appendChild(t);t.select();try{document.execCommand('copy');done()}catch(_){b.textContent='คัดลอกไม่ได้'}document.body.removeChild(t)}
    if(navigator.clipboard&&window.isSecureContext){navigator.clipboard.writeText(text).then(done,fallback)}else{fallback()}
  });
  // เมนูมือถือ
  var menu=document.getElementById('menu'),scrim=document.getElementById('scrim');
  if(menu)menu.onclick=function(){body.classList.toggle('menu-open')};
  if(scrim)scrim.onclick=function(){body.classList.remove('menu-open')};
  document.getElementById('sidebar').addEventListener('click',function(e){if(e.target.closest('a'))body.classList.remove('menu-open')});
  // เปิด details ถ้าลิงก์ชี้เข้าไปข้างใน
  function openFor(){var id=decodeURIComponent(location.hash.slice(1));var el=id&&document.getElementById(id);
    while(el){if(el.tagName==='DETAILS')el.open=true;el=el.parentElement}}
  window.addEventListener('hashchange',openFor);openFor();
  // scroll-spy
  var chs=[].slice.call(document.querySelectorAll('.chapter'));
  var heads=[].slice.call(document.querySelectorAll('.chapter h2[id]'));
  var navCh={},navSub={};
  document.querySelectorAll('.toc .ch').forEach(function(li){navCh[li.dataset.ch]=li});
  document.querySelectorAll('.subs a').forEach(function(a){navSub[a.getAttribute('href').slice(1)]=a});
  var ticking=false;
  function spy(){ticking=false;var y=window.innerHeight*0.3,cur=chs[0],h=null;
    chs.forEach(function(c){if(c.getBoundingClientRect().top<=y)cur=c});
    heads.forEach(function(x){if(x.getBoundingClientRect().top<=y&&cur.contains(x))h=x});
    Object.keys(navCh).forEach(function(k){navCh[k].classList.toggle('active',cur&&k===cur.dataset.ch)});
    Object.keys(navSub).forEach(function(k){navSub[k].classList.toggle('on',h&&k===h.id)});
    var act=document.querySelector('.ch.active .on')||document.querySelector('.ch.active');
    if(act&&act.scrollIntoView&&!spy.skip){var sb=document.getElementById('sidebar'),r=act.getBoundingClientRect();
      if(r.top<80||r.bottom>window.innerHeight-40)sb.scrollTop+=r.top-window.innerHeight/2}}
  window.addEventListener('scroll',function(){if(!ticking){ticking=true;requestAnimationFrame(spy)}},{passive:true});
  spy();
})();
