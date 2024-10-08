import os
import sys
from os.path import join
from yaml import load, dump
from yaml import CLoader as Loader, CDumper as Dumper

class Config(object):
    def __init__(self):
        self.path = self.get_config_path()

    def get_config_path(self):
        if getattr(sys, 'frozen', False):
            # PyInstaller로 빌드된 실행 파일일 때
            base_path = sys._MEIPASS
        else:
            # 개발 중일 때
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        return os.path.join(base_path, 'config', 'config.yml')

    def parse(self):
        with open(self.path) as f:
            self.config = load(f, Loader=Loader)
        return self.config

    def save_config(self):
        with open(self.path, 'w') as f:
            dump(self.config, f)