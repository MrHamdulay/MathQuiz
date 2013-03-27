#!/bin/bash
cd `dirname $0`
. venv/bin/activate
exec python2.7 run.py $@
