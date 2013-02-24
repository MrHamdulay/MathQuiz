import random

class Enum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError

difficulties = Enum('EASY', 'MEDIUM', 'HARD')
types = Enum('ADDSUB', 'MULTDIV')

def generateAddSub(difficulty):
    operations = '+-'
    operation = random.choice(operations)

    answer = None
    if difficulty == difficulties.EASY:
        first = random.randint(1, 15)
        second = random.randint(1, 15)

        answer = eval(first+operation+second, {}, {})
        # negative numbers is hard, we don't deal
        if answer < 0:
            answer *= -1
            first, second = second, first
    elif difficulty == difficulties.MEDIUM:
        first = random.randint(11, 50)
        second = random.randint(11, 60-first)
    elif difficulty == difficulties.HARD:
        first = random.randint(11, 80)
        second = random.randint(11, 100-first)

    answer = eval(first+operation+second, {}, {})

    return (first, operation, second), answer

def generateMultDiv(difficulty):
    operations = '/x'
    operation = random.choice(operations)


def generateQuestion(type, difficulty):
    assert difficulty in difficulties
    assert type in types

    if type == types.ADDSUB:
        generateAddSub(difficulty)
    elif type == types.MULTDIV:
        generateMultDiv(difficulty)

