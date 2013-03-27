#!/bin/bash
set -e
virtualenv-2.7 -p /usr/bin/python2.7 venv
. venv/bin/activate
git pull origin master

venv/bin/pip install -r requirements.txt

python pyga/setup.py install
python create_db.py
