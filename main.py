#!/usr/bin/env python
from flask import Flask, render_template, request, make_response
import random

app = Flask(__name__)


def generate_question(level=0):
    operations = '+-'
    size = 3
    question = (random.randint(1, 30) if i % 2 == 0 else random.choice(operations) for i in xrange(size*2-1))
    return ' '.join(map(str, question))

@app.route('/')
def index():
    return render_template('index.html')

class State:
    QUESTIONS_REMAINING_COOKIE = 'questionsRemaining'
    CORRECTLY_ANSWERED_COOKIE = 'correctlyAnswered'
    INCORRECTLY_ANSWERED_COOKIE = 'incorrectlyAnswered'

    def __init__(self, questionsRemaining = 5, correctlyAnswered = 0, incorrectlyAnswered = 0):
        self.questionsRemaining = questionsRemaining
        self.correctlyAnswered = correctlyAnswered
        self.incorrectlyAnswered = incorrectlyAnswered

    def updateState(self, response):
        response.set_cookie(QUESTIONS_REMAINING_COOKIE, self.questionsRemaining)
        response.set_cookie(CORRECTLY_ANSWERED_COOKIE, self.correctlyAnswered)
        response.set_cookie(INCORRECTLY_ANSWERED_COOKIE, self.incorrectlyAnswered)

    @staticmethod
    def fromCookies(self, request):
        questionsRemaining = request.cookies.get(QUESTIONS_REMAINING_COOKIE, 5)
        correctlyAnswered = request.cookies.get(CORRECTLY_ANSWERED_COOKIE, 0)
        incorrectlyAnswered = request.cookies.get(INCORRECTLY_ANSWERED_COOKIE, 0)

        return State(questionsRemaining, correctlyAnswered, incorrectlyAnswered)

@app.route('/quiz/<level>', methods=('get', 'post'))
def quiz(**kwargs):
    lastQuestion = request.form.get('question', None)
    result = request.form.get('result', '')

    correctlyAnswered = None
    if lastQuestion:
        correctlyAnswered = eval(lastQuestion) == result
        if correctlyAnswered:
            state.correctlyAnswered += 1
        else:
            state.incorrectlyAnswered += 1

    state = State.fromCookies(request)

    # number of questions remaining in quiz
    # if we still have to ask questions of the user
    if state.questionsRemaining - 1 != 0:
        response = make_response(render_template('quiz.html', numberRemaining=state.questionsRemaining, question=generate_question(), result = result, correct=correctlyAnswered))
        # decrease remaining questions counter if the user answered the question
        if result:
            state.questionsRemaining -= 1
    else:
        response = make_response(render_template('quizComplete.html'))

    state.updateState(response)
    return response

@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html', leaderboard=(('yaseen', '0:05'), ('shuaib parker', '0:05'), ('salaama maniveld', '0:06')))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
