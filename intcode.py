from dataclasses import dataclass
from functools import partial
from operator import add, eq, lt, mul, ne
from typing import Callable, List


@dataclass
class State:
    memory: List[int]
    ip: int = 0
    input_: Callable[[], int] = lambda: int(input().rstrip())
    output: Callable[[int], None] = print

    @classmethod
    def parse(cls, f):
        return cls(list(map(int, f.read().split(','))))

    def clone(self, noun=None, verb=None, ip=None, input_=None, output=print):
        memory = self.memory[:]
        if noun is not None:
            memory[1] = noun
        if verb is not None:
            memory[2] = verb
        ip = self.ip if ip is None else ip
        input_ = self.input_ if input_ is None else input_
        output = self.output if output is None else output
        return State(memory, ip, input_, output)


def decode(opcode):
    modebits, op = divmod(opcode, 100)  # mode bits: 0: position, 1: immediate
    return op, [int(digit) for digit in '{:02d}'.format(modebits)[::-1]]


def args(nargs, nresults, state, param_modes):
    args = state.memory[state.ip + 1:state.ip + 1 + nargs + nresults]
    arg_decoders = [lambda arg: state.memory[arg], lambda arg: arg]
    # Results are always addresses that we need to return (as if 'immediate')
    modes = param_modes[:nargs] + [1] * nresults
    return [arg_decoders[mode](arg) for arg, mode in zip(args, modes)]


def binary_op(do_op, state, param_modes):
    a, b, result = args(2, 1, state, param_modes)
    state.memory[result] = do_op(a, b)
    return state.ip + 4


def do_input(state, param_modes):
    addr, = args(0, 1, state, param_modes)
    state.memory[addr] = state.input_()
    return state.ip + 2


def do_output(state, param_modes):
    arg, = args(1, 0, state, param_modes)
    state.output(arg)
    return state.ip + 2


def conditional_jump(predicate, state, param_modes):
    condition, target = args(2, 0, state, param_modes)
    return target if predicate(condition) else state.ip + 3


def binary_test(predicate, state, param_modes):
    a, b, result = args(2, 1, state, param_modes)
    state.memory[result] = 1 if predicate(a, b) else 0
    return state.ip + 4


def end(state, param_modes):
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


def run(state):
    try:
        while True:
            op, param_modes = decode(state.memory[state.ip])
            state.ip = ops[op](state, param_modes)
    except StopIteration:
        return state
