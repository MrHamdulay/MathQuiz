import random

class Enum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError

class Question:
    def __init__(self, first, operation, second):
        self.answer = eval(str(first)+str(operation)+str(second), {}, {})
        self.first = first
        self.second = second

    def __str__(self):
        return '%d %s %d' % (self.first, self.operation, self.second)

difficulties = Enum('EASY', 'MEDIUM', 'HARD')
types = Enum('ADDSUB', 'MULTDIV')

def generateAddSub(difficulty):
    operations = '+-'
    operation = random.choice(operations)

    if difficulty == difficulties.EASY:
        first = random.randint(1, 15)
        second = random.randint(1, 15)

        answer = eval(first+operation+second, {}, {})
        # negative numbers is hard, we can't deal
        if answer < 0:
            second, first = first, second

    elif difficulty == difficulties.MEDIUM:
        first = random.randint(11, 50)
        second = random.randint(11, 60-first)
    elif difficulty == difficulties.HARD:
        first = random.randint(11, 80)
        second = random.randint(11, 100-first)

    return Question(first, operation, second)

def generateMultDiv(difficulty):
    operations = '/x'
    operation = random.choice(operations)

    first, second = None, None

    if operation == '/':
        if difficulty == difficulties.EASY:
            result = random.randint(0, 10)
            second = random.randint(0, 5)
        elif difficulty == difficulties.MEDIUM:
            result = random.randint(0, 12)
            second = random.randint(0, 20)
        elif difficulty == difficulties.HARD:
            result = random.randint(-12, 12)
            second = random.randint(-20, 20)

        first = result*second
    elif operation == '*':
        if difficulty = difficulties.EASY:
            first = random.randint(0, 8)
            second = random.randint(0, 10/first)
        elif difficulty = difficulties.MEDIUM:
            first = random.randint(0, 12)
            second = random.randint(0, 80/first)
        elif
            first = random.randint(-12, 12)
            second = random.randint(-80/first, 80/first)

    return Question(first, operation, second)


def generateQuestion(type, difficulty):
    assert difficulty in difficulties
    assert type in types

    if type == types.ADDSUB:
        generateAddSub(difficulty)
    elif type == types.MULTDIV:
        generateMultDiv(difficulty)

