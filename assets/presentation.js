(() => {
  'use strict';
  const revision = document.querySelector('meta[name="espada-revision"]')?.content || '';
  function versioned(href) {
    const url = new URL(href, location.href);
    if (revision) url.searchParams.set('v', revision);
    return url.href;
  }
  const pages = [
    ['home','Главная','Главная'],['kit','UI-кит и сквозные элементы','UI-кит'],
    ['design','Дизайн интерьера','Дизайн интерьера'],['materials','Комплектация','Комплектация'],
    ['acceptance','Приёмка квартир','Приёмка квартир'],['partners','Партнёрам','Партнёрам'],
    ['pillar','Шаблон раздела','Пиллар услуги'],['category','Шаблон услуги','Категория услуги'],
    ['portfolio','Портфолио и отзывы','Портфолио и отзывы'],['company','О компании и контакты','О компании и контакты'],
    ['blog','Блог','Блог'],['service','Служебные страницы','Служебные страницы'],
    ['forms','Формы и состояния','Формы'],['quiz','Квиз-калькуляторы','Квиз-калькуляторы'],['404','Страница не найдена','404'],
  ].map(([key,title,name])=>({key,title,file:name+'.dc.html'}));
  const variants = {
    pillar:['Ремонт квартир','Дизайн интерьера','Приёмка квартир'],
    category:['Ремонт в новостройке','Дизайн кухни','Приёмка без отделки'],
    portfolio:['Портфолио','Кейс','Отзывы'],company:['О компании','Контакты'],blog:['Список','Статья'],
    service:['Вопросы и ответы','Страница ЖК','Юридическая','404','Спасибо'],
  };
  const frame=document.getElementById('preview'), artboard=document.getElementById('artboard'), box=document.getElementById('artboard-box'), stage=document.getElementById('stage');
  let current=pages[0], selectedVariant='', context={}, device=innerWidth<650?'mobile':'desktop', applied='';
  const menu=document.getElementById('page-list');
  pages.forEach(p=>{const b=document.createElement('button');b.type='button';b.className='page-button';b.dataset.key=p.key;b.textContent=p.title;b.addEventListener('click',()=>navigate(p));menu.append(b);});
  function resetScroll() { stage.scrollTop=0; frame.contentWindow?.scrollTo({top:0,left:0,behavior:'instant'}); }
  function saveHash(){const hash=new URLSearchParams({page:current.key});if(context.servicePath){hash.set('path',context.servicePath);hash.set('title',context.serviceTitle);}else if(selectedVariant && selectedVariant!==(variants[current.key]||[])[0])hash.set('variant',selectedVariant);history.replaceState(null,'','#'+(hash.size>1?hash.toString():current.key));}
  function navigate(p, variant='', nextContext={}) {
    current=p;context=nextContext;selectedVariant=variant || (variants[p.key]||[])[0] || '';applied='';
    if (frame.src !== versioned(p.file)) frame.src=versioned(p.file);
    frame.title=p.title;document.getElementById('page-title').textContent=p.title;
    document.getElementById('open-page').href=versioned(p.file);
    document.title='Эспада — '+p.title;
    menu.querySelectorAll('button').forEach(b=>{if(b.dataset.key===p.key)b.setAttribute('aria-current','page');else b.removeAttribute('aria-current');});
    const bar=document.getElementById('variant-bar');bar.replaceChildren();bar.hidden=!variants[p.key];
    (variants[p.key]||[]).forEach(v=>{const b=document.createElement('button');b.type='button';b.textContent=v;b.setAttribute('aria-pressed',String(v===selectedVariant));b.addEventListener('click',()=>{selectedVariant=v;context={};applied='';bar.querySelectorAll('button').forEach(el=>el.setAttribute('aria-pressed',String(el===b)));saveHash();resetScroll();});bar.append(b);});
    saveHash();resetScroll();document.body.classList.remove('sidebar-open');
  }
  function route(href, title='') {
    const path=href.split(/[?#]/)[0].replace(/\/?$/,'/');
    let file=(window.ESPADA_ROUTES||{})[path];
    if(!file && /^\/(dizajn-(sovremennyj-stil|minimalizm|neoklassika|skandinavskij-stil|loft)|remont-posle-(zaliva|pozhara)|priyomka-(posle-remonta|kvartiry-po-renovatsii))\/$/.test(path))file='Категория услуги.dc.html';
    if(!file && /^(\/remont-v-zhk-|\/priyomka-v-zhk-)/.test(path))file='Служебные страницы.dc.html';
    if(!file && path.startsWith('/blog/'))file='Блог.dc.html';
    if(!file && path.startsWith('/portfolio/'))file='Портфолио и отзывы.dc.html';
    if(!file && (window.ESPADA_KNOWN||[]).includes(path))file='Категория услуги.dc.html';
    let variant='';
    if(path==='/otzyvy/')variant='Отзывы';else if(path==='/kontakty/')variant='Контакты';
    else if(path.startsWith('/portfolio/') && path!=='/portfolio/')variant='Кейс';
    else if(path.startsWith('/blog/') && path!=='/blog/')variant='Статья';
    else if(path==='/faq/')variant='Вопросы и ответы';
    else if(/(politika|soglasie)/.test(path))variant='Юридическая';
    else if(path.includes('zhk'))variant='Страница ЖК';
    else if(file==='Категория услуги.dc.html')variant=path.startsWith('/dizajn')?'Дизайн кухни':path.startsWith('/priyomka')?'Приёмка без отделки':'Ремонт в новостройке';
    const target=pages.find(p=>p.file===file)||pages.find(p=>p.key==='404');
    const serviceTitle=(window.ESPADA_TITLES||{})[path] || title;
    const serviceContext=['pillar','category'].includes(target.key) && serviceTitle ? {serviceTitle,servicePath:path} : {};
    navigate(target,variant,serviceContext);
  }
  function wire(doc) {
    if(doc.__presentationWired)return;doc.__presentationWired=true;
    doc.addEventListener('click',e=>{if(e.defaultPrevented)return;const a=e.target.closest('a');if(!a)return;const href=a.getAttribute('href');if(!href||/^(#|tel:|mailto:)/i.test(href)||a.hasAttribute('download'))return;e.preventDefault();if(/^https?:/i.test(href)){window.open(href,'_blank','noopener');return;}if(href.endsWith('.dc.html'))navigate(pages.find(p=>p.file===href)||pages[0]);else route(href,a.innerText.trim());});
  }
  function fit() {
    const doc=frame.contentDocument, win=frame.contentWindow;if(!doc||!doc.body)return;
    const standalone=new URL(versioned(current.file));if(selectedVariant)standalone.searchParams.set('page',selectedVariant);Object.entries(context).forEach(([key,value])=>standalone.searchParams.set(key,value));document.getElementById('open-page').href=standalone.href;
    const mobile=device==='mobile',width=mobile?390:1440;
    artboard.style.width=(width+(mobile?12:0))+'px';artboard.classList.toggle('is-mobile',mobile);stage.classList.toggle('is-mobile',mobile);
    if(win.__dcSetProps && win.__dcRootName){const signature=current.key+'|'+selectedVariant+'|'+device+'|'+JSON.stringify(context);if(applied!==signature){win.__dcSetProps(win.__dcRootName(),{mobile,page:selectedVariant,...context});applied=signature;}}
    wire(doc);
    const stageStyle=getComputedStyle(stage),paddingX=parseFloat(stageStyle.paddingLeft)+parseFloat(stageStyle.paddingRight),paddingY=parseFloat(stageStyle.paddingTop)+parseFloat(stageStyle.paddingBottom);
    const scale=Math.min(1,(stage.clientWidth-paddingX)/artboard.offsetWidth);
    const height=Math.floor((stage.clientHeight-paddingY)/scale)-(mobile?12:0);
    frame.style.height=Math.max(200,height)+'px';
    doc.body.style.setProperty('--demo-visible-top',Math.max(0,win.scrollY)+'px');
    doc.body.style.setProperty('--demo-visible-height',win.innerHeight+'px');
    artboard.style.transform='scale('+scale+')';box.style.width=Math.ceil(artboard.offsetWidth*scale)+'px';box.style.height=Math.ceil(artboard.offsetHeight*scale)+'px';
    document.querySelectorAll('[data-device]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.device===device)));
  }
  frame.addEventListener('load',()=>{applied='';fit();});
  window.__espadaNavigate = (href,title) => { document.querySelectorAll('dialog').forEach(d=>d.close()); route(href,title); };
  document.querySelectorAll('[data-device]').forEach(b=>b.addEventListener('click',()=>{device=b.dataset.device;applied='';resetScroll();fit();}));
  document.getElementById('menu-toggle').addEventListener('click',()=>{if(innerWidth<=900){document.body.classList.toggle('sidebar-open');}else{document.body.classList.toggle('sidebar-closed');}document.getElementById('menu-toggle').setAttribute('aria-expanded',String(!document.body.classList.contains('sidebar-closed')));fit();});
  function fromHash(){const hash=location.hash.slice(1);if(hash.startsWith('page=')){const params=new URLSearchParams(hash);if(params.get('path'))route(params.get('path'),params.get('title')||'');else navigate(pages.find(p=>p.key===params.get('page'))||pages[0],params.get('variant')||'');}else navigate(pages.find(p=>p.key===hash)||pages[0]);}
  fromHash();addEventListener('hashchange',fromHash);
  setInterval(fit,250);addEventListener('resize',fit);
})();
