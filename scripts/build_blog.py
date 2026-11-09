#!/usr/bin/env python3
"""Build the cxwiki Markdown source into a self-contained static HTML blog."""

from __future__ import annotations

import html
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

import mistune
import yaml


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
PI_ARTICLE_ORDER = [
    "pi-series-overview",
    "pi-0-flow-vla",
    "pi-fast-action-tokenization",
    "pi-05-open-world",
    "pi-knowledge-insulation",
    "pi-rtc-real-time-chunking",
    "pi-06-recap",
    "pi-human-to-robot",
    "pi-mem-memory",
    "pi-rlt-token",
    "pi-07-steerable",
]


@dataclass
class Page:
    source: Path
    output: Path
    meta: dict
    title: str
    kind: str
    series: str
    html: str = ""
    excerpt: str = ""
    headings: list[tuple[str, str, int]] | None = None


def parse_frontmatter(source: Path) -> tuple[dict, str]:
    text = source.read_text(encoding="utf-8")
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end >= 0:
            raw = text[4:end]
            body = text[end + 4 :].lstrip("\n")
            data = yaml.safe_load(raw) or {}
            if not isinstance(data, dict):
                data = {}
            return data, body
    return {}, text


def markdown_sources() -> list[Path]:
    # `_index.md` remains the authoring/check index; the reader-facing index
    # is the generated root and series pages.
    paths = [p for p in (ROOT / "wiki").rglob("*.md") if p.name != "_index.md"]
    paths.extend((ROOT / "raw" / "entries").rglob("*.md"))
    return sorted(paths)


def page_kind(path: Path, meta: dict) -> str:
    if meta.get("type") == "comprehensive" or "01-comprehensive" in path.parts:
        return "comprehensive"
    if "raw" in path.parts:
        return "source"
    return str(meta.get("type", "concept"))


def page_series(path: Path) -> str:
    if any(part == "01-embodied-ai" for part in path.parts) or "pi-series" in path.name:
        return "pi"
    if any(part == "02-classical-robotics" for part in path.parts) or "retargeting" in path.name or "FRAX" in path.name:
        return "robotics"
    if "raw" in path.parts:
        return "sources"
    return "other"


def output_path(source: Path) -> Path:
    return SITE / source.relative_to(ROOT).with_suffix(".html")


def split_target(target: str) -> tuple[str, str]:
    if "#" in target:
        path, anchor = target.split("#", 1)
        return path, "#" + anchor
    return target, ""


def mapped_target(source: Path, output: Path, target: str) -> str:
    target = target.strip()
    if not target or target.startswith(("#", "/", "http://", "https://", "mailto:", "data:")):
        return target
    path_part, anchor = split_target(target)
    if not path_part:
        return target
    resolved = (source.parent / path_part).resolve()
    if not resolved.exists():
        return target
    if resolved.is_dir():
        return target
    if resolved.suffix.lower() == ".md":
        destination = output_path(resolved)
    elif resolved.is_relative_to(ROOT):
        destination = SITE / resolved.relative_to(ROOT)
    else:
        return target
    return Path(os.path.relpath(destination, output.parent)).as_posix() + anchor


def rewrite_links(text: str, source: Path, output: Path) -> str:
    # Obsidian image embeds are accepted as a convenience for future pages.
    text = re.sub(
        r"!\[\[([^\]|]+)(?:\|([^\]]+))?\]\]",
        lambda m: f"![{m.group(2) or m.group(1)}]({m.group(1)})",
        text,
    )

    pattern = re.compile(r"(!?\[[^\]]*\]\()([^\s)]+)(\))")

    def replace(match: re.Match[str]) -> str:
        target = match.group(2)
        if not re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target):
            resolved = (source.parent / split_target(target)[0]).resolve()
            if resolved.is_relative_to(ROOT / "raw" / "codes") and not resolved.exists():
                # Optional local snapshots are not committed. Keep the label
                # without presenting a broken download in a fresh checkout.
                return match.group(1)[1:-2] + "（本地代码未下载）"
        return match.group(1) + mapped_target(source, output, match.group(2)) + match.group(3)

    return pattern.sub(replace, text)


