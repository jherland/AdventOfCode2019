from intcode import IntCode

with open('05.input') as f:
    program = IntCode.from_file(f)

# part 1
print(program.setup(inputs=[1], outputs=[]).run().outputs.pop())

# part 2
program.setup(inputs=[5]).run()
