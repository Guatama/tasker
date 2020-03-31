import tasks.tasks as tasks

from functools import reduce


@tasks.task('charcount')
def char_count(text):
    count_char = 0
    count_space = 0
    for char in text:
        if char.isspace():
            count_space += 1
        elif char.isalpha():
            count_char += 1
    return {'char': count_char, 'space': count_space}


@tasks.task('delay')
def delay(params):
    import time
    print('start delay')
    time.sleep(20)
    print('end delay')


@tasks.task('multiprint')
def multi_print(msg, count=5):
    return '\n'.join(msg for _ in range(count))


@tasks.task('multiply')
def multiply(operands):
    return reduce(lambda x, y: x*y, operands)


class MultiPrint(tasks.BaseTask):
    name = 'multiprint_schema'
    json_schema = {'type': 'object',
                           'properties': {
                             'msg': {'type': 'string'},
                             'count': {'type': 'integer', 'minimum': 1}
                                         },
                           'required': ['msg']}

    def run_task(self, msg, count=5):
        return '\n'.join(msg for _ in range(count))


class ManyArg(tasks.BaseTask):
    name = 'manyarg'

    def run_task(self, a, b, c, d, e, f, g):
        result = a ** b + c - (d * e) + f + g
        return result


class Multiply(tasks.BaseTask):
    name = 'mult'
    json_schema = {'type': 'object',
                   'properties': {
                       'operands': {
                                    "type": "array",
                                    "minItems": 1,
                                    "items": {"type": "number"}
                                }
                            },
                       'required': ['operands']}

    def run_task(self, operands):
        return reduce(lambda x, y: x*y, operands)


if __name__ == "__main__":
    print('Tasks: ', list(tasks.TASK_LINE), '\n')
    tasks.run_cli()
    print('\nEND')