def protect_code(text: str) -> tuple[str, list[str]]:
    blocks: list[str] = []

    def replacement(match: re.Match[str]) -> str:
        blocks.append(match.group(0))
        return f"<!--CXWIKI_CODE_{len(blocks) - 1}-->"

    return re.sub(r"```[\s\S]*?```", replacement, text), blocks


def restore_code(text: str, blocks: list[str]) -> str:
    for index, block in enumerate(blocks):
        text = text.replace(f"<!--CXWIKI_CODE_{index}-->", MARKDOWN(block))
    return text


def math_markup(text: str) -> str:
    # Keep equations readable without requiring a network-hosted math renderer.
    text = re.sub(
        r"\$\$\s*([\s\S]*?)\s*\$\$",
        lambda m: '<div class="math-block" data-tex="' + html.escape(m.group(1).strip(), quote=True) + '"><code>' + html.escape(m.group(1).strip()) + "</code></div>",
        text,
    )
    text = re.sub(
        r"(?<!\\)\$([^$\n]+?)\$",
        lambda m: '<span class="math-inline" data-tex="' + html.escape(m.group(1).strip(), quote=True) + '"><code>' + html.escape(m.group(1).strip()) + "</code></span>",
        text,
    )
    return text


def slugify(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value)
    value = html.unescape(value).strip().lower()
    value = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "section"


def add_heading_ids(rendered: str) -> tuple[str, list[tuple[str, str, int]]]:
    headings: list[tuple[str, str, int]] = []
    used: dict[str, int] = {}

    def replace(match: re.Match[str]) -> str:
        level = int(match.group(1))
        inner = match.group(2)
        plain = re.sub(r"<[^>]+>", "", inner)
        base = slugify(plain)
        count = used.get(base, 0)
        used[base] = count + 1
        ident = base if count == 0 else f"{base}-{count + 1}"
        if level in (2, 3):
            headings.append((ident, plain, level))
        return f'<h{level} id="{ident}">{inner}</h{level}>'

    rendered = re.sub(r"<h([1-6])>([\s\S]*?)</h\1>", replace, rendered)
    return rendered, headings


def excerpt_from(rendered: str) -> str:
    match = re.search(r"<p>([\s\S]*?)</p>", rendered)
    if not match:
        return ""
    text = re.sub(r"<[^>]+>", "", match.group(1))
    text = html.unescape(re.sub(r"\s+", " ", text)).strip()
    return text[:180] + ("…" if len(text) > 180 else "")


def make_markdown() -> mistune.Markdown:
    return mistune.create_markdown(
        escape=False,
        hard_wrap=False,
        plugins=["table", "strikethrough", "task_lists", "footnotes", "url"],
    )


MARKDOWN = make_markdown()


def render_content(source: Path, output: Path, body: str) -> tuple[str, list[tuple[str, str, int]]]:
    protected, blocks = protect_code(body)
    protected = rewrite_links(protected, source, output)
    protected = math_markup(protected)
    rendered = MARKDOWN(protected)
    rendered = restore_code(rendered, blocks)
    # The page shell renders the document title; keep the source H1 out of the
    # prose so readers see one clear title and the generated TOC starts at H2.
    rendered = re.sub(r"^<h1[^>]*>[\s\S]*?</h1>\s*", "", rendered, count=1)
    return add_heading_ids(rendered)


def tag_list(meta: dict) -> list[str]:
    tags = meta.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]
    return [str(tag) for tag in tags]


def rel_url(from_file: Path, to_file: Path) -> str:
    return Path(os.path.relpath(to_file, from_file.parent)).as_posix()


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def meta_date(page: Page) -> str:
    return str(
        page.meta.get("last_updated")
        or page.meta.get("created")
        or page.meta.get("date")
        or page.meta.get("retrieved")
        or ""
    )


