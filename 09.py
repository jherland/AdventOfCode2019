from intcode import IntCode

with open('09.input') as f:
    program = IntCode.from_file(f)

# part 1
program.prepare(inputs=[1]).run()

# part 2
program.prepare(inputs=[2]).run()
