import random

class Enum(list):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError

    def __getitem__(self, name):
        return self.__getattr__(name)

class Question:
    def __init__(self, first, operation, second):
        self.answer = eval(str(first)+operation.replace('x', '*')+str(second), {}, {})
        self.first = first
        self.second = second
        self.operation = operation

    def __str__(self):
        return '%d %s %d' % (self.first, self.operation, self.second)

Difficulties = Enum(('EASY', 'MEDIUM', 'HARD'))
Types = Enum(('ADDSUB', 'MULTDIV', 'ALL'))

def generateAddSub(difficulty):
    operations = '+-'
    operation = random.choice(operations)

    if difficulty == Difficulties.EASY:
        first = random.randint(1, 15)
        second = random.randint(1, 15)

        # negative numbers is hard, we can't deal
        if Question(first, operation, second).answer < 0:
            second, first = first, second

    elif difficulty == Difficulties.MEDIUM:
        first = random.randint(11, 50)
        second = random.randint(11, 60-first)
    elif difficulty == Difficulties.HARD:
        first = random.randint(11, 80)
        second = random.randint(11, 100-first)

    return Question(first, operation, second)

def generateMultDiv(difficulty):
    operations = '/x'
    operation = random.choice(operations)

    first, second = None, None

    if operation == '/':
        if difficulty == Difficulties.EASY:
            result = random.randint(0, 10)
            second = random.randint(1, 5)
        elif difficulty == Difficulties.MEDIUM:
            result = random.randint(0, 12)
            second = random.randint(1, 20)
        elif difficulty == Difficulties.HARD:
            result = random.randint(-12, 12)
            second = random.randint(-20, 20)
            if second == 0:
                second = -1

        first = result*second
    elif operation == 'x':
        if difficulty == Difficulties.EASY:
            first = random.randint(1, 8)
            second = random.randint(0, 10/first)
        elif difficulty == Difficulties.MEDIUM:
            first = random.randint(1, 12)
            second = random.randint(0, 80/first)
        elif difficulty == Difficulties.HARD:
            first = random.randint(-12, 12)
            if first == 0:
                first = 1
            second = random.randint(-80/first, 80/first)

    return Question(first, operation, second)


def generateQuestion(type, difficulty):
    assert difficulty in Difficulties
    assert type in Types

    if type == Types.ADDSUB:
        return generateAddSub(difficulty)
    elif type == Types.MULTDIV:
        return generateMultDiv(difficulty)

