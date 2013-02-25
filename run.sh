#!/bin/bash
. venv/bin/activate
python -c 'from mathquiz import app; app.run(debug=True)'

