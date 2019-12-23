def parse_instruction(line):
    if line.startswith('deal with increment '):
        return 'deal_w_i', int(line[20:])
    elif line == 'deal into new stack':
        return 'deal',
    elif line.startswith('cut '):
        return 'cut', int(line[4:])
    else:
        raise NotImplementedError(line)


def parse(f):
    for line in f:
        if line:
            yield parse_instruction(line.strip())


def inv(mod, n):
    return pow(n, mod - 2, mod)


def update(mod, off, inc, instr, *arg):
    ops = {
        'deal': lambda: (off - inc, -inc),
        'cut': lambda n: (off + inc * n, inc),
        'deal_w_i': lambda n: (off, inc * inv(mod, n)),
    }
    return tuple(n % mod for n in ops[instr](*arg))


def find_linear_func(mod, instructions):
    off, inc = 0, 1
    for instr in instructions:
        off, inc = update(mod, off, inc, *instr)
    return off, inc


def apply_linear_func_n_times(off, inc, mod, n):
    total_inc = pow(inc, n, mod)
    total_off = off * (1 - total_inc) * inv(mod, 1 - inc)
    return total_off, total_inc


with open('22.input') as f:
    instructions = list(parse(f))

# part 1
deck_size = 10007
card = 2019
off, inc = find_linear_func(deck_size, instructions)
print(((card - off) * inv(deck_size, inc)) % deck_size)

# part 2
deck_size = 119315717514047
instr_times = 101741582076661
pos = 2020
off, inc = find_linear_func(deck_size, instructions)
off, inc = apply_linear_func_n_times(off, inc, deck_size, instr_times)
print((off + pos * inc) % deck_size)
