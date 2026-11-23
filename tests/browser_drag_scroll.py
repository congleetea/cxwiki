"""Run with a Python environment containing Playwright: python3 tests/browser_drag_scroll.py."""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    saved = []
    html = '''<style>body{margin:0}.article-list-item{height:70px;display:flex}
    .drag-handle{width:35px;touch-action:none}</style>
    <section class="listing-section"><div class="article-list" data-order-key="test">'''
    html += ''.join(f'<div class="article-list-item" data-article-id="a{i}"><button class="drag-handle">drag</button><span>Article {i}</span></div>' for i in range(70))
    html += '</div></section><script src="/assets/blog.js"></script>'
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width':900, 'height':600})
        def route(request):
            path = request.request.url
            if path.endswith('/assets/blog.js'):
                request.fulfill(body=(ROOT/'scripts/blog.js').read_text(), content_type='text/javascript')
            elif path.endswith('/article-order.json'):
                request.fulfill(body='{}', content_type='application/json')
            elif path.endswith('/__cxwiki/orders'):
                saved.append(request.request.post_data_json)
                request.fulfill(body='{"saved":true,"published":true}', content_type='application/json')
            else:
                request.fulfill(body=html, content_type='text/html')
        page.route('http://cxwiki.test/**', route)
        page.goto('http://cxwiki.test/')
        page.wait_for_selector('.order-toolbar', state='attached')
        handle = page.locator('[data-article-id="a40"] .drag-handle')
        handle.scroll_into_view_if_needed()
        box = handle.bounding_box()
        initial_scroll = page.evaluate('scrollY')
        page.mouse.move(box['x']+10, box['y']+15)
        page.mouse.down()
        page.mouse.move(15, 8, steps=5)
        page.wait_for_timeout(650)
        assert page.evaluate('scrollY') < initial_scroll-100, 'Holding near top must scroll without additional pointer moves'
        page.mouse.up()
        page.wait_for_timeout(100)
        stopped = page.evaluate('scrollY')
        page.wait_for_timeout(200)
        assert page.evaluate('scrollY') == stopped, 'Scrolling must stop on release'
        assert len(saved) == 1 and saved[0]['test'].index('a40') < 39, 'Moved article must follow scrolling and save once'
        page.evaluate('scrollTo(0,0)')
        first = page.locator('.article-list-item').first.locator('.drag-handle').bounding_box()
        page.mouse.move(first['x']+10, first['y']+15)
        page.mouse.down()
        page.mouse.move(15, 592, steps=5)
        page.wait_for_timeout(650)
        assert page.evaluate('scrollY') > 100, 'Holding near bottom must scroll down'
        page.mouse.up()
        page.wait_for_timeout(100)
        assert len(saved) == 2, 'Each drag must save exactly once'
        browser.close()
        print('PASS: upward/downward edge scrolling, stationary pointer reordering, release stops scrolling, single save')


if __name__ == '__main__':
    main()