def series_sort_key(page: Page) -> tuple[int, str, str]:
    stem = page.source.stem
    if page.series == "pi" and stem in PI_ARTICLE_ORDER:
        return (PI_ARTICLE_ORDER.index(stem), "", page.title)
    return (len(PI_ARTICLE_ORDER) + 1, meta_date(page), page.title)


def nav_path(page: Page, target: Path) -> str:
    return rel_url(page.output, target)


def header(page: Page, active: str = "") -> str:
    home = nav_path(page, SITE / "index.html")
    embodied = nav_path(page, SITE / "categories" / "01-embodied-ai" / "index.html")
    robotics = nav_path(page, SITE / "categories" / "02-classical-robotics" / "index.html")
    foundations = nav_path(page, SITE / "categories" / "03-ai-foundations" / "index.html")
    return f"""<header class=\"site-header\">
  <div class=\"header-inner\">
    <a class=\"brand\" href=\"{home}\"><span class=\"brand-mark\">π</span><span><strong>cxwiki</strong><small>研究与实现笔记</small></span></a>
    <nav aria-label=\"主导航\">
      <a class=\"{('active' if active == '01-embodied-ai' else '')}\" href=\"{embodied}\">具身智能</a>
      <a class=\"{('active' if active == '02-classical-robotics' else '')}\" href=\"{robotics}\">经典机器人</a>
      <a href=\"{foundations}\">人工智能基础</a>
      <a href=\"{home}#about\">关于</a>
    </nav>
  </div>
</header>"""


def footer(page: Page) -> str:
    return f"""<footer class=\"site-footer\"><div><strong>cxwiki</strong> · 研究、概念与综述的 HTML 阅读版</div><div>来源与证据仍保存在 <code>raw/</code>，页面由本地静态生成器构建。</div></footer>"""


def toc_html(page: Page) -> str:
    headings = page.headings or []
    if not headings:
        return ""
    items = []
    for ident, title, level in headings:
        items.append(f'<li class=\"toc-level-{level}\"><a href=\"#{esc(ident)}\">{esc(title)}</a></li>')
    return '<aside class="toc"><div class="eyebrow">本文目录</div><ol>' + "".join(items) + "</ol></aside>"


def source_links(page: Page) -> str:
    raw_link = page.meta.get("source") or page.meta.get("sources")
    if not raw_link:
        return ""
    values = raw_link if isinstance(raw_link, list) else [raw_link]
    links = []
    for value in values:
        value = str(value)
        target = mapped_target(page.source, page.output, value)
        links.append(f'<a href="{esc(target)}">{esc(Path(value).stem)}</a>')
    return '<section class="sources"><h2>来源与证据</h2><p>' + " · ".join(links) + "</p></section>"


