from functools import partial
from operator import add, eq, lt, mul, ne


def decode(opcode):
    modebits, op = divmod(opcode, 100)  # mode bits: 0: position, 1: immediate
    return op, [int(digit) for digit in '{:02d}'.format(modebits)[::-1]]


def args(nargs, nresults, memory, ip, param_modes):
    args = memory[ip + 1:ip + 1 + nargs + nresults]
    arg_decoders = [lambda arg: memory[arg], lambda arg: arg]
    # Results are always addresses that we need to return (as if 'immediate')
    modes = param_modes[:nargs] + [1] * nresults
    return [arg_decoders[mode](arg) for arg, mode in zip(args, modes)]


def binary_op(do_op, memory, ip, param_modes):
    a, b, result = args(2, 1, memory, ip, param_modes)
    memory[result] = do_op(a, b)
    return ip + 4


def do_input(memory, ip, param_modes):
    addr, = args(0, 1, memory, ip, param_modes)
    memory[addr] = memory.pop()  # input is passed through at end of memory
    return ip + 2


def do_output(memory, ip, param_modes):
    arg, = args(1, 0, memory, ip, param_modes)
    print(arg)
    return ip + 2


def conditional_jump(predicate, memory, ip, param_modes):
    condition, target = args(2, 0, memory, ip, param_modes)
    return target if predicate(condition) else ip + 3


def binary_test(predicate, memory, ip, param_modes):
    a, b, result = args(2, 1, memory, ip, param_modes)
    memory[result] = 1 if predicate(a, b) else 0
    return ip + 4


def end(memory, ip, param_modes):
    raise StopIteration


ops = {
    1: partial(binary_op, add),
    2: partial(binary_op, mul),
    3: do_input,
    4: do_output,
    5: partial(conditional_jump, partial(ne, 0)),
    6: partial(conditional_jump, partial(eq, 0)),
    7: partial(binary_test, lt),
    8: partial(binary_test, eq),
    99: end,
}


def run(program, noun=None, verb=None, ip=0, input=None):
    memory = program[:]
    if input is not None:  # Pass through input at end of memory
        memory.append(input)
    if noun is not None:
        memory[1] = noun
    if verb is not None:
        memory[2] = verb
    try:
        while True:
            op, param_modes = decode(memory[ip])
            ip = ops[op](memory, ip, param_modes)
    except StopIteration:
        return memory[0]


with open('05.input') as f:
    program = list(map(int, f.read().split(',')))

# part 1
run(program, input=1)

# part 2
run(program, input=5)
