from mathquiz import app
from mathquiz.model import battleModel


@app.route('/battle/start/random')
def battle_start():
    return 'result %s'%battleModel.start_random()