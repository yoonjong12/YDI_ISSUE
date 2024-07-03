from yaml import load, dump
from yaml import CLoader as Loader, CDumper as Dumper

class Config(object):
    def __init__(
            self, 
            path_config=''):

        self.config_file_path = path_config

    def parse(self):
        with open(self.config_file_path, 'rb') as f:
            self.config = load(f, Loader=Loader)
        return self.config

    def save_config(self):
        with open(self.config_file_path, 'w') as f:
            dump(self.config, f)