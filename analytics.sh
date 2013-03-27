#!/bin/bash
cd `dirname $0`
source venv/bin/activate
exec python2.7 analytics.py
