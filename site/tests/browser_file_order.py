"""Direct file:// ranking must persist through navigation and explicit JSON save."""
import json
from pathlib import Path
import tempfile
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

def main():
    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as pw:
        root = Path(tmp)
        (root/'blog.js').write_text((ROOT/'scripts/blog.js').read_text())
        html = '<meta charset="utf-8"><style>.article-list-item{height:60px}</style><section class="listing-section"><div class="article-list" data-order-key="test" data-order-revision="v1">'
        html += ''.join(f'<div class="article-list-item" data-article-id="{i}"><button class="drag-handle">drag</button>{i}</div>' for i in 'abc')
        html += '</div></section><script src="blog.js"></script>'
        for name in ('one.html','two.html'):
            (root/name).write_text(html)
        browser=pw.chromium.launch(headless=True)
        page=browser.new_page()
        page.add_init_script("""window.showOpenFilePicker = async () => [{
          name: 'article-order.json',
          getFile: async () => ({text: async () => '{"test":{"a":30,"b":20,"c":10},"other":{"x":1}}'}),
          createWritable: async () => ({write: async (s) => {window.written=JSON.parse(s)}, close: async () => {}})
        }];""")
        page.goto((root/'one.html').as_uri())
        page.wait_for_selector('.order-toolbar', state='attached')
        handle=page.locator('[data-article-id="c"] button').bounding_box()
        target=page.locator('[data-article-id="a"]').bounding_box()
        page.mouse.move(handle['x']+5,handle['y']+5)
        page.mouse.down()
        page.mouse.move(target['x']+5,target['y']+5,steps=5)
        page.mouse.up()
        assert page.locator('.article-list-item').first.get_attribute('data-article-id')=='c'
        page.goto((root/'two.html').as_uri())
        page.wait_for_selector('.order-toolbar', state='attached')
        assert page.locator('.article-list-item').first.get_attribute('data-article-id')=='c', 'Order lost after navigation'
        page.get_by_role('button',name='保存到排序文件').click()
        page.wait_for_function('window.written !== undefined')
        saved=page.evaluate('window.written')
        assert saved['test']['c']>30 and saved['test']['a']==30 and saved['test']['b']==20
        assert saved['other']=={'x':1}
        page.reload()
        page.wait_for_selector('.order-toolbar', state='attached')
        assert page.locator('.article-list-item').first.get_attribute('data-article-id')=='c'
        for origin in ('http://localhost:8765', 'https://wiki.example.test', 'http://wiki.example.test'):
            web=browser.new_page(accept_downloads=True)
            def route(req):
                if req.request.url.endswith('/blog.js'):
                    req.fulfill(body=(ROOT/'scripts/blog.js').read_text(), content_type='application/javascript; charset=utf-8')
                elif req.request.url.endswith('/__cxwiki/orders'):
                    req.fulfill(status=404)
                else:
                    req.fulfill(body=html, content_type='text/html; charset=utf-8')
            web.route(origin+'/**',route)
            web.goto(origin+'/one.html')
            web.wait_for_selector('.order-toolbar',state='attached')
            handle=web.locator('[data-article-id="c"] button').bounding_box()
            target=web.locator('[data-article-id="a"]').bounding_box()
            web.mouse.move(handle['x']+5,handle['y']+5)
            web.mouse.down()
            web.mouse.move(target['x']+5,target['y']+5,steps=5)
            web.mouse.up()
            web.goto(origin+'/two.html')
            web.wait_for_selector('.order-toolbar',state='attached')
            assert web.locator('.article-list-item').first.get_attribute('data-article-id')=='c', origin
            web.reload()
            web.wait_for_selector('.order-toolbar',state='attached')
            assert web.locator('.article-list-item').first.get_attribute('data-article-id')=='c', origin
            if origin.startswith('http://wiki.example'):
                with web.expect_download() as download:
                    web.get_by_role('button',name='保存到排序文件').click()
                assert json.loads(Path(download.value.path()).read_text()) == {'test':['c','a','b']}
            web.close()
        browser.close()
        print('PASS: file, local static HTTP, remote HTTPS/HTTP drag, navigation, reload, source save and patch export')

if __name__=='__main__':
    main()
