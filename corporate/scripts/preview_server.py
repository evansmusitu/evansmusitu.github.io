#!/usr/bin/env python3
"""Loopback-only local QA server; never a public hosting configuration."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from functools import partial
import argparse
from build import META_CSP

ROOT=Path(__file__).resolve().parents[1]/'dist'
class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        import urllib.parse
        path=urllib.parse.urlsplit(self.path).path
        if path=='/404/' or not (ROOT/path.lstrip('/')).exists() and not path.startswith('/assets/'):
            raw=(ROOT/'404/index.html').read_bytes()
            self.send_response(404)
            self.send_header('Content-Type','text/html; charset=utf-8')
            self.send_header('Content-Length',str(len(raw)))
            self.end_headers();self.wfile.write(raw)
        else:
            super().do_GET()
    def end_headers(self):
        self.send_header('X-Robots-Tag','noindex, nofollow')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','strict-origin-when-cross-origin')
        self.send_header('Content-Security-Policy',META_CSP+'; frame-ancestors \'none\'')
        self.send_header('Cache-Control','no-store')
        super().end_headers()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8000);args=parser.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',args.port),partial(Handler,directory=str(ROOT)))
    print(f'REVIEW ONLY http://127.0.0.1:{args.port}/ (loopback, noindex, no publishing)',flush=True)
    server.serve_forever()
