import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import article_order

class OrderTest(unittest.TestCase):
    def test_saved_order_keeps_new_articles_and_ignores_removed_ids(self):
        self.assertEqual(article_order.apply_order(['a','b','c'], ['removed','b','a']), ['b','a','c'])
    def test_rejects_invalid_or_duplicate_order(self):
        for value in [[], {'key':'text'}, {'key':['a','a']}, {'key':[1]}]:
            with self.assertRaises(ValueError): article_order.validate_orders(value)
    def test_merge_persists_other_columns_and_roundtrips(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'order.json'
            article_order.save_orders(path, {'concepts':['a','b']})
            article_order.save_orders(path, {'reviews':['c']})
            self.assertEqual(article_order.load_orders(path), {'concepts':['a','b'],'reviews':['c']})
            self.assertEqual(json.loads(path.read_text())['concepts'], ['a','b'])


class PreviewApiTest(unittest.TestCase):
    def test_same_origin_save_and_reject_invalid_requests(self):
        import functools
        import threading
        from http.server import ThreadingHTTPServer
        from unittest.mock import patch
        import urllib.request
        import urllib.error
        import preview_blog
        with tempfile.TemporaryDirectory() as tmp:
            order=Path(tmp)/'order.json'
            handler=functools.partial(preview_blog.PreviewHandler, directory=tmp)
            with patch.object(preview_blog,'ORDER_FILE',order), patch.object(preview_blog,'load_orders',lambda:article_order.load_orders(order)), patch.object(preview_blog,'rebuild_site') as rebuild:
                server=ThreadingHTTPServer(('127.0.0.1',0),handler)
                thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
                base=f'http://127.0.0.1:{server.server_port}'
                try:
                    request=urllib.request.Request(base+'/__cxwiki/orders', data=b'{"test":["b","a"]}',headers={'Origin':base,'Content-Type':'application/json'})
                    with urllib.request.urlopen(request) as response:
                        self.assertEqual(response.status,200)
                        self.assertTrue(json.load(response)['published'])
                    rebuild.assert_called_once()
                    self.assertEqual(article_order.load_orders(order),{'test':['b','a']})
                    for origin,payload,code in [('https://example.com',b'{}',403),(base,b'{"test":["a","a"]}',400)]:
                        request=urllib.request.Request(base+'/__cxwiki/orders',data=payload,headers={'Origin':origin,'Content-Type':'application/json'})
                        with self.assertRaises(urllib.error.HTTPError) as caught:urllib.request.urlopen(request)
                        self.assertEqual(caught.exception.code,code)
                    self.assertEqual(article_order.load_orders(order),{'test':['b','a']})
                finally:server.shutdown();server.server_close();thread.join()

if __name__ == "__main__":
    unittest.main()
