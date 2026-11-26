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
  // Static pages already contain the saved order; local preview reads the source directly.
  const orderUrl = '/__cxwiki/orders';
  let serverMode = false;
  const draftKey = 'cxwiki-order:' + document.currentScript.src;
  let drafts = {};
  try { drafts = JSON.parse(localStorage.getItem(draftKey) || '{}'); } catch { /* storage unavailable */ }
  const storeDrafts = () => localStorage.setItem(draftKey, JSON.stringify(drafts));
  const ranksFor = (ids, previous) => {
    const ranks = Array.isArray(previous)
      ? Object.fromEntries(previous.map((id, i) => [id, (previous.length-i)*1024]))
      : {...previous};
    let top = Math.max(0, ...Object.values(ranks));
    [...ids].reverse().filter(id => !(id in ranks)).forEach(id => { top += 1024; ranks[id] = top; });
    const current = [...ids].sort((a,b) => ranks[b]-ranks[a]);
    if (current.every((id,i) => id === ids[i])) return ranks;
    for (const moved of ids) {
      if (current.filter(id => id !== moved).join() !== ids.filter(id => id !== moved).join()) continue;
      const i = ids.indexOf(moved);
      const high = i ? ranks[ids[i-1]] : null;
      const low = i+1 < ids.length ? ranks[ids[i+1]] : null;
      const n = high === null ? low+1024 : low === null ? high-1024 : (high+low)/2;
      if (Number.isFinite(n) && (high === null || n < high) && (low === null || n > low)
          && !Object.entries(ranks).some(([id, value]) => id !== moved && value === n)) {
        ranks[moved] = n;
        return ranks;
      }
    }
    // Bulk reordering: retain only rankings of the currently displayed articles.
    return Object.fromEntries(ids.map((id,i) => [id,(ids.length-i)*1024]));
  };
  let orders = {};
  try {
    if (location.protocol !== 'http:' || !['localhost', '127.0.0.1'].includes(location.hostname)) throw new Error('static');
    const response = await fetch(orderUrl, {cache: 'no-store'});
    if (!response.ok) throw new Error('排序文件读取失败');
    orders = await response.json();
    serverMode = true;
  } catch { /* Static reading falls back to the order embedded during build. */ }
  const idsFor = (list) => [...list.querySelectorAll(':scope > .article-list-item')]
    .map((item) => item.dataset.articleId);
  const toolbar = document.createElement('div');
  toolbar.className = 'order-toolbar';
  const status = document.createElement('span');
  status.setAttribute('role', 'status');
  status.textContent = '';
  toolbar.append(status);
  const button = document.createElement('button');
  {
    button.type = 'button';
    button.textContent = '保存到排序文件';
    toolbar.append(button);
    button.hidden = serverMode && !Object.values(drafts).some(d => d.pending);
    const updateStatus = () => {
      status.textContent = Object.values(drafts).some(d => d.pending)
        ? '顺序已在本浏览器保留，尚未写入排序文件。'
        : '拖动顺序会自动保存在本浏览器，也可写入 site/article-order.json。';
    };
    // A newer generated revision supersedes saved drafts; unsaved edits are retained.
    lists.forEach(list => {
      const key = list.dataset.orderKey;
      if (drafts[key] && !drafts[key].pending && drafts[key].revision !== list.dataset.orderRevision) delete drafts[key];
    });
    try { storeDrafts(); } catch { /* storage unavailable */ }
    if (!serverMode || !button.hidden) updateStatus();
    button.addEventListener('click', async () => {
      if (!Object.values(drafts).some(d => d.pending)) {
        status.textContent = '没有待保存的排序修改。';
        return;
      }
      if (!window.showOpenFilePicker) {
        // Non-secure HTTP or browsers without the file picker can export a patch.
        const patch = Object.fromEntries(Object.entries(drafts).filter(([,d]) => d.pending).map(([key,d]) => [key,d.ids]));
        const url = URL.createObjectURL(new Blob([JSON.stringify(patch,null,2)+'\n'], {type:'application/json'}));
        const link = document.createElement('a');
        link.href = url;
        link.download = 'article-order-changes.json';
        link.click();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
        status.textContent = '已导出排序修改；可用 site/scripts/article_order.py 合并到唯一排序源文件。';
        return;
      }
      try {
        const [handle] = await window.showOpenFilePicker({
          types: [{description: '排序 JSON', accept: {'application/json': ['.json']}}]
        });
        if (handle.name !== 'article-order.json') throw new Error('请选择 site/article-order.json');
        const source = JSON.parse(await (await handle.getFile()).text());
        if (!source || typeof source !== 'object' || Array.isArray(source)) throw new Error('排序文件格式无效');
        const pending = Object.entries(drafts).filter(([,d]) => d.pending);
        for (const [key, draft] of pending) source[key] = ranksFor(draft.ids, source[key] || {});
        const writer = await handle.createWritable();
        await writer.write(JSON.stringify(source, null, 2) + '\n');
        await writer.close();
        for (const [,draft] of pending) draft.pending = false;
        try { storeDrafts(); } catch { /* source already saved */ }
        status.textContent = '已保存到 site/article-order.json；下次构建会使用新顺序。';
      } catch (error) {
        status.textContent = '未写入排序文件，浏览器内顺序仍保留：' + error.message;
      }
    });
  }
  const section = lists[0].closest('.listing-section') || lists[0].parentElement;
  section.prepend(toolbar);
  let queue = Promise.resolve();
  const persist = (patch, draft) => {
    queue = queue.then(async () => {
      status.textContent = '正在固定排序…';
      try {
        if (!['http:', 'https:'].includes(location.protocol)) throw new Error('static');
        const response = await fetch('/__cxwiki/orders', {
          method: 'POST',
          keepalive: true,
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(patch),
        });
        const result = await response.json();
        if (!response.ok || result.saved !== true) throw new Error(result.error || 'static');
        const key = Object.keys(patch)[0];
        if (drafts[key] === draft) {
          draft.pending = false;
          try { storeDrafts(); } catch { /* source already saved */ }
        }
        button.hidden = !Object.values(drafts).some(d => d.pending);
        status.textContent = result.published === false ? result.error : '已保存到 site/article-order.json';
      } catch {
        button.hidden = false;
        status.textContent = '自动写入失败；顺序已在本浏览器保留，可点击保存到排序文件。';
      }
    });
    return queue;
  };
  // A page restored from the back-forward cache must read the latest order.
  window.addEventListener('pageshow', event => { if (event.persisted) location.reload(); });
  lists.forEach((list) => {
    const key = list.dataset.orderKey;
    const items = () => [...list.querySelectorAll(':scope > .article-list-item')];
    const save = () => {
      const draft = {ids: idsFor(list), revision: list.dataset.orderRevision, pending: true};
      drafts[key] = draft;
      try {
        storeDrafts();
        status.textContent = '顺序已在本浏览器保留；点击“保存到排序文件”永久保存。';
      } catch {
        status.textContent = '浏览器存储不可用，请在离开前点击“保存到排序文件”。';
      }
      if (serverMode) return persist({[key]: draft.ids}, draft);
    };
    const ranks = drafts[key] && (!serverMode || drafts[key].pending) ? drafts[key].ids : orders[key] || {};
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
