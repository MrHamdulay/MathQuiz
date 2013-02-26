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



@app.route('/quiz/<typee>/<difficulty>', methods=('get', 'post'))
def quiz(typee, difficulty):
    #convert string types to internal enums
    difficulty = question.Difficulties[difficulty.upper()]
    type = question.Types[typee.upper()]

    try:
        state = State.fromSession(request)
    except KeyError:
        state = State()
    error = ''

    previousAnswer, userAnswer, userAnswerCorrect = None, None, None

    if 'quizId' not in session:
        session['quizId'] = database.create_quiz(type)
    else:
        # if we have already started the quiz
        try:
            previousAnswer = int(request.form['question'])
            userAnswer = int(request.form['result'])
            userAnswerCorrect = previousAnswer == userAnswer

            database.log_quiz_answer(session['quizId'], previousAnswer, userAnswer, userAnswerCorrect)
            if userAnswerCorrect:
                state.correctlyAnswered += 1
            else:
                state.incorrectlyAnswered += 1
        except (ValueError, KeyError):
            error += 'Please enter a number as an answer'

    # number of questions remaining in quiz
    # if we still have to ask questions of the user
    if state.questionsRemaining - 1 != 0:
        q = question.generateQuestion(type, difficulty)

        response = make_response(render_template('quiz.html',
            numberRemaining=state.questionsRemaining,
            question=str(q),
            answer=q.answer,
            error=error,
            answered = userAnswer != '', #has the user answered this question
            correct=userAnswerCorrect))

        # decrease remaining questions counter if the user answered the question
        if userAnswer is not None:
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

