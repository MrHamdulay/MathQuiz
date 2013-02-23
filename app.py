#!/usr/bin/env python
from flask import Flask, render_template, request, make_response, session
import random
from time import time
import config

app = Flask(__name__)
app.secret_key = 'testingthingy' #config.secret_key

import config


def generate_question(level=0):
    operations = '+-'
    size = 2
    question = (random.randint(1, 15) if i % 2 == 0 else random.choice(operations) for i in xrange(size*2-1))
    return ' '.join(map(str, question))

@app.route('/')
def index():
    return render_template('index.html')

class State:
    QUESTIONS_REMAINING_COOKIE = 'questionsRemaining'
    CORRECTLY_ANSWERED_COOKIE = 'correctlyAnswered'
    INCORRECTLY_ANSWERED_COOKIE = 'incorrectlyAnswered'
    START_TIME_COOKIE = 'time'

    def __init__(self, questionsRemaining = 5, correctlyAnswered = 0, incorrectlyAnswered = 0, startTime=time()):
        self.questionsRemaining = questionsRemaining
        self.correctlyAnswered = correctlyAnswered
        self.incorrectlyAnswered = incorrectlyAnswered
        self.startTime = startTime

    def updateState(self, response):
        session[State.QUESTIONS_REMAINING_COOKIE] = self.questionsRemaining
        session[State.CORRECTLY_ANSWERED_COOKIE] = self.correctlyAnswered
        session[State.INCORRECTLY_ANSWERED_COOKIE] = self.incorrectlyAnswered
        session[State.START_TIME_COOKIE] = self.startTime

    def reset(self):
        self.questionsRemaining = 5
        self.correctlyAnswered = 0
        self.incorrectlyAnswered = 0
        self.starTime = time()

    @staticmethod
    def fromCookies(request):
        questionsRemaining = int(session[State.QUESTIONS_REMAINING_COOKIE])
        correctlyAnswered = int(session[State.CORRECTLY_ANSWERED_COOKIE])
        incorrectlyAnswered = int(session[State.INCORRECTLY_ANSWERED_COOKIE])
        startTime = float(session[State.START_TIME_COOKIE])

        return State(questionsRemaining, correctlyAnswered, incorrectlyAnswered, startTime)

@app.route('/quiz/<level>', methods=('get', 'post'))
def quiz(**kwargs):
    try:
        state = State.fromCookies(request)
    except KeyError:
        state = State()
    error = ''

    lastQuestion = None
    result = ''
    correctlyAnswered = False

    try:
        lastQuestion = request.form['question']
        result = int(request.form['result'])
        correctlyAnswered = int(lastQuestion) == result
    except KeyError:
        print 'keyerror'
    except ValueError:
        print 'user entered invalid input'
        error += 'Please enter a number as your result'
        lastQuestion = None


    if lastQuestion is not None:
        if correctlyAnswered:
            state.correctlyAnswered += 1
        else:
            state.incorrectlyAnswered += 1


    # number of questions remaining in quiz
    # if we still have to ask questions of the user
    if state.questionsRemaining - 1 != 0:
        question = generate_question()
        answer = eval(question, {}, {})

        response = make_response(render_template('quiz.html',
            numberRemaining=state.questionsRemaining,
            question=question,
            answer=answer,
            error=error,
            answered = result != '', #has the user answered this question
            correct=correctlyAnswered))

        # decrease remaining questions counter if the user answered the question
        if result:
            state.questionsRemaining -= 1
    else:
        response = make_response(render_template('quizComplete.html',
            numberCorrect=state.correctlyAnswered,
            total=state.correctlyAnswered+state.incorrectlyAnswered,
            time=round(time()-state.startTime, 1)))
        state.reset()

    state.updateState(response)
    return response

@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html', leaderboard=(('yaseen', '0:05'), ('shuaib parker', '0:05'), ('salaama maniveld', '0:06')))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