def article_body(page: Page, pages: list[Page]) -> str:
    siblings = [p for p in pages if p.series == page.series and p.kind in ("concept", "tool", "comprehensive")]
    siblings.sort(key=lambda p: (p.kind != "comprehensive", series_sort_key(p)))
    current_index = next((i for i, p in enumerate(siblings) if p.source == page.source), None)
    previous = siblings[current_index - 1] if current_index is not None and current_index > 0 else None
    following = siblings[current_index + 1] if current_index is not None and current_index + 1 < len(siblings) else None
    tag_target = SITE / "series" / page.series / "index.html"
    if page.series in {"pi", "robotics"}:
        tags = "".join(f'<a class="tag" href="{nav_path(page, tag_target)}">{esc(tag)}</a>' for tag in tag_list(page.meta))
    else:
        tags = "".join(f'<span class="tag">{esc(tag)}</span>' for tag in tag_list(page.meta))
    date_value = meta_date(page)
    series_name = "π 系列" if page.series == "pi" else "经典机器人" if page.series == "robotics" else "来源"
    prev_next = '<div class="article-pager">'
    if previous:
        prev_next += f'<a class="pager prev" href="{nav_path(page, previous.output)}"><span>上一篇</span><strong>{esc(previous.title)}</strong></a>'
    else:
        prev_next += '<span></span>'
    if following:
        prev_next += f'<a class="pager next" href="{nav_path(page, following.output)}"><span>下一篇</span><strong>{esc(following.title)}</strong></a>'
    else:
        prev_next += '<span></span>'
    prev_next += "</div>"
    return f"""<!doctype html>
<html lang=\"zh-CN\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
<title>{esc(page.title)} · cxwiki</title><meta name=\"description\" content=\"{esc(page.excerpt)}\"><link rel=\"stylesheet\" href=\"{nav_path(page, SITE / 'assets/style.css')}\"><link rel=\"stylesheet\" href=\"{nav_path(page, SITE / 'assets/katex/katex.min.css')}\"><script defer src=\"{nav_path(page, SITE / 'assets/katex/katex.min.js')}\"></script><script defer src=\"{nav_path(page, SITE / 'assets/blog.js')}\"></script></head>
<body><a class=\"skip-link\" href=\"#content\">跳到正文</a>{header(page, 'comprehensive' if page.kind == 'comprehensive' else 'concepts')}
<main id=\"content\" class=\"article-shell\"><div class=\"article-layout\"><article class=\"article\">
  <div class=\"eyebrow\">{esc(series_name)} · {esc(page.kind)}</div><h1>{esc(page.title)}</h1>
  <div class=\"article-meta\"><time datetime=\"{esc(date_value)}\">更新于 {esc(date_value)}</time><span>·</span><span>{len(page.headings or [])} 个章节</span></div><div class=\"article-institution\">主体机构：{esc(page.meta.get("institution") or "未注明")}</div><div class=\"tags\">{tags}</div>
  <div class=\"prose\">{page.html}</div>{source_links(page)}{prev_next}
</article>{toc_html(page)}</div></main>{footer(page)}</body></html>"""


def card(page: Page, from_page: Path) -> str:
    kind = "综述" if page.kind == "comprehensive" else "概念" if page.kind == "concept" else "工具"
    organization = page.meta.get("institution") or ""
    organization_markup = f'<div class="card-institution">{esc(organization)}</div>' if organization else ""
    return f"""<a class=\"article-card\" href=\"{rel_url(from_page, page.output)}\"><div class=\"card-top\"><span class=\"card-kind\">{kind}</span><time>{esc(meta_date(page))}</time></div><h3>{esc(page.title)}</h3>{organization_markup}<p>{esc(page.excerpt)}</p><span class=\"read-more\">阅读文章 <span>→</span></span></a>"""


def ordered_card(page: Page, from_page: Path) -> str:
    identifier = str(page.meta.get("id") or page.source.stem)
    return f'<div class="article-list-item" draggable="true" data-article-id="{esc(identifier)}"><button class="drag-handle" type="button" aria-label="拖动调整顺序" title="拖动调整顺序">⠿</button>{card(page, from_page)}</div>'


def category_topic(page: Page, category: str) -> str:
    relative = page.source.relative_to(ROOT / "wiki" / category)
    return relative.parts[0] if len(relative.parts) > 1 else "根目录"


def category_title(category: str) -> tuple[str, str]:
    if category == "00-concepts":
        return "概念文章", "一个对象，一篇可以独立读懂的解释。"
    if category == "01-comprehensive":
        return "主题综述", "把不同对象放回同一张地图，比较关系、差异与发展脉络。"
    return category, "知识库分类"


def topic_label(topic: str) -> str:
    labels = {"01-embodied-ai": "具身智能", "02-classical-robotics": "经典机器人", "03-journal": "个人日记", "03-ai-foundations": "人工智能基础"}
    if topic in labels:
        return labels[topic]
    return re.sub(r"^\d+-", "", topic).replace("-", " ").replace("_", " ").title()


def extra_topics(pages: list[Page]) -> set[str]:
    reserved = {"00-concepts", "01-comprehensive", "imgs", "logs", "series"}
    topics = set()
    for page in pages:
        try:
            relative = page.source.relative_to(ROOT / "wiki")
        except ValueError:
            continue
        if relative.parts and relative.parts[0] not in reserved:
            topics.add(relative.parts[0])
    return topics


