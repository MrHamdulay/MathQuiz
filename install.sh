#!/bin/bash
set -e
virtualenv-2.7 venv
. venv/bin/activate
git pull origin master

venv/bin/pip install -r requirements.txt
