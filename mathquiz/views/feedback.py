from flask import request, render_template, session, flash, redirect

from mathquiz import app, analytics, database
from mathquiz.analytics import stats

@app.route('/feedback', methods=('post', 'get'))
def feedback():
    if 'feedback' in request.form:
        feedback = request.form['feedback']
        database.submit_feedback(session['userId'], feedback)
        flash('Thank you for your feedback.')
        analytics.track('feedback')
        stats.incr('mathchallenge.feedback')

        return redirect('/')
    else:
        analytics.track('page', {'page':'feedback'})
        stats.incr('mathchallenge.pageview.feedback')
        return render_template('feedback.html')