def extra_topic_page(topic: str, pages: list[Page], output: Path) -> str:
    relevant = []
    for page in pages:
        try:
            relative = page.source.relative_to(ROOT / "wiki")
        except ValueError:
            continue
        if relative.parts and relative.parts[0] == topic:
            relevant.append(page)
    relevant.sort(key=series_sort_key)
    page = Page(Path("/dev/null"), output, {}, topic_label(topic), "index", "")
    cards = "".join(ordered_card(p, output) for p in relevant)
    return f"""<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><title>{esc(topic_label(topic))} · cxwiki</title><link rel=\"stylesheet\" href=\"{rel_url(output, SITE / 'assets/style.css')}"><script defer src=\"{rel_url(output, SITE / 'assets/blog.js')}"></script></head><body><a class=\"skip-link\" href=\"#content\">跳到正文</a>{header(page)}<main id=\"content\" class=\"listing-shell\"><div class=\"listing-hero\"><div class=\"eyebrow\">个人知识库 · 主题目录</div><h1>{esc(topic_label(topic))}</h1><p>这个主题按文章目录直接浏览，后续可以继续拆分子目录。</p></div><section class=\"listing-section\"><div class=\"section-heading\"><div><h2>内容目录</h2><span class=\"order-hint\">拖动左侧手柄调整顺序，顺序会自动保存在当前浏览器</span></div><span>{len(relevant)} 篇</span></div><div class=\"card-grid article-list\" data-order-key=\"{esc(topic)}\">{cards}</div></section></main>{footer(page)}</body></html>"""


def topic_index(category: str, topic: str, pages: list[Page], output: Path) -> str:
    title, _ = category_title(category)
    relevant = [p for p in pages if p.source.is_relative_to(ROOT / "wiki" / category) and category_topic(p, category) == topic]
    relevant.sort(key=series_sort_key)
    page = Page(Path("/dev/null"), output, {}, topic, "index", "")
    cards = "".join(ordered_card(p, output) for p in relevant)
    return f"""<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><title>{esc(topic_label(topic))} · {esc(title)} · cxwiki</title><link rel=\"stylesheet\" href=\"{rel_url(output, SITE / 'assets/style.css')}"><script defer src=\"{rel_url(output, SITE / 'assets/blog.js')}"></script></head><body><a class=\"skip-link\" href=\"#content\">跳到正文</a>{header(page, topic)}<main id=\"content\" class=\"listing-shell\"><div class=\"listing-hero\"><div class=\"eyebrow\">{esc(title)} · 主题目录</div><h1>{esc(topic_label(topic))}</h1><p>从这里选择一篇文章进入阅读。目录页负责导航，文章页负责完整解释。</p></div><section class=\"listing-section\"><div class=\"section-heading\"><div><h2>文章</h2><span class=\"order-hint\">拖动左侧手柄调整顺序，顺序会自动保存在当前浏览器</span></div><span>{len(relevant)} 篇</span></div><div class=\"card-grid article-list\" data-order-key=\"{esc(category + '/' + topic)}\">{cards}</div></section></main>{footer(page)}</body></html>"""


