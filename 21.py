from intcode import IntCode

with open('21.input') as f:
    program = IntCode.from_file(f)


def run_script(script):
    def output(i, draw=False):
        if i < 128:
            if draw:
                print(chr(i), end='')
        else:
            print(i)

    assert len(script) <= 15
    program.setup(ascii=script, outputs=output).run()


# part 1
# Jump if any of ABC are holes and D is ground
script = '''
NOT J J
AND A J
AND B J
AND C J
NOT J J
AND D J
WALK
'''
run_script(script.strip().split('\n'))

# part 2
# Jump if the above rules hold, and we can also make another jump from D or E
script = [
    'NOT J J',
    'AND A J',
    'AND B J',
    'AND C J',
    'NOT J J',
    'AND D J',  # J = (!A | !B | !C) & D
    'OR E T',  # can jump from E
    'OR H T',  # can jump from D and land at H
    'AND T J',  # J &= (E | H)
    'RUN',
]
run_script(script)
