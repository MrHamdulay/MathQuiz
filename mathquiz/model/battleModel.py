from flask import g, session

OPPONENT_LIST_KEY = 'opponent_list'


def find_opponent():
    opponentId = g.redis.lpop(OPPONENT_LIST_KEY)

    # if there aren't any opponents to go against add ourselves to the list
    if opponentId is None:
        g.redis.rpush(session['userId'])

    return opponentId