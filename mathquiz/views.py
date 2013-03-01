#!/usr/bin/env python
from flask import render_template, request, make_response, session, redirect, url_for, flash
import random
from time import time

from . import app

import config
import question
import database

@app.route('/user/set_username', methods=('get', 'post'))
def set_username():
    if 'username' in request.form:
        username = request.form['username']
        if database.username_exists(username):
            return render_template('set_username.html', username_exists = username)
        else:
            session['username'] = username
            database.set_username(username)
            return redirect('/')
    else:
        return render_template('set_username.html')

@app.route('/')
def index():
    session['quizId'] = -1

    # if the user has not given us a username we should probably ask for one
    if not session.has_key('username') or session['username'] is None:
       return redirect('/user/set_username')

    return render_template('index.html',
            username=session['username'],
            difficulty='Easy',
        )


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
        # force a new quiz
        session['quizId'] = -1

    previousAnswer, userAnswer, userAnswerCorrect = None, None, None
    scoring = ''

    if 'quizId' not in session or session['quizId'] == -1:
        quizId = session['quizId'] = database.create_quiz(type)
        startTime = session['startTime'] = time()
        questionsRemaining = session['questionsRemaining'] = 15
        correctlyAnswered = session['correctlyAnswered'] = 0
        incorrectlyAnswered = session['incorrectlyAnswered'] = 0

    else:
        # if we have already started the quiz
        try:
            previousAnswer = session['previousQuestionAnswer']
            userAnswer = int(request.form['result'])
            userAnswerCorrect = previousAnswer == userAnswer

            score = 5 if userAnswerCorrect else 0

            # calculate streak bonus
            streakLength = database.calculate_streak_length(session['userId'], session['quizId'])
            streakScore = 0 if streakLength < 5 else 5 + streakLength
            score += streakScore
            if streakScore != 0:
                scoring = 'Streak of %d. %d bonus points!' % (streakLength, streakScore)

            database.quiz_answer(session['userId'], session['quizId'], previousAnswer, userAnswer, userAnswerCorrect, score)
            if userAnswerCorrect:
               correctlyAnswered += 1
            else:
               incorrectlyAnswered += 1
        except (ValueError, KeyError):
            flash('Please enter a number as an answer')

    # number of questions remaining in quiz
    # if we still have to ask questions of the user
    if questionsRemaining - 1 != 0:
        q = question.generateQuestion(type, difficulty)
        session['previousQuestionAnswer'] = q.answer

        response = make_response(render_template('quiz.html',
            numberRemaining=questionsRemaining,
            question=str(q),
            scoring=scoring,
            answered = userAnswer is not None, #has the user answered this question
            correct=userAnswerCorrect))

        # decrease remaining questions counter if the user answered the question
        if userAnswer is not None:
            questionsRemaining -= 1
    else:
        # calculate score
        database.quiz_complete(session['quizId'], correctlyAnswered, correctlyAnswered+incorrectlyAnswered)
        response = make_response(render_template('quizComplete.html',
            correct=userAnswerCorrect,
            numberCorrect=correctlyAnswered,
            total=correctlyAnswered+incorrectlyAnswered,
            time=round(time()-startTime, 1)))

        session['quizId'] = -1


    # persist changes to session
    session['questionsRemaining'] = questionsRemaining
    session['correctlyAnswered'] = correctlyAnswered
    session['incorrectlyAnswered'] = incorrectlyAnswered

    return response

@app.route('/leaderboard', defaults={'page': 0})
@app.route('/leaderboard/<int:page>')
def leaderboard(page):
    return render_template('leaderboard.html', leaderboard=database.leaderboard(page))
