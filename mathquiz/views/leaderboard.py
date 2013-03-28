from flask import render_template, session, redirect
from mathquiz import app, analytics, database, question

@app.route('/leaderboard/<scoring>/<difficulty>', defaults={'page': 0})
@app.route('/leaderboard/<scoring>/<difficulty>/<int:page>')
def leaderboard(difficulty, scoring, page):
    if page < 0:
        page = 0
    analytics.track('page', {'page':'leaderboard-%s-%s'%(scoring, difficulty)})

    try:
        difficulty = int(difficulty)
    except ValueError:
        difficulty = question.Difficulties.index(difficulty.upper())

    if scoring == 'streak':
        difficulty += 10
    leaderboard=database.leaderboard(page, difficulty)
    userPosition=None
    if sum(1 for x in leaderboard if x[2] == session['userId']) == 0:
        userPosition = (database.fetch_user_rank(session['userId'], difficulty),
                session['userId'],
                database.fetch_user_score(session['userId'], difficulty))

    leaderboardSize = database.leaderboard_size(difficulty)
    leaderboardPages = leaderboardSize / 10

    return render_template('leaderboard.html',
            page=page,
            scoring=scoring,
            lastPage=(page==leaderboardPages),
            leaderboard=leaderboard,
            difficulty=difficulty%10,
            difficultyName = question.Difficulties[difficulty%10],
            userPosition=userPosition)

@app.route('/leaderboard')
def redirect_leaderboard():
    return redirect('/leaderboard/points/%s' % (session['difficulty'].lower()))
