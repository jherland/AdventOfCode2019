from functools import partial
from itertools import product


def args(nargs, nresults, program, ip, param_modes):
    args = program[ip + 1:ip + 1 + nargs + nresults]
    # Results are always addresses that we need to return (as if 'immediate')
    modes = param_modes[:nargs] + ['imm'] * nresults
    resolve_arg = {'pos': lambda arg: program[arg], 'imm': lambda arg: arg}
    return [resolve_arg[mode](arg) for arg, mode in zip(args, modes)]


def binary_op(do_op, program, ip, param_modes, input):
    a, b, result = args(2, 1, program, ip, param_modes)
    #  print('Combining', a, 'and', b, '->', result)
    program[result] = do_op(a, b)
    return ip + 4


def do_input(program, ip, param_modes, input):
    addr, = args(0, 1, program, ip, param_modes)
    program[addr] = input
    return ip + 2


def do_output(program, ip, param_modes, input):
    arg = args(1, 0, program, ip, param_modes)
    print('Output:', arg)
    return ip + 2


def conditional_jump(predicate, program, ip, param_modes, input):
    condition, target = args(2, 0, program, ip, param_modes)
    return target if predicate(condition) else ip + 3


def binary_test(predicate, program, ip, param_modes, input):
    a, b, result = args(2, 1, program, ip, param_modes)
    program[result] = 1 if predicate(a, b) else 0
    return ip + 4


def end(program, ip, param_modes, input):
    raise StopIteration


ops = {
    1: partial(binary_op, lambda a, b: a + b),
    2: partial(binary_op, lambda a, b: a * b),
    3: do_input,
    4: do_output,
    5: partial(conditional_jump, lambda arg: arg != 0),
    6: partial(conditional_jump, lambda arg: arg == 0),
    7: partial(binary_test, lambda a, b: a < b),
    8: partial(binary_test, lambda a, b: a == b),
    99: end,
}


def decode(opcode):
    modebits, op = divmod(opcode, 100)
    modedecode = {'0': 'pos', '1': 'imm'}
    return op, [modedecode[c] for c in '{:03d}'.format(modebits)[::-1]]


def run(program, noun=None, verb=None, ip=0, input=None):
    program = program[:]
    if noun is not None:
        program[1] = noun
    if verb is not None:
        program[2] = verb
    try:
        while True:
            #  print('  Next:', program[ip:ip + 4])
            op, param_modes = decode(program[ip])
            #  print('Op:', op, 'Modes:', param_modes)
            ip = ops[op](program, ip, param_modes, input)
    except StopIteration:
        return program[0]


with open('05.input') as f:
    program = list(map(int, f.read().split(',')))

# part 1
run(program, input=1)

# part 2
run(program, input=5)
