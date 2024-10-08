#!/bin/bash
pyinstaller --onefile --add-data "src:src" --add-data "config/config.yml:config" --add-data "data:data" execute.py
