from functools import reduce


def char_count(text):
    count_char = 0
    count_space = 0
    for char in text:
        if char.isspace():
            count_space += 1
        elif char.isalpha():
            count_char += 1
    return {'char': count_char, 'space': count_space}


def multi_print(msg, count=10):
    return '\n'.join(msg for _ in range(count))


def multiply(operands):
    return reduce(lambda x, y: x*y, operands)
