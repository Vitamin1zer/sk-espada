(() => {
  'use strict';
  const revision = document.querySelector('meta[name="espada-revision"]')?.content || '';
  function versioned(href) {
    const url = new URL(href, location.href);
    if (revision) url.searchParams.set('v', revision);
    return url.href;
  }
  const pages = [
    ['kit','UI-кит и сквозные элементы','UI-кит'],['home','Главная','Главная'],
    ['renovation','Ремонт квартир','Пиллар услуги'],['design','Дизайн интерьера','Дизайн интерьера'],
    ['acceptance','Приёмка','Приёмка квартир'],['materials','Комплектация','Комплектация'],
    ['services','Услуги','Услуги'],['partners','Партнёрам','Партнёрам'],
    ['portfolio','Портфолио и отзывы','Портфолио и отзывы'],['company','О компании и контакты','О компании и контакты'],
    ['blog','Блог','Блог'],['service','Служебные страницы','Служебные страницы'],
    ['forms','Формы и состояния','Формы'],['quiz','Квиз-калькуляторы','Квиз-калькуляторы'],['404','Страница не найдена','404'],
  ].map(([key,title,name])=>({key,title,file:name+'.dc.html'}));
  const variants = {
    portfolio:['Портфолио','Кейс','Отзывы'],company:['О компании','Контакты'],blog:['Список','Статья'],
    service:['Вопросы и ответы','Страница ЖК','Юридическая','404','Спасибо'],
  };
  const category={key:'category',title:'Услуга',file:'Категория услуги.dc.html'};
  const sections=window.ESPADA_SERVICE_MENU;
  const frame=document.getElementById('preview'), artboard=document.getElementById('artboard'), box=document.getElementById('artboard-box'), stage=document.getElementById('stage');
  let current=pages.find(p=>p.key==='home'), selectedVariant='', context={}, device=innerWidth<650?'mobile':'desktop', applied='';
  const menu=document.getElementById('page-list');
  pages.forEach(p=>{const b=document.createElement('button');b.type='button';b.className='page-button';b.dataset.key=p.key;b.textContent=p.title;b.addEventListener('click',()=>navigate(p));menu.append(b);});
  function resetScroll() { stage.scrollTop=0; frame.contentWindow?.scrollTo({top:0,left:0,behavior:'instant'}); }
  function saveHash(){const hash=new URLSearchParams({page:current.key});if(context.servicePath){hash.set('path',context.servicePath);hash.set('title',context.serviceTitle);hash.set('section',context.serviceSection);}else if(selectedVariant && selectedVariant!==(variants[current.key]||[])[0])hash.set('variant',selectedVariant);history.replaceState(null,'','#'+(hash.size>1?hash.toString():current.key));}
  function sectionBar(bar, section) {
    const overview=document.createElement('button');overview.type='button';overview.textContent='Основная страница';
    overview.setAttribute('aria-pressed',String(!context.servicePath || context.servicePath===section.href));
    overview.addEventListener('click',()=>route(section.href));bar.append(overview);
    const label=document.createElement('label');label.className='service-picker';label.textContent='Услуга раздела';
    const select=document.createElement('select');select.setAttribute('aria-label','Услуга раздела');
    const placeholder=document.createElement('option');placeholder.value='';placeholder.textContent='Выберите услугу';select.append(placeholder);
    section.groups.forEach(group=>{
      const optgroup=document.createElement('optgroup');optgroup.label=group.title || 'По виду ремонта — продолжение';
      if(group.href){const option=document.createElement('option');option.value=group.href;option.textContent='Все: '+group.title;optgroup.append(option);}
      group.items.filter(item=>item.href!==section.href).forEach(item=>{const option=document.createElement('option');option.value=item.href;option.textContent=item.t;optgroup.append(option);});
      select.append(optgroup);
    });
    select.value=context.servicePath || '';select.addEventListener('change',()=>{if(select.value)route(select.value,'',section.key);});
    label.append(select);bar.append(label);
  }
  function renderBar() {
    const bar=document.getElementById('variant-bar');bar.replaceChildren();
    const section=sections.find(s=>s.key===(context.serviceSection || current.key));
    bar.hidden=!section?.groups.length && !variants[current.key];
    if(section?.groups.length){sectionBar(bar,section);return;}
    (variants[current.key]||[]).forEach(v=>{const b=document.createElement('button');b.type='button';b.textContent=v;b.setAttribute('aria-pressed',String(v===selectedVariant));b.addEventListener('click',()=>navigate(current,v));bar.append(b);});
  }
  function navigate(p, variant='', nextContext={}) {
    current=p;context=nextContext;selectedVariant=variant || (variants[p.key]||[])[0] || '';applied='';
    if (frame.src !== versioned(p.file)) frame.src=versioned(p.file);
    const title=context.serviceTitle || p.title;
    frame.title=title;document.getElementById('page-title').textContent=title;
    document.getElementById('open-page').href=versioned(p.file);
    document.title='Эспада — '+title;
    menu.querySelectorAll('button').forEach(b=>{if(b.dataset.key===(context.serviceSection || p.key))b.setAttribute('aria-current','page');else b.removeAttribute('aria-current');});
    renderBar();
    saveHash();resetScroll();document.body.classList.remove('sidebar-open');
  }
  function route(href, title='', sectionHint='') {
    const path=href.split(/[?#]/)[0].replace(/\/?$/,'/');
    const matching=sections.filter(s=>s.href===path || s.groups.some(g=>g.href===path || g.items.some(i=>i.href===path)));
    const section=matching.find(s=>s.key===sectionHint) || matching[0];
    let file=(window.ESPADA_ROUTES||{})[path];
    if(!file && section && path.includes('-v-zhk-'))file=category.file;
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
    const target=(file===category.file ? category : pages.find(p=>p.file===file))||pages.find(p=>p.key==='404');
    const serviceTitle=(window.ESPADA_TITLES||{})[path] || title;
    const isNested=section && path!==section.href;
    const serviceContext=(isNested || target.key==='services' && path!=='/uslugi/') && serviceTitle
      ? {serviceTitle,servicePath:path,serviceSection:section?.key || 'services',serviceParentTitle:section?.title || 'Услуги',serviceParentPath:section?.href || '/uslugi/'} : {};
    if(section && path===section.href){navigate(pages.find(p=>p.key===section.key));return;}
    navigate(target,variant,serviceContext);
  }
  function wire(doc) {
    if(doc.__presentationWired)return;doc.__presentationWired=true;
    doc.addEventListener('click',e=>{if(e.defaultPrevented)return;const a=e.target.closest('a');if(!a)return;const href=a.getAttribute('href');if(!href||/^(#|tel:|mailto:)/i.test(href)||a.hasAttribute('download'))return;e.preventDefault();if(/^https?:/i.test(href)){window.open(href,'_blank','noopener');return;}if(href.endsWith('.dc.html'))navigate(pages.find(p=>p.file===href)||pages[0]);else route(href,a.innerText.trim(),a.closest('[data-service-section]')?.dataset.serviceSection);});
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
  window.__espadaNavigate = (href,title,sectionHint) => { document.querySelectorAll('dialog').forEach(d=>d.close()); route(href,title,sectionHint); };
  document.querySelectorAll('[data-device]').forEach(b=>b.addEventListener('click',()=>{device=b.dataset.device;applied='';resetScroll();fit();}));
  document.getElementById('menu-toggle').addEventListener('click',()=>{if(innerWidth<=900){document.body.classList.toggle('sidebar-open');}else{document.body.classList.toggle('sidebar-closed');}document.getElementById('menu-toggle').setAttribute('aria-expanded',String(!document.body.classList.contains('sidebar-closed')));fit();});
  function legacyPage(key,variant='') {
    if(key==='pillar'){route(variant==='Дизайн интерьера'?'/dizajn-interera/':variant==='Приёмка квартир'?'/priyomka-kvartir-v-novostrojke/':'/remont-kvartir-pod-klyuch/');return;}
    if(key==='category'){route(variant==='Дизайн кухни'?'/dizajn-kuhni/':variant==='Приёмка без отделки'?'/priyomka-kvartiry-bez-otdelki/':'/remont-kvartiry-v-novostrojke/');return;}
    navigate(pages.find(p=>p.key===key)||pages.find(p=>p.key==='home'),variant);
  }
  function fromHash(){const hash=location.hash.slice(1);if(hash.startsWith('page=')){const params=new URLSearchParams(hash);if(params.get('path'))route(params.get('path'),params.get('title')||'',params.get('section')||'');else legacyPage(params.get('page'),params.get('variant')||'');}else legacyPage(hash);}
  fromHash();addEventListener('hashchange',fromHash);
  setInterval(fit,250);addEventListener('resize',fit);
})();
