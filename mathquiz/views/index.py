from flask import session, render_template
from mathquiz import app, analytics, database


@app.route('/')
def index():
    session['quizId'] = -1
    analytics.track('page', {'page': 'index'})

    # if the user has not given us a username we should probably ask for one
    return render_template('index.html',
                           username = session['username'],
                           userId = session['userId'],
                           current_difficulty = session['difficulty'].title(),
                           actual_difficulty = database.fetch_user_difficulty(session['userId']).title(),
                           rank = database.fetch_user_rank(session['userId'], session['difficulty']),
                           total_users = database.fetch_number_users())
