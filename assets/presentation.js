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
  let current=pages[0], selectedVariant='', device=innerWidth<650?'mobile':'desktop', applied='';
  const menu=document.getElementById('page-list');
  pages.forEach(p=>{const b=document.createElement('button');b.type='button';b.className='page-button';b.dataset.key=p.key;b.textContent=p.title;b.addEventListener('click',()=>navigate(p));menu.append(b);});
  function navigate(p, variant='') {
    current=p;selectedVariant=variant || (variants[p.key]||[])[0] || '';applied='';
    if (frame.src !== versioned(p.file)) frame.src=versioned(p.file);
    frame.title=p.title;document.getElementById('page-title').textContent=p.title;
    document.getElementById('open-page').href=versioned(p.file);
    document.title='Эспада — '+p.title;
    menu.querySelectorAll('button').forEach(b=>{if(b.dataset.key===p.key)b.setAttribute('aria-current','page');else b.removeAttribute('aria-current');});
    const bar=document.getElementById('variant-bar');bar.replaceChildren();bar.hidden=!variants[p.key];
    (variants[p.key]||[]).forEach(v=>{const b=document.createElement('button');b.type='button';b.textContent=v;b.setAttribute('aria-pressed',String(v===selectedVariant));b.addEventListener('click',()=>{selectedVariant=v;applied='';bar.querySelectorAll('button').forEach(el=>el.setAttribute('aria-pressed',String(el===b)));stage.scrollTop=0;});bar.append(b);});
    history.replaceState(null,'','#'+p.key);stage.scrollTop=0;document.body.classList.remove('sidebar-open');
  }
  function route(href) {
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
    navigate(pages.find(p=>p.file===file)||pages.find(p=>p.key==='404'),variant);
  }
  function wire(doc) {
    if(doc.__presentationWired)return;doc.__presentationWired=true;
    doc.addEventListener('click',e=>{if(e.defaultPrevented)return;const a=e.target.closest('a');if(!a)return;const href=a.getAttribute('href');if(!href||/^(#|tel:|mailto:)/i.test(href)||a.hasAttribute('download'))return;e.preventDefault();if(/^https?:/i.test(href)){window.open(href,'_blank','noopener');return;}if(href.endsWith('.dc.html'))navigate(pages.find(p=>p.file===href)||pages[0]);else route(href);});
  }
  function fit() {
    const doc=frame.contentDocument, win=frame.contentWindow;if(!doc||!doc.body)return;
    document.getElementById('open-page').href=versioned(current.file+(selectedVariant?'?page='+encodeURIComponent(selectedVariant):''));
    const mobile=device==='mobile',width=mobile?390:1440;
    artboard.style.width=(width+(mobile?12:0))+'px';artboard.classList.toggle('is-mobile',mobile);stage.classList.toggle('is-mobile',mobile);
    if(win.__dcSetProps && win.__dcRootName){const signature=current.key+'|'+selectedVariant+'|'+device;if(applied!==signature){win.__dcSetProps(win.__dcRootName(),{mobile,page:selectedVariant});applied=signature;}}
    wire(doc);
    const root=doc.body.firstElementChild;
    const height=Math.max(root?root.scrollHeight:0,root?root.getBoundingClientRect().height:0,200);
    frame.style.height=Math.ceil(height)+'px';
    const padding=parseFloat(getComputedStyle(stage).paddingLeft)*2;
    const scale=Math.min(1,(stage.clientWidth-padding)/artboard.offsetWidth);
    doc.body.style.setProperty('--demo-visible-top',Math.max(0,stage.scrollTop/scale)+'px');
    doc.body.style.setProperty('--demo-visible-height',((stage.clientHeight-padding)/scale)+'px');
    artboard.style.transform='scale('+scale+')';box.style.width=Math.ceil(artboard.offsetWidth*scale)+'px';box.style.height=Math.ceil(artboard.offsetHeight*scale)+'px';
    document.querySelectorAll('[data-device]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.device===device)));
  }
  frame.addEventListener('load',()=>{applied='';fit();});
  window.__espadaNavigate = href => { document.querySelectorAll('dialog').forEach(d=>d.close()); route(href); };
  document.querySelectorAll('[data-device]').forEach(b=>b.addEventListener('click',()=>{device=b.dataset.device;applied='';stage.scrollTop=0;fit();}));
  document.getElementById('menu-toggle').addEventListener('click',()=>{if(innerWidth<=900){document.body.classList.toggle('sidebar-open');}else{document.body.classList.toggle('sidebar-closed');}document.getElementById('menu-toggle').setAttribute('aria-expanded',String(!document.body.classList.contains('sidebar-closed')));fit();});
  navigate(pages.find(p=>p.key===location.hash.slice(1))||pages[0]);
  addEventListener('hashchange',()=>navigate(pages.find(p=>p.key===location.hash.slice(1))||pages[0]));
  setInterval(fit,250);addEventListener('resize',fit);
})();
