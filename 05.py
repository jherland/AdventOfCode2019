from functools import partial
from operator import add, eq, lt, mul, ne


class Jump(Exception):
    pass


class End(StopIteration):
    pass


def conditional_jump(test, arg, target):
    if test(arg):
        raise Jump(target)


def end(memory):
    raise End


ops = {
    1: (2, 1, add),
    2: (2, 1, mul),
    3: (0, 1, lambda memory: memory.pop()),
    4: (1, 0, print),
    5: (2, 0, partial(conditional_jump, partial(ne, 0))),
    6: (2, 0, partial(conditional_jump, partial(eq, 0))),
    7: (2, 1, lambda a, b: int(lt(a, b))),
    8: (2, 1, lambda a, b: int(eq(a, b))),
    99: (0, 0, end),
}


def step(memory, ip):
    modebits, op = divmod(memory[ip], 100)
    num_args, store_result, call = ops[op]
    if num_args:
        param_values = memory[ip + 1:ip + 1 + num_args]
        resolve_arg = {'0': lambda arg: memory[arg], '1': lambda arg: arg}
        args = [
            resolve_arg[mode](arg)
            for arg, mode in zip(param_values, '{:03d}'.format(modebits)[::-1])
        ]
    else:
        args = (memory, )
    try:
        result = call(*args)
    except Jump as j:
        return j.args[0]
    if store_result:
        memory[memory[ip + 1 + num_args]] = result
    return ip + 1 + num_args + store_result


def run(program, ip=0, input=None):
    memory = program[:]
    if input is not None:  # Pass through input at end of memory
        memory.append(input)
    try:
        while True:
            ip = step(memory, ip)
    except End:
        return memory[0]


with open('05.input') as f:
    program = list(map(int, f.read().split(',')))

# part 1
run(program, input=1)

# part 2
run(program, input=5)
