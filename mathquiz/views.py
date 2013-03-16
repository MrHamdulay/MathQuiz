#!/usr/bin/env python
from flask import render_template, request, make_response, session, redirect, url_for, flash
import random
from time import time

from . import app

import config
import question
import database
import analytics

@app.route('/feedback', methods=('post', 'get'))
def feedback():
    if 'feedback' in request.form:
        feedback = request.form['feedback']
        database.submit_feedback(session['userId'], feedback)
        flash('Thank you for your feedback.')
        return redirect('/')
    else:
        return render_template('feedback.html')

@app.route('/set_difficulty')
@app.route('/set_difficulty/<difficulty>')
def set_difficulty(difficulty=None):
    if difficulty is None:
        difficulty = question.Difficulties.index(database.fetch_user_difficulty(session['userId']))
        return render_template('change_difficulty.html', difficulty=difficulty)

    if difficulty.upper() in question.Difficulties:
        session['difficulty'] = difficulty.upper()
        return redirect('/')
    else:
        return 'unknown difficulty'

@app.route('/')
def index():
    session['quizId'] = -1
    analytics.track('page', {'user': session['userId'], 'page':'index'})


    # if the user has not given us a username we should probably ask for one
    return render_template('index.html',
            username=session['username'],
            userId=session['userId'],
            current_difficulty=session['difficulty'].title(),
            actual_difficulty=database.fetch_user_difficulty(session['userId']).title(),
            rank=database.fetch_user_rank(session['userId'], session['difficulty']),
            total_users=database.fetch_number_users()
        )


@app.route('/quiz/<typee>', methods=('get', 'post'))
def quiz(typee):
    #convert string types to internal enums
    difficulty = question.Difficulties[session['difficulty'].upper()]
    type = question.Types[typee.upper()]
    if type == question.Types.ALL:
        type = random.choice(list(question.Types))
        # looks ugly but we don't want to accidently get ourselves into a
        # semi infinite loop where we always choose Type.ALL do we?
        if type == question.Types.ALL:
            type = question.Types.ADDSUB

    startTime = time()
    try:
        correctlyAnswered = int(session['correctlyAnswered'])
        incorrectlyAnswered = int(session['incorrectlyAnswered'])
        startTime = float(session['startTime'])
    except KeyError:
        # force a new quiz
        session['quizId'] = -1
        analytics.track('new_quiz', {'user': session['userId']})

    previousAnswer, userAnswer, userAnswerCorrect = None, None, None
    scoring = []


    # number of questions remaining in quiz
    # if we still have to ask questions of the user
    timeRemaining = 30 - (time() - startTime)

    if 'quizId' not in session or session['quizId'] == -1:
        quizId = session['quizId'] = database.create_quiz(type)
        startTime = session['startTime'] = time()
        timeRemaining = 30
        correctlyAnswered = session['correctlyAnswered'] = 0
        incorrectlyAnswered = session['incorrectlyAnswered'] = 0

    elif timeRemaining >= 0:
        # if we have already started the quiz
        try:
            previousAnswer = session['previousQuestionAnswer']
            userAnswer = int(request.form['result'])
            userAnswerCorrect = previousAnswer == userAnswer

            score = question.score(type, difficulty, userAnswerCorrect)

            database.quiz_answer(session['userId'], session['quizId'], previousAnswer, userAnswer, userAnswerCorrect, score)
            # calculate streak bonus
            streakLength = database.calculate_streak_length(session['userId'], session['quizId'])
            streakScore = 0 if streakLength < 3 else 5 + streakLength
            score += streakScore
            if streakScore != 0:
                scoring.append('Streak of %d. %d bonus points!' % (streakLength, streakScore))


            scoring.append('Score so far: %d points!' % database.cumulative_quiz_score(session['quizId']))
            analytics.track('quiz_answer', {'user': session['userId'], 'quiz':session['quizId'], 'correct':userAnswerCorrect})
            if userAnswerCorrect:
               correctlyAnswered += 1
            else:
               incorrectlyAnswered += 1
        except (ValueError, KeyError):
            flash('Please enter a number as an answer')

    if timeRemaining >= 0:
        q = question.generateQuestion(type, difficulty)
        session['previousQuestionAnswer'] = q.answer

        response = make_response(render_template('quiz.html',
            question=str(q),
            scoring=scoring,
            timeRemaining=int(timeRemaining),
            answered = userAnswer is not None, #has the user answered this question
            correct=userAnswerCorrect,
            correctAnswer=previousAnswer))
    else:
        # calculate score
        numberAnswered = correctlyAnswered+incorrectlyAnswered

        oldHighScore = database.fetch_user_score(session['userId'], difficulty)
        oldLeaderboardPosition = database.fetch_user_rank(session['userId'], difficulty)
        score = database.quiz_complete(difficulty, session['quizId'], correctlyAnswered, numberAnswered)
        newLeaderboardPosition = database.fetch_user_rank(session['userId'], difficulty)
        leaderboardJump = None
        if oldLeaderboardPosition is not None and newLeaderboardPosition is not None:
            leadboardJump = newLeaderboardPosition - oldLeaderboardPosition

        analytics.track('quiz_completed', {'user':session['userId'], 'quiz':session['quizId'], 'score':score})
        # reset quiz
        session['quizId'] = -1

        newDifficulty = False
        # if user answered > 80% of answers correctly and answered > 10 correctly increase difficulty level
        if numberAnswered >= 8 and (float(correctlyAnswered) / numberAnswered) > 0.8:
            newDifficultyIndex = question.Difficulties.index(session['difficulty'].upper())+1
            # don't go over max difficulty (hard)
            if newDifficultyIndex < len(question.Difficulties):
                if newDifficultyIndex > question.Difficulties.index(database.fetch_user_difficulty(session['userId'])):
                    newDifficulty = question.Difficulties[newDifficultyIndex].lower()
                    analytics.track('difficulty_increased', {'user':session['userId'], 'new_difficulty':newDifficulty})
                    database.set_user_difficulty(session['userId'], newDifficultyIndex)


        response = make_response(render_template('quizComplete.html',
            correct=userAnswerCorrect,
            numberCorrect=correctlyAnswered,
            newDifficulty=newDifficulty,
            oldHighScore=oldHighScore,
            score=score,
            leaderboardJump=leaderboardJump,
            total=correctlyAnswered+incorrectlyAnswered))


    # persist changes to session
    session['correctlyAnswered'] = correctlyAnswered
    session['incorrectlyAnswered'] = incorrectlyAnswered

    return response

