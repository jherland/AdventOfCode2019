from intcode import IntCode

with open('25.input') as f:
    program = IntCode.from_file(f)


def output(i):
    if i < 128:
        print(chr(i), end='')
    else:
        print(i)


program.setup(ascii=input, outputs=output).run()
