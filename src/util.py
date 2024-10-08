import os
import sys
from os.path import join
from pathlib import Path
import json
from tkinter import filedialog
from PIL import Image, ImageTk
def clear_frame(frame):
   for widgets in frame.winfo_children():
      widgets.destroy()

def open_img(path):
    return ImageTk.PhotoImage(Image.open(path).resize((800, 600)))

def browse(output, path):
    directory = filedialog.askdirectory(initialdir=path)
    output.config(text=directory)

def browse_file(output, path):
    path = filedialog.askopenfilename(initialdir=path)
    output.config(text=path)

def get_download_folder():
    home = Path.home()  # 사용자의 홈 디렉토리 경로를 얻음
    if os.name == 'nt':  # Windows 시스템인 경우
        download_folder = home / 'Downloads'
    else:  # Mac 또는 Linux 시스템인 경우
        download_folder = home / 'Downloads'
    
    return download_folder

def make_path():
    if getattr(sys, 'frozen', False):
        # PyInstaller로 빌드된 실행 파일일 때
        return os.path.dirname(sys.executable)
    else:
        return ''
    
def get_key_path():
    if getattr(sys, 'frozen', False):
        # PyInstaller로 빌드된 실행 파일일 때
        base_path = os.path.dirname(os.path.dirname(sys.executable))
    else:
        # 개발 중일 때
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return os.path.join(base_path, 'config', 'key.json')

# 텍스트를 파일에서 불러오는 함수
def load_key():
    PATH_KEY = get_key_path()
    print(PATH_KEY)

    if os.path.exists(PATH_KEY):
        with open(PATH_KEY, 'r') as file:
            data = json.load(file)
            return data.get('key', None)
    return None

# 텍스트를 파일에 저장하는 함수
def save_key(key_value):
    PATH_KEY = get_key_path()
    print(PATH_KEY)

    with open(PATH_KEY, 'w') as file:
        json.dump({'key': key_value}, file)