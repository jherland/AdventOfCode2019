from itertools import product

from intcode import IntCode

with open('02.input') as f:
    program = IntCode.from_file(f)

# part 1
print(program.prepare(noun=12, verb=2).run().memory[0])

# part 2
target = 19690720
for n, v in product(range(100), range(100)):
    if program.prepare(noun=n, verb=v).run().memory[0] == target:
        break
print(100 * n + v)
