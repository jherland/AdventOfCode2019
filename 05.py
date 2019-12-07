import intcode

with open('05.input') as f:
    program = intcode.State.parse(f)

# part 1
state = program.clone(input_=lambda: 1)
intcode.run(state)

# part 2
state = program.clone(input_=lambda: 5)
intcode.run(state)
