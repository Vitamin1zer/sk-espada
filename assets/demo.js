/* Общие попапы макетов. Сетевые запросы с контактами здесь не выполняются. */
(() => {
  'use strict';
  const forms = {
    repair: { kind: 'Попап', title: 'Получите индивидуальный расчёт сметы', cta: 'Бесплатный расчёт сметы' },
    design: { kind: 'Дизайн', title: 'Рассчитать стоимость дизайна', cta: 'Рассчитать стоимость дизайна' },
    acceptance: { kind: 'Приёмка', title: 'Заказать приёмку квартиры', cta: 'Вызвать приёмщика' },
    showroom: { kind: 'Шоурум', title: 'Посетить шоурум', cta: 'Записаться в шоурум' },
    partner: { kind: 'Партнёрство', title: 'Стать партнёром Эспады', cta: 'Стать партнёром' },
  };
  function openPopup(config, quiz = false) {
    if (window.parent !== window && window.parent.__espadaOpenPopup) {
      window.parent.__espadaOpenPopup(config, quiz);
      return;
    }
    let dialog = document.querySelector('dialog.espada-dialog');
    if (dialog) dialog.remove();
    dialog = document.createElement('dialog');
    dialog.className = 'espada-dialog';
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
        if (!win.__dcSetProps || !win.__dcRootName) return;
        if (!configured) {
          win.__dcSetProps(win.__dcRootName(), config);
          configured = true;
        }
        const root = frame.contentDocument.querySelector('[data-dc-root]') || frame.contentDocument.body.firstElementChild;
        if (root) frame.style.height = Math.max(460, root.scrollHeight) + 'px';
      }, 150);
    });
    dialog.addEventListener('close', () => { clearInterval(timer); dialog.remove(); }, { once: true });
    dialog.addEventListener('click', e => { if (e.target === dialog) dialog.close(); });
    dialog.showModal();
    close.focus();
  }
  window.__espadaOpenPopup = openPopup;
  const mobileViewport = matchMedia('(max-width:700px)');
  function responsiveProps() {
    if (!window.__dcSetProps || !window.__dcRootName || !document.getElementById('dc-root')) return false;
    const page = new URLSearchParams(location.search).get('page');
    window.__dcSetProps(window.__dcRootName(), Object.assign({ mobile: mobileViewport.matches }, page ? { page } : {}));
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
        window.parent.__espadaNavigate(href);
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
})();
