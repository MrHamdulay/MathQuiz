from flask import g, session

OPPONENT_LIST_KEY = 'opponent_list'

def start_random():
    opponentId = g.redis.lpop(OPPONENT_LIST_KEY)

    # if there aren't any opponents to go against
    if opponentId is None:
        g.redis.rpush(session['userId'])
        return False

    return opponentId