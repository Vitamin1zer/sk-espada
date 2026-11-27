/* Общие попапы макетов. Сетевые запросы с контактами здесь не выполняются. */
(() => {
  'use strict';
  const forms = {
    repair: { kind: 'Попап', title: 'Получите индивидуальный расчёт сметы', cta: 'Бесплатный расчёт сметы' },
    design: { kind: 'Дизайн', title: 'Рассчитать стоимость дизайна', cta: 'Рассчитать стоимость дизайна' },
    acceptance: { kind: 'Приёмка', title: 'Заказать приёмку квартиры', cta: 'Вызвать приёмщика' },
    showroom: { kind: 'Шоурум', title: 'Посетить шоурум', cta: 'Записаться в шоурум' },
    partner: { kind: 'Партнёрство', title: 'Стать партнёром Эспады', cta: 'Стать партнёром' },
    viewing: { kind: 'Просмотр объектов', title: 'Посмотрите наши объекты', cta: 'Посмотреть объекты' },
  };
  function openPopup(config, quiz = false) {
    if (window.parent !== window && window.parent.__espadaOpenPopup) {
      window.parent.__espadaOpenPopup({ ...config, mobile: innerWidth <= 700 }, quiz);
      return;
    }
    let dialog = document.querySelector('dialog.espada-dialog');
    if (dialog) dialog.close();
    dialog = document.createElement('dialog');
    dialog.className = 'espada-dialog';
    if(config.mobile)dialog.classList.add('espada-dialog--mobile');
    dialog.setAttribute('aria-label', config.title);
    const close = document.createElement('button');
    close.type = 'button';
    close.className = 'espada-dialog__close';
    close.setAttribute('aria-label', 'Закрыть форму');
    close.textContent = '×';
    close.addEventListener('click', () => dialog.close());
    const frame = document.createElement('iframe');
    frame.title = config.title;
    const popupUrl = new URL(quiz ? 'Квиз.dc.html' : 'Форма.dc.html', location.href);
    popupUrl.searchParams.set('kind', config.kind);
    const revision = document.querySelector('meta[name="espada-revision"]')?.content;
    if (revision) popupUrl.searchParams.set('v', revision);
    frame.src = popupUrl.href;
    dialog.append(close, frame);
    document.body.append(dialog);
    let timer;
    frame.addEventListener('load', () => {
      let configured = false;
      timer = setInterval(() => {
        const win = frame.contentWindow;
        if (!win.__dcSetProps || !win.__dcRootName || !frame.contentDocument.getElementById('dc-root')) return;
        if (!configured) {
          win.__dcSetProps(win.__dcRootName(), { ...config, modal: true });
          configured = true;
        }
        const root = frame.contentDocument.getElementById('dc-root') || frame.contentDocument.body.firstElementChild;
        if (root) frame.style.height = Math.max(460, root.scrollHeight) + 'px';
      }, 150);
    });
    dialog.addEventListener('close', () => { clearInterval(timer); dialog.remove(); }, { once: true });
    dialog.addEventListener('click', e => { if (e.target === dialog) dialog.close(); });
    dialog.showModal();
    close.focus();
  }
  window.__espadaOpenPopup = openPopup;
  window.__espadaClosePopup = () => {
    const dialog=document.querySelector('dialog.espada-dialog[open]');
    if(!dialog)return false;
    dialog.close();return true;
  };
  document.addEventListener('keydown',e=>{
    if(e.key==='Escape' && window.parent!==window && window.parent.__espadaClosePopup?.())e.preventDefault();
  });
  const mobileViewport = matchMedia('(max-width:700px)');
  function responsiveProps() {
    // The shell and dialog configure their child once it is ready. A second
    // owner would replace page/kind/context overrides after the first render.
    if(window.parent!==window && (window.parent.__espadaNavigate || window.frameElement?.closest('dialog.espada-dialog')))return true;
    if (!window.__dcSetProps || !window.__dcRootName || !document.getElementById('dc-root')) return false;
    const params=new URLSearchParams(location.search),page=params.get('page');
    const context={};['serviceTitle','servicePath','serviceSection','serviceParentTitle','serviceParentPath'].forEach(key=>{if(params.get(key))context[key]=params.get(key);});
    window.__dcSetProps(window.__dcRootName(), Object.assign({ mobile: mobileViewport.matches }, page ? { page } : {},context));
    return true;
  }
  let attempts = 0;
  const boot = setInterval(() => { if (responsiveProps() || ++attempts > 100) clearInterval(boot); }, 100);
  mobileViewport.addEventListener('change', responsiveProps);
  document.addEventListener('click', e => {
    const link = e.target.closest('a');
    if (link && !e.defaultPrevented) {
      const href = link.getAttribute('href') || '';
      if (href.startsWith('/') && window.parent !== window && window.parent.__espadaNavigate) {
        e.preventDefault();
        window.parent.__espadaNavigate(href,(link.querySelector('h2,h3')?.textContent || link.innerText).trim(),link.closest('[data-service-section]')?.dataset.serviceSection);
        return;
      }
    }
    const control = e.target.closest('[data-open-form], [data-open-quiz]');
    if (!control) return;
    e.preventDefault();
    if (control.dataset.openQuiz) {
      openPopup({ kind: control.dataset.openQuiz, title: 'Узнайте, какой стиль вам подойдёт' }, true);
    } else {
      openPopup(forms[control.dataset.openForm] || forms.repair);
    }
  });
  // Imported headers have a runtime host; the host must own sticky positioning.
  // Galleries in the UI kit deliberately show several independent header states.
  const headerObserver = new MutationObserver(() => {
    const sitePages=['Главная','Дизайн интерьера','Комплектация','Приёмка квартир','Партнёрам','Пиллар услуги','Категория услуги','Услуги','Портфолио и отзывы','О компании и контакты','Блог','Служебные страницы','404'];
    if(!sitePages.includes(window.__dcRootName?.()))return;
    const headers=document.querySelectorAll('.espada-demo-header');
    if(headers.length!==1)return;
    const host=headers[0].parentElement;
    if(host?.classList.contains('sc-host') && host.nextElementSibling)host.classList.add('espada-header-host');
  });
  headerObserver.observe(document.body,{childList:true,subtree:true});
})();
