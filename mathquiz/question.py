import random

class Enum(list):
    def __getattr__(self, name):
        if isinstance(name , int):
            return list.__getitem__(self, name)
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

def score(typee, difficulty, correct):
    score = 0

    # badass bonus
    if typee == Types.ALL:
        score += 3

    if not correct:
        return -3
    elif difficulty == Difficulties.EASY:
        score += 5
    elif difficulty == Difficulties.MEDIUM:
        score += 7
    else:
        score += 9

    return score

def generateAddSub(difficulty):
    operations = '+-'
    operation = random.choice(operations)

    allowNegative = False

    if difficulty == Difficulties.EASY:
        first = random.randint(1, 15)
        second = random.randint(1, 15)

    elif difficulty == Difficulties.MEDIUM:
        first = random.randint(11, 50)
        second = random.randint(min(11, 60-first), max(11, 60-first))
    elif difficulty == Difficulties.HARD:
        first = random.randint(11, 80)
        second = random.randint(min(11, 100-first), max(11, 100-first))
        allowNegative = True

    # negative numbers is hard, we can't deal
    print (first, operation, second)
    print 'answer', Question(first, operation, second).answer
    if not allowNegative and Question(first, operation, second).answer < 0:
        second, first = first, second
        assert(Question(first, operation, second).answer >= 0)

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
                second = 1

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

