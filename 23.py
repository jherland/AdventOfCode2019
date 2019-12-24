from functools import partial
import sys

from intcode import IntCode

with open('23.input') as f:
    program = IntCode.from_file(f)


class NeedInput(Exception):
    def __init__(self, who):
        self.who = who


class HasOutput(Exception):
    def __init__(self, src, dst, x, y):
        self.src = src
        self.dst = dst
        self.x = x
        self.y = y


input_qs = [[i, -1] for i in range(50)]


def on_input(who):
    if not input_qs[who]:
        raise NeedInput(who)
    else:
        return input_qs[who].pop(0)


output_qs = [[] for _ in range(50)]


def on_output(who, what):
    output_qs[who].append(what)
    if len(output_qs[who]) == 3:
        dst, x, y = output_qs[who]
        output_qs[who] = []
        raise HasOutput(who, dst, x, y)


procs = [
    program.setup(partial(on_input, i), partial(on_output, i))
    for i in range(50)
]

print_next = True
prev_x, prev_y = None, None


def nat(x, y):
    global print_next, prev_x, prev_y
    if print_next:
        print(y)
        print_next = False
    prev_x = x
    prev_y = y


last_y = None


def nat_send():
    global last_y
    assert prev_x is not None and prev_y is not None
    if prev_y == last_y:
        print(prev_y)
        sys.exit(0)
    input_qs[0].extend([prev_x, prev_y])
    last_y = prev_y


i = 0
idle = 0
while True:
    try:
        procs[i].run()
    except HasOutput as e:
        idle = 0
        assert e.src == i
        if e.dst == 255:
            nat(e.x, e.y)
        else:
            input_qs[e.dst].extend([e.x, e.y, -1])
    except NeedInput as e:
        idle += 1
        assert e.who == i
    i = (i + 1) % 50
    if all(len(q) == 0 for q in input_qs):
        nat_send()
        idle = 0
