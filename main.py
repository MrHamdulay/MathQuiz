#!/usr/bin/env python
from flask import Flask, render_template, request, make_response
import random

app = Flask(__name__)

QUESTIONS_REMAINING_COOKIE = 'questionsRemaining'

def generate_question(level=0):
    operations = '+-'
    size = 3
    question = (random.randint(1, 30) if i % 2 == 0 else random.choice(operations) for i in xrange(size*2-1))
    return ' '.join(map(str, question))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/quiz/<level>', methods=('get', 'post'))
def quiz(**kwargs):
    lastQuestion = request.args.get('question', None)

    # number of questions remaining in quiz
    questionsRemaining = int(request.cookies.get(QUESTIONS_REMAINING_COOKIE, 6))
    # if we still have to ask questions of the user
    if questionsRemaining != 0:
        response = make_response(render_template('quiz.html', numberRemaining=questionsRemaining, question=generate_question()))
        # decrease remaining questions counter
        response.set_cookie(QUESTIONS_REMAINING_COOKIE, questionsRemaining-1)
    else:
        response = make_response(render_template('quizComplete.html'))
    return response

@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html', leaderboard=(('yaseen', '0:05'), ('shuaib parker', '0:05'), ('salaama maniveld', '0:06')))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
