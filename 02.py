from functools import partial
from itertools import product


def binary_op(op, program, ip):
    a, b, result = program[ip + 1:ip + 4]
    program[result] = op(program[a], program[b])
    return ip + 4


def end(program, ip):
    raise StopIteration


ops = {
    1: partial(binary_op, lambda a, b: a + b),
    2: partial(binary_op, lambda a, b: a * b),
    99: end,
}


def run(program, noun=None, verb=None, ip=0):
    program = program[:]
    if noun is not None:
        program[1] = noun
    if verb is not None:
        program[2] = verb
    try:
        while True:
            ip = ops[program[ip]](program, ip)
    except StopIteration:
        return program[0]


with open('02.input') as f:
    program = list(map(int, f.read().split(',')))

# part 1
print(run(program, 12, 2))

# part 2
target = 19690720
for n, v in product(range(100), range(100)):
    result = run(program, n, v)
    if result == target:
        break
print(100 * n + v)
