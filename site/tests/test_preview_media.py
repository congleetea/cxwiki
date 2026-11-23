"""Browser media seeking requires correct byte-range responses from local preview."""
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from preview_blog import PreviewHandler

class QuietHandler(PreviewHandler):
    def log_message(self,*args): pass

class MediaRangesTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.data=bytes(range(256))*4
        (Path(self.temp.name)/'demo.mp4').write_bytes(self.data)
        self.server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=self.temp.name))
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.url=f'http://127.0.0.1:{self.server.server_port}/demo.mp4'
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join();self.temp.cleanup()
    def request(self,range_value=None,method='GET'):
        return urllib.request.urlopen(urllib.request.Request(self.url,headers={'Range':range_value} if range_value else {},method=method))
    def test_bounded_open_and_suffix_ranges(self):
        for spec,start,end in [('bytes=100-199',100,199),('bytes=900-',900,1023),('bytes=-24',1000,1023),('bytes=1000-9999',1000,1023)]:
            with self.subTest(spec=spec),self.request(spec) as response:
                self.assertEqual(response.status,206)
                self.assertEqual(response.headers['Content-Range'],f'bytes {start}-{end}/1024')
                self.assertEqual(response.headers['Accept-Ranges'],'bytes')
                self.assertEqual(response.read(),self.data[start:end+1])
    def test_full_file_and_head(self):
        with self.request() as response:
            self.assertEqual(response.status,200);self.assertEqual(response.headers['Accept-Ranges'],'bytes');self.assertEqual(response.read(),self.data)
        with self.request('bytes=20-39','HEAD') as response:
            self.assertEqual(response.status,206);self.assertEqual(response.headers['Content-Length'],'20');self.assertEqual(response.read(),b'')
    def test_unsatisfiable_range(self):
        for spec in ['bytes=1024-','bytes=200-100','bytes=-0']:
            with self.subTest(spec=spec),self.assertRaises(urllib.error.HTTPError) as caught:self.request(spec)
            self.assertEqual(caught.exception.code,416)
            self.assertEqual(caught.exception.headers['Content-Range'],'bytes */1024')
    def test_malformed_or_multiple_ranges_fall_back_to_whole_file(self):
        for spec in ['bytes=abc','bytes=1-2,5-6']:
            with self.subTest(spec=spec),self.request(spec) as response:
                self.assertEqual(response.status,200);self.assertEqual(response.read(),self.data)

if __name__=='__main__':unittest.main()
