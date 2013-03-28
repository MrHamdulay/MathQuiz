from flask import render_template

from mathquiz import app, analytics, database, question
@app.route('/user/profile/<int:user_id>')
def profile(user_id):
    analytics.track('page', {'page':'profile-%d'%user_id})
    analytics.track('page', {'page':'profile'})
    username=database.fetch_user_name(user_id)
    difficulty=database.fetch_user_difficulty(user_id)

    startedDate=database.fetch_user_joined_date(user_id)

    gamesPlayed=database.fetch_user_games_started(user_id)
    gamesCompleted=database.fetch_user_games_completed(user_id)

    highscores = [database.fetch_user_score(user_id, d) for d in question.Difficulties]

    return render_template('profile.html',
            username=username,
            difficulty=difficulty,
            startDated=startedDate,
            gamesPlayed=gamesPlayed,
            gamesCompleted=gamesCompleted,
            highscores=highscores)
