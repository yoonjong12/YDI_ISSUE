@echo off
pyinstaller --onefile --noconsole --add-data "src:src" --add-data "config/config.yml:config" --add-data "data:data" --hidden-import pydantic.deprecated.decorator execute.py
pause