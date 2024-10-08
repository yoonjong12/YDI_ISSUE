import os
import sys
import time
from src import ui

if getattr(sys, 'frozen', False):
    current_path = os.path.dirname(os.path.dirname(sys.executable))
else:
    current_path = os.path.dirname(os.path.abspath(__file__))

def add_path(current_path, path):
    src_path = os.path.join(current_path, path)
    sys.path.append(src_path)

# 작업 디렉토리 변경
os.chdir(current_path)
print("현재 작업 디렉토리:", os.getcwd())

for path in ['src', 'config', 'data']:
    add_path(current_path, path)

# src.ui 모듈 import 및 실행
try:
    time.sleep(1)
    ui.main()
except Exception as e:
    print(f"실행 중 오류가 발생했습니다: {e}")