#!/usr/bin/env bash
git add .
git commit -m "local"
git pull
chmod +x main.py
python3 main.py