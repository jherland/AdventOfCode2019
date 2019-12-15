from itertools import product

from intcode import IntCode

with open('02.input') as f:
    program = IntCode.from_file(f)

# part 1
print(program.prepare(mem={1: 12, 2: 2}).run().memory[0])

# part 2
target = 19690720
for noun, verb in product(range(100), range(100)):
    if program.prepare(mem={1: noun, 2: verb}).run().memory[0] == target:
        break
print(100 * noun + verb)
