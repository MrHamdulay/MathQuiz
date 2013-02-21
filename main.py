#!/usr/bin/env python
from flask import Flask, render_template
import random

app = Flask(__name__)

def generate_question(level=0):
    operations = '+-'
    size = 2
    question = (random.randint(1, 30) if i % 2 == 0 else random.choice(operations) for i in xrange(size*2-1))
    return ' '.join(map(str, question))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/quiz/<level>', methods=('get', 'post'))
def quiz(**kwargs):
    return render_template('quiz.html', numberRemaining=5, question=generate_question())

@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html', leaderboard=(('yaseen', '0:05'), ('shuaib parker', '0:05'), ('salaama maniveld', '0:06')))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
