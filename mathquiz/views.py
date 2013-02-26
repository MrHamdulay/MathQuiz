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
    del session['quizId']
    return render_template('index.html')


@app.route('/quiz/<typee>/<difficulty>', methods=('get', 'post'))
def quiz(typee, difficulty):
    #convert string types to internal enums
    difficulty = question.Difficulties[difficulty.upper()]
    type = question.Types[typee.upper()]

    try:
        questionsRemaining = int(session['questionsRemaining'])
        correctlyAnswered = int(session['correctlyAnswered'])
        incorrectlyAnswered = int(session['incorrectlyAnswered'])
        startTime = float(session['startTime'])
    except KeyError:
        questionsRemaining = 5
        correctlyAnswered = 0
        incorrectlyAnswered = 0
        startTime = time()
    error = ''

    previousAnswer, userAnswer, userAnswerCorrect = None, None, None

    if 'quizId' not in session:
        session['quizId'] = database.create_quiz(type)
        session['startTime'] = time()
        session['questionsRemaining'] = 5
        session['correctlyAnswered'] = 0
        session['incorrectlyAnswered'] = 0

    else:
        # if we have already started the quiz
        try:
            previousAnswer = session['previousQuestionAnswer']
            userAnswer = int(request.form['result'])
            userAnswerCorrect = previousAnswer == userAnswer

            database.log_quiz_answer(session['quizId'], previousAnswer, userAnswer, userAnswerCorrect)
            if userAnswerCorrect:
               correctlyAnswered += 1
            else:
               incorrectlyAnswered += 1
        except (ValueError, KeyError):
            error += 'Please enter a number as an answer'

    # number of questions remaining in quiz
    # if we still have to ask questions of the user
    if questionsRemaining - 1 != 0:
        q = question.generateQuestion(type, difficulty)
        session['previousQuestionAnswer'] = q.answer

        response = make_response(render_template('quiz.html',
            numberRemaining=questionsRemaining,
            question=str(q),
            error=error,
            answered = userAnswer != '', #has the user answered this question
            correct=userAnswerCorrect))

        # decrease remaining questions counter if the user answered the question
        if userAnswer is not None:
            questionsRemaining -= 1
    else:
        score = max(0, 10*correctlyAnswered - 15 * incorrectlyAnswered)

        database.quiz_complete(session['quizId'], correctlyAnswered, correctlyAnswered+incorrectlyAnswered, score)
        response = make_response(render_template('quizComplete.html',
            numberCorrect=correctlyAnswered,
            total=correctlyAnswered+incorrectlyAnswered,
            time=round(time()-startTime, 1)))


    # persist changes to session
    session['questionsRemaining'] = questionsRemaining
    session['correctlyAnswered'] = correctlyAnswered
    session['incorrectlyAnswered'] = incorrectlyAnswered

    return response

@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html', leaderboard=(('yaseen', '0:05'), ('shuaib parker', '0:05'), ('salaama maniveld', '0:06')))

