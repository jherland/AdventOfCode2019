from itertools import product

import intcode

with open('02.input') as f:
    program = intcode.parse(f)

# part 1
print(intcode.run(program, 12, 2))

# part 2
target = 19690720
for n, v in product(range(100), range(100)):
    result = intcode.run(program, n, v)
    if result == target:
        break
print(100 * n + v)
