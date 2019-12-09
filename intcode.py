from dataclasses import dataclass
from functools import partial
from operator import add, eq, lt, mul, ne
from typing import Callable, List


@dataclass
class State:
    memory: List[int]
    ip: int = 0  # instruction pointer
    rb: int = 0  # relative base
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
        rb = self.rb
        input_ = self.input_ if input_ is None else input_
        output = self.output if output is None else output
        return State(memory, ip, rb, input_, output)


def decode(opcode):
    modebits, op = divmod(opcode, 100)  # mode bits: 0: position, 1: immediate
    return op, [int(digit) for digit in '{:03d}'.format(modebits)[::-1]]


def load(state, address):
    if address >= len(state.memory):
        state.memory += [0] * (address + 1 - len(state.memory))
    return state.memory[address]


def store(state, address, value):
    if address >= len(state.memory):
        state.memory += [0] * (address + 1 - len(state.memory))
    state.memory[address] = value


def args(nargs, nresults, state, param_modes):
    args = state.memory[state.ip + 1:state.ip + 1 + nargs + nresults]
    arg_decode = [
        lambda arg: load(state, arg),  # positional mode
        lambda arg: arg,  # immediate mode
        lambda arg: load(state, state.rb + arg)  # relative mode
    ]
    # Results are either direct addresses (mode 0) or relative to RB (mode 2)
    result_decode = [
        lambda arg: arg, NotImplemented, lambda arg: state.rb + arg
    ]
    decoders = [arg_decode[m] for m in param_modes[:nargs]]
    decoders += [result_decode[m] for m in param_modes[nargs:nargs + nresults]]
    return [decoders[i](arg) for i, arg in enumerate(args)]


def binary_op(do_op, state, param_modes):
    a, b, result = args(2, 1, state, param_modes)
    store(state, result, do_op(a, b))
    return state.ip + 4


def do_input(state, param_modes):
    addr, = args(0, 1, state, param_modes)
    store(state, addr, state.input_())
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
    store(state, result, 1 if predicate(a, b) else 0)
    return state.ip + 4


def adjust_relative_base(state, param_modes):
    a, = args(1, 0, state, param_modes)
    state.rb += a
    return state.ip + 2


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
    9: adjust_relative_base,
    99: end,
}


def run(state):
    try:
        while True:
            op, param_modes = decode(state.memory[state.ip])
            state.ip = ops[op](state, param_modes)
    except StopIteration:
        return state