def category_index(category: str, pages: list[Page], output: Path) -> str:
    title, subtitle = category_title(category)
    topics = sorted({category_topic(p, category) for p in pages if p.source.is_relative_to(ROOT / "wiki" / category)})
    page = Page(Path("/dev/null"), output, {}, title, "index", "")
    cards = []
    for topic in topics:
        topic_pages = [p for p in pages if p.source.is_relative_to(ROOT / "wiki" / category) and category_topic(p, category) == topic]
        target = SITE / "wiki" / category / topic / "index.html"
        cards.append(f'<a class="topic-card" href="{rel_url(output, target)}"><div class="topic-number">{len(cards) + 1:02d}</div><div><div class="eyebrow">主题目录</div><h2>{esc(topic_label(topic))}</h2><p>{len(topic_pages)} 篇文章，点击进入文章目录。</p><span class="read-more">打开目录 <span>→</span></span></div></a>')
    return f"""<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><title>{esc(title)} · cxwiki</title><link rel=\"stylesheet\" href=\"{rel_url(output, SITE / 'assets/style.css')}"><script defer src=\"{rel_url(output, SITE / 'assets/blog.js')}"></script></head><body><a class=\"skip-link\" href=\"#content\">跳到正文</a>{header(page, 'comprehensive' if category == '01-comprehensive' else 'concepts')}<main id=\"content\" class=\"listing-shell\"><div class=\"listing-hero\"><div class=\"eyebrow\">个人知识库 · 分类</div><h1>{esc(title)}</h1><p>{esc(subtitle)}</p></div><section class=\"listing-section\"><div class=\"section-heading\"><h2>主题目录</h2><span>{len(topics)} 个主题</span></div><div class=\"topic-grid\">{''.join(cards)}</div></section></main>{footer(page)}</body></html>"""


def series_page(series: str, pages: list[Page], output: Path) -> str:
    relevant = [p for p in pages if p.series == series and p.kind in ("concept", "tool", "comprehensive")]
    comprehensive = [p for p in relevant if p.kind == "comprehensive"]
    concepts = [p for p in relevant if p.kind != "comprehensive"]
    title = "π 系列" if series == "pi" else "经典机器人"
    subtitle = "连续动作、泛化、记忆与在线改进" if series == "pi" else "动作重定向、逆运动学与物理执行"
    page = Page(Path("/dev/null"), output, {}, title, "index", series)
    comp_cards = "".join(card(p, output) for p in comprehensive)
    concept_cards = "".join(card(p, output) for p in sorted(concepts, key=series_sort_key))
    concept_label = "概念文章" if all(p.kind == "concept" for p in concepts) else "概念与工具"
    return f"""<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><title>{esc(title)} · cxwiki</title><link rel=\"stylesheet\" href=\"{rel_url(output, SITE / 'assets/style.css')}\"><script defer src=\"{rel_url(output, SITE / 'assets/blog.js')}"></script></head><body><a class=\"skip-link\" href=\"#content\">跳到正文</a>{header(page, 'concepts')}<main id=\"content\" class=\"listing-shell\"><div class=\"listing-hero\"><div class=\"eyebrow\">研究系列</div><h1>{esc(title)}</h1><p>{esc(subtitle)}。综述负责建立关系和时间线，概念文章展开公式、流程、图示与实现边界。</p></div>{'<section class="listing-section"><div class="section-heading"><h2>先读综述</h2><span>关系、差异与发展脉络</span></div><div class="card-grid">' + comp_cards + '</div></section>' if comp_cards else ''}<section class=\"listing-section\"><div class=\"section-heading\"><h2>{concept_label}</h2><span>{len(concepts)} 篇</span></div><div class=\"card-grid\">{concept_cards}</div></section></main>{footer(page)}</body></html>"""


