#!/usr/bin/env python
from flask import render_template, request, make_response, session
import random
from time import time

from . import app

import config
import question
import database

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
        self.startTime = time()

    @staticmethod
    def fromSession(request):
        questionsRemaining = int(session[State.QUESTIONS_REMAINING_COOKIE])
        correctlyAnswered = int(session[State.CORRECTLY_ANSWERED_COOKIE])
        incorrectlyAnswered = int(session[State.INCORRECTLY_ANSWERED_COOKIE])
        startTime = float(session[State.START_TIME_COOKIE])

        return State(questionsRemaining, correctlyAnswered, incorrectlyAnswered, startTime)



@app.route('/quiz/<type>/<difficulty>', methods=('get', 'post'))
def quiz(**kwargs):
    try:
        state = State.fromSession(request)
    except KeyError:
        state = State()
    error = ''

    lastQuestion = None
    result = ''
    correctlyAnswered = False

    if 'quizId' not in session:
        session['quizId'] = database.create_quiz(kwargs['type'])

    try:
        lastQuestion = request.form['question']
        result = int(request.form['result'])
        correctlyAnswered = int(lastQuestion) == result
    except KeyError:
        pass
    except ValueError:
        print 'user entered invalid input'
        error += 'Please enter a number as your result'
        lastQuestion = None


    if lastQuestion is not None:
        database.log_quiz_answer(session['quizId'], lastQuestion, result, correctlyAnswered)
        if correctlyAnswered:
            state.correctlyAnswered += 1
        else:
            state.incorrectlyAnswered += 1


    # number of questions remaining in quiz
    # if we still have to ask questions of the user
    if state.questionsRemaining - 1 != 0:
        difficulty = question.Difficulties[kwargs['difficulty'].upper()]
        type = question.Types[kwargs['type'].upper()]

        q = question.generateQuestion(type, difficulty)

        response = make_response(render_template('quiz.html',
            numberRemaining=state.questionsRemaining,
            question=str(q),
            answer=q.answer,
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

