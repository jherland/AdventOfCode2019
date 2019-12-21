from intcode import IntCode

with open('09.input') as f:
    program = IntCode.from_file(f)

# part 1
program.setup(inputs=[1]).run()

# part 2
program.setup(inputs=[2]).run()
