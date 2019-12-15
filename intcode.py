from dataclasses import dataclass
from functools import partial
from multiprocessing import Process, Queue
from operator import add, eq, lt, mul, ne
from typing import Callable, List, Optional


@dataclass
class IntCode:
    memory: List[int]
    ip: int = 0  # instruction pointer
    rb: int = 0  # relative base
    do_input: Callable[[], int] = lambda: int(input('Input:').rstrip())
    inputs: Optional[List[int]] = None
    do_output: Callable[[int], None] = print
    outputs: Optional[List[int]] = None

    @classmethod
    def from_file(cls, f):
        return cls(list(map(int, f.read().split(','))))

    def prepare(self, inputs=None, outputs=None, mem=None):
        memory = self.memory[:]
        if inputs is None:
            do_input = self.do_input
            inputs = self.inputs
        else:
            if callable(inputs):
                do_input = inputs
                inputs = None
            elif isinstance(inputs, list):
                do_input = partial(inputs.pop, 0)
            else:
                raise NotImplementedError
        if outputs is None:
            do_output = self.do_output
            outputs = self.outputs
        else:
            if callable(outputs):
                do_output = outputs
                outputs = None
            elif isinstance(outputs, list):
                do_output = outputs.append
            else:
                raise NotImplementedError
        if mem is not None:
            for addr, value in mem.items():
                memory[addr] = value
        return self.__class__(memory, self.ip, self.rb, do_input, inputs,
                              do_output, outputs)

    @staticmethod
    def decode(opcode):
        modebits, op = divmod(opcode, 100)
        return op, [int(digit) for digit in '{:03d}'.format(modebits)[::-1]]

    def load(self, address):
        if address >= len(self.memory):
            return 0
        return self.memory[address]

    def store(self, address, value):
        if address >= len(self.memory):  # extend memory if needed
            self.memory += [0] * (address + 1 - len(self.memory))
        self.memory[address] = value

    def resolve_args(self, nargs, nresults, modes):
        assert nargs + nresults <= len(modes)
        decoders = {
            ('in', 0): lambda arg: self.load(arg),  # positional mode
            ('in', 1): lambda arg: arg,  # immediate mode
            ('in', 2): lambda arg: self.load(self.rb + arg),  # relative mode
            ('out', 0): lambda arg: arg,  # absolute address
            ('out', 2): lambda arg: self.rb + arg,  # address relative to RB
        }
        dirs = ['in'] * nargs + ['out'] * nresults
        args = self.memory[self.ip + 1:self.ip + 1 + nargs + nresults]
        return [decoders[(d, m)](arg) for d, m, arg in zip(dirs, modes, args)]

    def arithmetic_op(self, func, param_modes):
        a, b, result = self.resolve_args(2, 1, param_modes)
        self.store(result, func(a, b))
        self.ip += 4

    def input_op(self, param_modes):
        addr, = self.resolve_args(0, 1, param_modes)
        self.store(addr, self.do_input())
        self.ip += 2

    def output_op(self, param_modes):
        arg, = self.resolve_args(1, 0, param_modes)
        # self.do_output() may throw; a subsequent .run() should not repeat it.
        self.ip += 2  # increment IP _first_
        self.do_output(arg)  # _then_ call .do_output()

    def jump_op(self, predicate, param_modes):
        condition, target = self.resolve_args(2, 0, param_modes)
        self.ip = target if predicate(condition) else self.ip + 3

    def test_op(self, predicate, param_modes):
        a, b, result = self.resolve_args(2, 1, param_modes)
        self.store(result, 1 if predicate(a, b) else 0)
        self.ip += 4

    def adjust_rb_op(self, param_modes):
        a, = self.resolve_args(1, 0, param_modes)
        self.rb += a
        self.ip += 2

    @staticmethod
    def halt_op(param_modes):
        raise StopIteration

    def run(self):
        ops = {
            1: partial(self.arithmetic_op, add),
            2: partial(self.arithmetic_op, mul),
            3: self.input_op,
            4: self.output_op,
            5: partial(self.jump_op, partial(ne, 0)),
            6: partial(self.jump_op, partial(eq, 0)),
            7: partial(self.test_op, lt),
            8: partial(self.test_op, eq),
            9: self.adjust_rb_op,
            99: self.halt_op,
        }
        try:
            while True:
                op, parameter_modes = self.decode(self.memory[self.ip])
                ops[op](parameter_modes)
        except StopIteration:
            pass
        return self

    def start_in_subprocess(self, in_q=None, out_q=None):
        if in_q is None:
            in_q = Queue()
        if out_q is None:
            out_q = Queue()
        program = self.prepare(in_q.get, out_q.put)
        proc = Process(target=program.run)
        proc.start()
        return proc, in_q, out_q
