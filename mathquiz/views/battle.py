import logging
from flask import render_template, session

from mathquiz import app, config
from mathquiz.model import battleModel
from MxitAPI import MxitAPI


# opponent must be a user id
def battle_notify(opponent, message):
    mxitApi = MxitAPI(config.client_id, config.secret_id, 'mathchallenge')
    mxitApi.auth(('message/send',))

    r = mxitApi.sendMessage(opponent, message)

    if not r.ok:
        logging.error('MXit api error', r.text)

    return r.ok


def notify_opponent(opponent):
    battle_notify(opponent, 'Your challenge has been accepted. Opponent: %s' % session['username'])


def notify_opponent_answer(opponent, answer):
    battle_notify(opponent, '%s: %s' % (session['username'], answer))


@app.route('/battle/start/random')
def battle_start():
    opponent = battleModel.find_opponent()

    if opponent is None:
        return render_template('template/battle_waiting.html')
    else:
        notify_opponent(opponent)

    return render_template('template/battle_start.html')