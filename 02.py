from itertools import product

import intcode

with open('02.input') as f:
    program = intcode.State.parse(f)

# part 1
state = program.clone(12, 2)
print(intcode.run(state).memory[0])

# part 2
target = 19690720
for n, v in product(range(100), range(100)):
    state = program.clone(n, v)
    result = intcode.run(state).memory[0]
    if result == target:
        break
print(100 * n + v)
