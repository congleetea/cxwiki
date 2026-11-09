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
  document.querySelectorAll('.article-list[data-order-key]').forEach((list) => {
    const storageKey = `cxwiki-order:${list.dataset.orderKey}`;
    const items = () => [...list.querySelectorAll(':scope > .article-list-item')];
    const save = () => localStorage.setItem(storageKey, JSON.stringify(items().map((item) => item.dataset.articleId)));
    const saved = JSON.parse(localStorage.getItem(storageKey) || '[]');
    if (Array.isArray(saved) && saved.length) {
      const byId = new Map(items().map((item) => [item.dataset.articleId, item]));
      saved.forEach((id) => byId.get(id) && list.appendChild(byId.get(id)));
      items().forEach((item) => { if (!saved.includes(item.dataset.articleId)) list.appendChild(item); });
    }
    let dragged = null;
    list.addEventListener('dragstart', (event) => {
      const handle = event.target.closest('.drag-handle');
      if (!handle) { event.preventDefault(); return; }
      dragged = handle.closest('.article-list-item');
      dragged.classList.add('is-dragging');
      event.dataTransfer.effectAllowed = 'move';
    });
    list.addEventListener('dragover', (event) => {
      if (!dragged) return;
      event.preventDefault();
      const target = event.target.closest('.article-list-item');
      if (!target || target === dragged) return;
      const box = target.getBoundingClientRect();
      list.insertBefore(dragged, event.clientY < box.top + box.height / 2 ? target : target.nextSibling);
    });
    list.addEventListener('dragend', () => {
      if (!dragged) return;
      dragged.classList.remove('is-dragging');
      dragged = null;
      save();
    });
  });
})();
