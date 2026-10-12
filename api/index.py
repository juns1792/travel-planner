import os
import sys

# 프로젝트 루트 디렉터리를 sys.path에 추가하여 app 모듈을 가져올 수 있도록 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app

# Vercel Serverless Function 진입점
# app 객체가 WSGI 애플리케이션으로 동작합니다.
