(() => {
  document.querySelectorAll('[data-tex]').forEach((element) => {
    if (!window.katex) return;
    try {
      window.katex.render(element.dataset.tex, element, {
        displayMode: element.classList.contains('math-block'),
        throwOnError: false,
        trust: false,
      });
    } catch (error) {
      element.dataset.mathError = String(error);
    }
  });
  const headings = [...document.querySelectorAll('.prose h2, .prose h3')];
  const tocLinks = [...document.querySelectorAll('.toc a')];
  if (!headings.length || !tocLinks.length || !('IntersectionObserver' in window)) return;
  const byId = new Map(tocLinks.map((link) => [link.getAttribute('href').slice(1), link]));
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      const link = byId.get(entry.target.id);
      if (link && entry.isIntersecting) {
        tocLinks.forEach((item) => item.classList.remove('current'));
        link.classList.add('current');
      }
    });
  }, { rootMargin: '-90px 0px -65% 0px' });
  headings.forEach((heading) => observer.observe(heading));
})();

(() => {
  const lists = [...document.querySelectorAll('.article-list[data-order-key]')];
  if (!lists.length) return;
  const prefix = 'cxwiki-order:';
  const read = (key) => {
    try { return JSON.parse(localStorage.getItem(prefix + key) || 'null'); }
    catch { return null; }
  };
  const idsFor = (list) => [...list.querySelectorAll(':scope > .article-list-item')]
    .map((item) => item.dataset.articleId);
  const toolbar = document.createElement('div');
  toolbar.className = 'order-toolbar';
  const status = document.createElement('span');
  status.setAttribute('role', 'status');
  status.textContent = '';
  toolbar.append(status);
  const section = lists[0].closest('.listing-section') || lists[0].parentElement;
  section.prepend(toolbar);
  let queue = Promise.resolve();
  const persist = (patch) => {
    queue = queue.then(async () => {
      status.textContent = '正在固定排序…';
      try {
        if (!['http:', 'https:'].includes(location.protocol)) throw new Error('static');
        const response = await fetch('/__cxwiki/orders', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(patch),
        });
        const result = await response.json();
        if (!response.ok || result.saved !== true) throw new Error(result.error || 'static');
        status.textContent = result.published === false ? result.error : '顺序已固定';
      } catch {
        status.textContent = '无法固定：请用 bash build.sh --serve 打开的页面调整顺序。';
      }
    });
    return queue;
  };
  lists.forEach((list) => {
    const revision = list.dataset.orderRevision || 'default';
    const key = list.dataset.orderKey;
    const items = () => [...list.querySelectorAll(':scope > .article-list-item')];
    const save = () => {
      const ids = idsFor(list);
      try { localStorage.setItem(prefix + key, JSON.stringify({revision, ids})); }
      catch { /* The repository API can still save when browser storage is unavailable. */ }
      persist({[key]: ids});
    };
    const stored = read(key);
    // Old browser arrays are imported only before a shared order exists.
    const saved = Array.isArray(stored) ? (revision === 'default' ? stored : []) :
      (stored?.revision === revision && Array.isArray(stored.ids) ? stored.ids : []);
    if (saved.length) {
      const original = items();
      const byId = new Map(original.map((item) => [item.dataset.articleId, item]));
      const included = new Set();
      saved.forEach((id) => {
        if (byId.has(id) && !included.has(id)) {
          list.appendChild(byId.get(id)); included.add(id);
        }
      });
      original.forEach((item) => {
        if (!included.has(item.dataset.articleId)) list.appendChild(item);
      });
      if (revision === 'default' && ['http:', 'https:'].includes(location.protocol))
        persist({[key]: idsFor(list)});
    }
    let dragged = null;
    list.addEventListener('pointerdown', (event) => {
      const handle = event.target.closest('.drag-handle');
      if (!handle || event.button !== 0) return;
      event.preventDefault();
      dragged = handle.closest('.article-list-item');
      dragged.classList.add('is-dragging');
      list.setPointerCapture(event.pointerId);
    });
    list.addEventListener('pointermove', (event) => {
      if (!dragged) return;
      const target = items().find((item) => {
        const box = item.getBoundingClientRect();
        return item !== dragged && event.clientY >= box.top && event.clientY <= box.bottom;
      });
      if (!target) return;
      const box = target.getBoundingClientRect();
      list.insertBefore(dragged, event.clientY < box.top + box.height / 2 ? target : target.nextSibling);
    });
    const finish = () => {
      if (!dragged) return;
      dragged.classList.remove('is-dragging');
      dragged = null;
      save();
    };
    list.addEventListener('pointerup', finish);
    list.addEventListener('pointercancel', finish);
    list.addEventListener('lostpointercapture', finish);
    list.addEventListener('dragstart', (event) => event.preventDefault());
  });
})();
