import intcode

with open('09.input') as f:
    program = intcode.State.parse(f)

# part 1
state = program.clone(input_=[1].pop)
intcode.run(state)

# part 2
state = program.clone(input_=[2].pop)
intcode.run(state)
