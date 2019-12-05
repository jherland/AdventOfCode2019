import intcode

with open('05.input') as f:
    program = intcode.parse(f)

# part 1
intcode.run(program, input=1)

# part 2
intcode.run(program, input=5)
