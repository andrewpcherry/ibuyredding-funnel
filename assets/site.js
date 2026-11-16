(function(){
  var reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Lead form: contact details first (step 1), then optional situation questions (step 2).
  // PREVIEW MODE: nothing is sent. At launch, step 1 posts the lead to GHL (so a drop-off is
  // still captured) and step 2 updates that lead with the situations chosen.
  document.querySelectorAll('[data-lead-form]').forEach(function(form){
    var err=form.querySelector('.lf-error');
    function show(n){
      form.querySelectorAll('.lf-step').forEach(function(s){s.hidden=s.getAttribute('data-step')!==String(n);});
      var cur=form.querySelector('[data-step="'+n+'"]');
      if(form.getBoundingClientRect().top<70)form.scrollIntoView({behavior:reduce?'auto':'smooth',block:'start'});
      cur.focus({preventScroll:true});
    }
    form.addEventListener('submit',function(e){
      e.preventDefault();
      var el=form.elements,miss=[],first=null;
      function check(name,label,ok){var f=el.namedItem(name),bad=!ok(f.value.trim());f.setAttribute('aria-invalid',bad?'true':'false');if(bad){miss.push(label);if(!first)first=f;}}
      check('firstName','your first name',function(v){return v.length>0;});
      check('lastName','your last name',function(v){return v.length>0;});
      check('address','the property address',function(v){return v.length>4;});
      check('phone','a 10-digit phone number',function(v){var d=v.replace(/\D/g,'');return d.length===10||(d.length===11&&d.charAt(0)==='1');});
      check('email','a valid email (or leave it blank)',function(v){return !v||/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);});
      if(miss.length){err.textContent='Please add '+miss.join(', ')+'.';err.hidden=false;first.focus();return;}
      err.hidden=true;
      form.querySelector('[data-first]').textContent=el.namedItem('firstName').value.trim();
      show(2);
    });
    form.querySelectorAll('[data-next]').forEach(function(b){b.addEventListener('click',function(){show(3);});});
  });

  // Mobile menu
  var toggle=document.querySelector('.menu-toggle'),nav=document.getElementById('navigation');
  if(toggle&&nav){
    toggle.addEventListener('click',function(){var open=toggle.getAttribute('aria-expanded')!=='true';toggle.setAttribute('aria-expanded',String(open));nav.classList.toggle('open',open);});
  }

  // Header shadow and sticky mobile CTA
  var header=document.querySelector('[data-header]'),sticky=document.querySelector('[data-sticky]'),hero=document.querySelector('.hero,.page-hero');
  function onScroll(){
    var y=window.scrollY;
    if(header)header.classList.toggle('scrolled',y>10);
    if(sticky)sticky.classList.toggle('show',y>(hero?hero.offsetHeight-120:300));
  }
  window.addEventListener('scroll',onScroll,{passive:true});onScroll();

  // Resource library search
  var search=document.getElementById('resource-search');
  if(search){
    search.addEventListener('input',function(){
      var q=search.value.trim().toLowerCase(),count=0;
      document.querySelectorAll('.library .resource-card').forEach(function(c){c.hidden=q&&!c.textContent.toLowerCase().includes(q);if(!c.hidden)count++;});
      document.getElementById('no-results').hidden=count>0;
    });
  }

  // House grid: 100 squares, about 35 built before 1939, about 8 built 2000 or later
  var grid=document.querySelector('[data-grid]');
  if(grid){var h='';for(var i=0;i<100;i++){h+='<i class="'+(i<35?'old':(i>=92?'new':''))+'" style="transition-delay:'+(i*12)+'ms"></i>';}grid.innerHTML=h;}

  function countUp(el){
    var target=parseFloat(el.dataset.count),dec=+el.dataset.dec||0,suffix=el.dataset.suffix||'';
    var fmt=function(v){return v.toLocaleString('en-US',{minimumFractionDigits:dec,maximumFractionDigits:dec})+suffix;};
    if(reduce){el.textContent=fmt(target);return;}
    var t0=null;
    function step(t){if(!t0)t0=t;var p=Math.min((t-t0)/1400,1);el.textContent=fmt(target*(1-Math.pow(1-p,3)));if(p<1)requestAnimationFrame(step);}
    requestAnimationFrame(step);
  }

  var items=document.querySelectorAll('.reveal');
  if(!('IntersectionObserver' in window)||reduce){
    document.documentElement.classList.add('no-js');
    items.forEach(function(el){el.classList.add('in');});
    if(grid)grid.classList.add('on');
    return;
  }
  var io=new IntersectionObserver(function(entries){
    entries.forEach(function(en){
      if(!en.isIntersecting)return;
      var el=en.target;el.classList.add('in');
      if(el.classList.contains('mke-copy'))el.querySelectorAll('[data-count]').forEach(countUp);
      if(el.classList.contains('mke-visual')&&grid)grid.classList.add('on');
      io.unobserve(el);
    });
  },{threshold:.12,rootMargin:'0px 0px -30px 0px'});
  items.forEach(function(el){io.observe(el);});
})();
