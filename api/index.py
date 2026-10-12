import os
import sys

# 프로젝트 루트 디렉터리를 sys.path에 추가하여 app 모듈을 가져올 수 있도록 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app

# WSGI 미들웨어: Vercel rewrite로 전달된 prefix(/api/index 등) 보정
class VercelPathMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')
        for prefix in ['/api/index.py', '/api/index']:
            if path.startswith(prefix):
                new_path = path[len(prefix):]
                environ['PATH_INFO'] = new_path if new_path else '/'
                break
        return self.wsgi_app(environ, start_response)

# WSGI 앱 래핑
app.wsgi_app = VercelPathMiddleware(app.wsgi_app)