def home_page(pages: list[Page], output: Path) -> str:
    topics = sorted({category_topic(p, category) for category in ("00-concepts", "01-comprehensive") for p in pages if p.source.is_relative_to(ROOT / "wiki" / category)} | extra_topics(pages))
    page = Page(Path("/dev/null"), output, {}, "首页", "index", "")
    category_cards = []
    for topic in topics:
        topic_pages = [p for p in pages if any(p.source.is_relative_to(ROOT / "wiki" / category) and category_topic(p, category) == topic for category in ("00-concepts", "01-comprehensive")) or (topic in extra_topics(pages) and p.source.relative_to(ROOT / "wiki").parts[0] == topic)]
        target = SITE / "categories" / topic / "index.html"
        label = topic_label(topic)
        description = {"01-embodied-ai": "VLA、动作生成、记忆与机器人学习", "02-classical-robotics": "运动学、动作重定向与约束求解"}.get(topic, "按概念与综述继续浏览")
        category_cards.append(f'<a class="category-card" href="{rel_url(output, target)}"><span class="category-symbol">{len(category_cards) + 1:02d}</span><div><div class="eyebrow">知识主题</div><h2>{esc(label)}</h2><p>{esc(description)}</p><span class="read-more">查看概念与综述 <span>→</span></span></div></a>')
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>cxwiki · 个人知识库</title><meta name="description" content="按主题、概念与综述组织的个人知识库"><link rel="stylesheet" href="{rel_url(output, SITE / 'assets/style.css')}"><script defer src="{rel_url(output, SITE / 'assets/blog.js')}"></script></head><body><a class="skip-link" href="#content">跳到正文</a>{header(page)}<main id="content"><section class="library-hero"><div class="eyebrow">个人知识库 · cxwiki</div><h1>先按主题进入，<br><em>再选择概念或综述。</em></h1><p>这里同时容纳技术研究、人文阅读和个人记录。每个主题下面都分成概念文章与主题综述，文章本身放在更深一层的目录里。</p></section><section class="category-section"><div class="section-heading"><div><div class="eyebrow">主题分类</div><h2>选择一个知识主题</h2></div><span>{len(topics)} 个主题</span></div><div class="category-grid">{''.join(category_cards)}</div></section><section class="method-note" id="about"><div><div class="eyebrow">阅读方法</div><h2>概念讲清楚，综述讲关系。</h2></div><p>未来新增人文、日记、工作记录等目录时，只要放入对应主题目录，生成器会继续按“主题 → 概念/综述 → 文章目录”组织页面。</p></section></main>{footer(page)}</body></html>"""


def topic_category_page(topic: str, pages: list[Page], output: Path) -> str:
    label = topic_label(topic)
    page = Page(Path("/dev/null"), output, {}, label, "index", "")
    sections = []
    for category, heading, subtitle in (("00-concepts", "概念文章", "单个对象的公式、流程、图示与实现边界"), ("01-comprehensive", "主题综述", "对象之间的关系、差异、优缺点与发展脉络")):
        relevant = [p for p in pages if p.source.is_relative_to(ROOT / "wiki" / category) and category_topic(p, category) == topic]
        target = SITE / "wiki" / category / topic / "index.html"
        if relevant:
            href = rel_url(output, target)
            sections.append(f'<a class="door-card" href="{href}"><span class="door-symbol">{"概" if category == "00-concepts" else "综"}</span><div><div class="eyebrow">{heading}</div><h2>{heading}</h2><p>{subtitle}</p><span class="read-more">进入目录 · {len(relevant)} 篇 <span>→</span></span></div></a>')
        else:
            sections.append(f'<div class="door-card empty"><span class="door-symbol">—</span><div><div class="eyebrow">{heading}</div><h2>{heading}</h2><p>这个主题暂时没有已迁移的文章。</p></div></div>')
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(label)} · cxwiki</title><link rel="stylesheet" href="{rel_url(output, SITE / 'assets/style.css')}"><script defer src="{rel_url(output, SITE / 'assets/blog.js')}"></script></head><body><a class="skip-link" href="#content">跳到正文</a>{header(page)}<main id="content" class="listing-shell"><div class="listing-hero"><div class="eyebrow">主题入口</div><h1>{esc(label)}</h1><p>先选择文章层次，再进入对应的目录。</p></div><section class="listing-section"><div class="door-grid">{''.join(sections)}</div></section></main>{footer(page)}</body></html>"""

def copy_assets() -> None:
    assets = SITE / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "scripts" / "blog.js", assets / "blog.js") if (ROOT / "scripts" / "blog.js").exists() else None
    shutil.copytree(ROOT / "wiki" / "imgs", SITE / "wiki" / "imgs", dirs_exist_ok=True)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def redirect_page(title: str, target: str) -> str:
    return f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0; url={esc(target)}"><title>{esc(title)} · cxwiki</title></head><body><a href="{esc(target)}">打开 {esc(title)}</a></body></html>'


