import itertools
from multiprocessing import Queue

from intcode import IntCode


def run_amps(program, phase_setting):
    n = 0
    for p in phase_setting:
        n = program.setup(inputs=[p, n], outputs=[]).run().outputs.pop()
    return n


def run_amps_w_feedback(program, phase_setting):
    n = len(phase_setting)  # How many amps?
    qs = [Queue() for _ in range(n)]  # Queue #i between amps #i-1 and #i
    for i, p in enumerate(phase_setting):
        qs[i].put(p)  # First input to each amp is phase
    qs[0].put(0)  # The first amp take an additional 0 as input
    amps = [
        program.start_in_subprocess(qs[i], qs[(i + 1) % n])[0]
        for i in range(n)
    ]
    for amp in amps:
        amp.join()
    return qs[0].get()


with open('07.input') as f:
    program = IntCode.from_file(f)

# part 1
phase_permutations = itertools.permutations(list(range(5)), 5)
print(max(run_amps(program, phases) for phases in phase_permutations))

# part 2
phase_permutations = itertools.permutations(list(range(5, 10)), 5)
print(max(run_amps_w_feedback(program, p) for p in phase_permutations))
