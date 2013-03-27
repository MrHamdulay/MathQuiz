#!/bin/bash
set -e
virtualenv venv
. venv/bin/activate
git pull origin master

venv/bin/pip install -r requirements.txt

python pyga/setup.py install
python create_db.py
