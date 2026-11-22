#!/usr/bin/env python3
"""Local static preview with a same-origin, fixed-path order persistence API."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import re
import subprocess
import sys
import threading
from urllib.parse import urlsplit
from article_order import ROOT, ORDER_FILE, load_orders, save_orders

LOCK=threading.Lock()

def rebuild_site():
    subprocess.run([sys.executable, str(ROOT / 'scripts/build_blog.py')],
                   cwd=ROOT, check=True, timeout=120)


class PreviewHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        """Serve local MP4s with byte ranges so browser seeking works."""
        self._media_remaining = None
        path = self.translate_path(self.path)
        if not urlsplit(self.path).path.lower().endswith('.mp4') or not os.path.isfile(path):
            return super().send_head()
        try:
            source = open(path, 'rb')
        except OSError:
            self.send_error(404, 'File not found')
            return None
        try:
            stat = os.fstat(source.fileno())
            size = stat.st_size
            start, end, status = 0, size - 1, 200
            value = self.headers.get('Range', '')
            # An unvalidated If-Range condition must fall back to the full file.
            match = re.fullmatch(r'bytes=(\d*)-(\d*)', value) if not self.headers.get('If-Range') else None
            if match and any(match.groups()):
                first, last = match.groups()
                if first:
                    start = int(first)
                    end = min(int(last), size - 1) if last else size - 1
                else:
                    start = max(0, size - int(last))
                if start >= size or end < start:
                    source.close()
                    self.send_response(416)
                    self.send_header('Content-Range', f'bytes */{size}')
                    self.send_header('Content-Length', '0')
                    self.end_headers()
                    return None
                status = 206
            self.send_response(status)
            self.send_header('Content-Type', 'video/mp4')
            self.send_header('Accept-Ranges', 'bytes')
            self.send_header('Content-Length', str(end - start + 1))
            self.send_header('Last-Modified', self.date_time_string(stat.st_mtime))
            if status == 206:
                self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
            self.end_headers()
            source.seek(start)
            self._media_remaining = end - start + 1
            return source
        except Exception:
            source.close()
            raise

    def copyfile(self, source, outputfile):
        remaining = self._media_remaining
        if remaining is None:
            return super().copyfile(source, outputfile)
        try:
            while remaining > 0:
                data = source.read(min(65536, remaining))
                if not data:
                    break
                outputfile.write(data)
                remaining -= len(data)
        except (BrokenPipeError, ConnectionResetError):
            pass  # Browsers may cancel a range when playback pauses or seeks.

    def json_reply(self, code, data):
        payload=json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.send_header('Content-Length',str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if urlsplit(self.path).path=='/__cxwiki/orders':
            try:
                with LOCK:orders=load_orders()
                self.json_reply(200, orders)
            except (ValueError,OSError) as error:self.json_reply(500, {'error':str(error)})
            return
        with LOCK:
            super().do_GET()

    def do_HEAD(self):
        with LOCK:
            super().do_HEAD()

    def do_POST(self):
        if self.path!='/__cxwiki/orders':
            self.json_reply(404, {'error':'未知接口'})
            return
        # JSON cross-origin writes are forbidden; no CORS permission is sent.
        host=self.headers.get('Host','')
        if urlsplit('http://'+host).hostname not in ('127.0.0.1','localhost') or self.headers.get('Origin')!='http://'+host:
            self.json_reply(403, {'error':'仅允许本地预览页面保存排序'})
            return
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=1024*1024:
                raise ValueError('排序请求大小无效')
            patch=json.loads(self.rfile.read(length).decode('utf-8'))
            with LOCK:
                save_orders(ORDER_FILE, patch)
                try:
                    rebuild_site()
                except (subprocess.SubprocessError, OSError) as error:
                    self.log_error('排序已保存，但重新生成网页失败：%s', error)
                    self.json_reply(200, {'saved':True, 'published':False,
                                         'error':'排序已保存，但网页生成失败，请查看运行终端。'})
                    return
            self.json_reply(200, {'saved':True, 'published':True})
        except (ValueError, UnicodeError) as error:self.json_reply(400, {'error':str(error)})
        except OSError as error:self.json_reply(500, {'error':str(error)})

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--port',type=int,default=8000)
    args=parser.parse_args()
    handler=partial(PreviewHandler,directory=str(ROOT/'site'))
    with ThreadingHTTPServer(('127.0.0.1',args.port),handler) as server:
        print(f'预览：http://127.0.0.1:{args.port}/；拖动顺序自动写入仓库，Ctrl+C 停止。',flush=True)
        try:server.serve_forever()
        except KeyboardInterrupt:pass
