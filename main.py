#!/usr/bin/env python
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/quiz/<level>', methods=('get', 'post'))
def quiz(**kwargs):
    return render_template('quiz.html', numberRemaining=5, question='4 + 3')

@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html', leaderboard=(('yaseen', '0:05'), ))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