def build() -> list[Page]:
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir(parents=True)
    pages: list[Page] = []
    for source in markdown_sources():
        meta, body = parse_frontmatter(source)
        output = output_path(source)
        kind = page_kind(source, meta)
        series = page_series(source)
        title = str(meta.get("title") or source.stem)
        rendered, headings = render_content(source, output, body)
        page = Page(source, output, meta, title, kind, series, rendered, excerpt_from(rendered), headings)
        pages.append(page)
    pages.sort(key=lambda p: p.title)
    for page in pages:
        write_text(page.output, article_body(page, pages))

    # Theme files are checked into scripts so a build is reproducible from a clean site/.
    assets = SITE / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "scripts" / "blog.js", assets / "blog.js")
    shutil.copy2(ROOT / "scripts" / "blog.css", assets / "style.css")
    shutil.copytree(ROOT / "scripts" / "vendor" / "katex", assets / "katex", dirs_exist_ok=True)
    shutil.copytree(ROOT / "wiki" / "imgs", SITE / "wiki" / "imgs", dirs_exist_ok=True)
    # Code snapshots are linked from evidence pages; keep them available for
    # local browsing without converting source files into article pages.
    if (ROOT / "raw" / "codes").exists():
        shutil.copytree(ROOT / "raw" / "codes", SITE / "raw" / "codes", dirs_exist_ok=True)
    # Local PDFs travel with the standalone site; raw/papers remains the
    # editable source of truth and is refreshed on every build.
    shutil.copytree(ROOT / "raw" / "papers", SITE / "raw" / "papers",
                    dirs_exist_ok=True, ignore=shutil.ignore_patterns("*.txt"))

    write_text(SITE / "index.html", home_page(pages, SITE / "index.html"))
    # Keep a top-level, double-clickable entry point while also making site/
    # independently deployable.
    write_text(ROOT / "index.html", home_page(pages, ROOT / "index.html"))
    topics = sorted({category_topic(p, category) for category in ("00-concepts", "01-comprehensive") for p in pages if p.source.is_relative_to(ROOT / "wiki" / category)})
    for topic in topics:
        category_output = SITE / "categories" / topic / "index.html"
        if topic in extra_topics(pages):
            write_text(category_output, extra_topic_page(topic, pages, category_output))
        else:
            write_text(category_output, topic_category_page(topic, pages, category_output))
    for category in ("00-concepts", "01-comprehensive"):
        write_text(SITE / "wiki" / category / "index.html", category_index(category, pages, SITE / "wiki" / category / "index.html"))
        for topic in sorted({category_topic(p, category) for p in pages if p.source.is_relative_to(ROOT / "wiki" / category)}):
            write_text(SITE / "wiki" / category / topic / "index.html", topic_index(category, topic, pages, SITE / "wiki" / category / topic / "index.html"))
    write_text(SITE / "series/pi/index.html", series_page("pi", pages, SITE / "series/pi/index.html"))
    write_text(SITE / "series/robotics/index.html", series_page("robotics", pages, SITE / "series/robotics/index.html"))
    write_text(SITE / "wiki/index.html", redirect_page("cxwiki 首页", "../index.html"))
    write_text(SITE / "wiki/series/pi/index.html", redirect_page("π 系列", "../../../series/pi/index.html"))
    write_text(SITE / "wiki/series/robotics/index.html", redirect_page("机器人学系列", "../../../series/robotics/index.html"))
    write_text(ROOT / "wiki/index.html", redirect_page("cxwiki 首页", "../index.html"))
    write_text(ROOT / "wiki/series/pi/index.html", redirect_page("π 系列", "../../index.html#about"))
    write_text(ROOT / "wiki/series/robotics/index.html", redirect_page("机器人学系列", "../../index.html#about"))
    return pages


if __name__ == "__main__":
    built = build()
    print(f"built {len(built)} markdown pages into {SITE}")