@app.route('/leaderboard')
def redirect_leaderboard():
    return redirect('/leaderboard/%s' % (session['difficulty'].lower()))

@app.route('/leaderboard/<difficulty>', defaults={'page': 0})
@app.route('/leaderboard/<difficulty>/<int:page>')
def leaderboard(difficulty, page):
    if page < 0:
        page = 0
    analytics.track('page', {'user': session['userId'], 'page':'leaderboard-'+difficulty})
    leaderboard=database.leaderboard(page, difficulty)

    leaderboardSize = database.leaderboard_size(difficulty)
    leaderboardPages = leaderboardSize / 10

    return render_template('leaderboard.html',
            page=page,
            lastPage=(page==leaderboardPages),
            leaderboard=leaderboard)


@app.route('/user/profile/<int:user_id>')
def profile(user_id):
    analytics.track('page', {'user': session['userId'], 'page':'profile-'+user_id})
    analytics.track('page', {'user': session['userId'], 'page':'profile'})
    username=database.fetch_user_difficulty(user_id)
    difficulty=database.fetch_user_difficulty(user_id)
    startedDate=database.fetch_user_joined_date(user_id)

    gamesPlayed=database.fetch_user_games_started(user_id)
    gamesCompleted=database.fetch_user_games_completed(user_id)

    highscores = [database.fetch_user_score(user_id, difficulty) for difficulty in question.Difficulties]
    print highscores

    return render_template('profile.html',
            username=username,
            difficulty=difficulty,
            startDated=startedDate,
            gamesPlayed=gamesPlayed,
            gamesCompleted=gamesCompleted,
            highscores=highscores
        )
