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

(async () => {
  const lists = [...document.querySelectorAll('.article-list[data-order-key]')];
  if (!lists.length) return;
  const script = document.currentScript;
  const orderUrl = new URL('../article-order.json', script.src);
  let orders = {};
  try {
    const response = await fetch(orderUrl, {cache: 'no-store'});
    if (!response.ok) throw new Error('排序文件读取失败');
    orders = await response.json();
  } catch { /* file:// reading falls back to the order embedded during build. */ }
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
        status.textContent = result.published === false ? result.error : '已保存到 site/article-order.json';
      } catch {
        status.textContent = '无法固定：请用 bash build.sh --serve 打开的页面调整顺序。';
      }
    });
    return queue;
  };
  lists.forEach((list) => {
    const key = list.dataset.orderKey;
    const items = () => [...list.querySelectorAll(':scope > .article-list-item')];
    const save = () => persist({[key]: idsFor(list)});
    const ranks = orders[key] || {};
    const saved = Array.isArray(ranks) ? ranks : Object.keys(ranks).sort((a, b) => ranks[b] - ranks[a]);
    if (saved.length) {
      const original = items();
      const byId = new Map(original.map((item) => [item.dataset.articleId, item]));
      const included = new Set();
      saved.forEach((id) => {
        if (byId.has(id) && !included.has(id)) {
          list.appendChild(byId.get(id)); included.add(id);
        }
      });
      // Unlisted articles remain before the saved articles.
    }
    let dragged = null;
    let pointerY = 0;
    let scrollFrame = null;
    let previousFrame = null;
    const reorder = () => {
      if (!dragged) return;
      const target = items().find((item) => {
        const box = item.getBoundingClientRect();
        return item !== dragged && pointerY >= box.top && pointerY <= box.bottom;
      });
      if (!target) return;
      const box = target.getBoundingClientRect();
      list.insertBefore(dragged, pointerY < box.top + box.height / 2 ? target : target.nextSibling);
    };
    const autoScroll = (timestamp) => {
      if (!dragged) return;
      const elapsed = previousFrame === null ? 1 / 60 : Math.min((timestamp - previousFrame) / 1000, 0.05);
      previousFrame = timestamp;
      const edge = Math.min(100, window.innerHeight / 4);
      // Ramp speed toward either edge, up to 900 pixels per second.
      const direction = pointerY < edge ? -Math.min(1, (edge - pointerY) / edge) :
        pointerY > window.innerHeight - edge ? Math.min(1, (pointerY - window.innerHeight + edge) / edge) : 0;
      if (direction) {
        window.scrollBy({top: direction * 900 * elapsed, behavior: 'instant'});
        // Scroll changes row positions even when the pointer is stationary.
        reorder();
      }
      scrollFrame = requestAnimationFrame(autoScroll);
    };
    list.addEventListener('pointerdown', (event) => {
      const handle = event.target.closest('.drag-handle');
      if (!handle || event.button !== 0 || dragged) return;
      event.preventDefault();
      pointerY = event.clientY;
      dragged = handle.closest('.article-list-item');
      dragged.classList.add('is-dragging');
      list.classList.add('is-sorting');
      list.setPointerCapture(event.pointerId);
      previousFrame = null;
      scrollFrame = requestAnimationFrame(autoScroll);
    });
    list.addEventListener('pointermove', (event) => {
      if (!dragged) return;
      pointerY = event.clientY;
      reorder();
    });
    const finish = () => {
      if (!dragged) return;
      cancelAnimationFrame(scrollFrame);
      scrollFrame = null;
      previousFrame = null;
      list.classList.remove('is-sorting');
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
