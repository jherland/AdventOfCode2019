from functools import partial


def deal_w_i(inc, deck):
    new = [None] * len(deck)
    for i, card in enumerate(deck):
        new[i * inc % len(deck)] = card
    assert None not in new
    return new


def deal(deck):
    return list(reversed(deck))


def cut(num, deck):
    return deck[num:] + deck[:num]


def parse_instruction(line):
    if line.startswith('deal with increment '):
        return partial(deal_w_i, int(line[20:]))
    elif line == 'deal into new stack':
        return deal
    elif line.startswith('cut '):
        return partial(cut, int(line[4:]))
    else:
        raise NotImplementedError(line)


def parse(f):
    for line in f:
        if line:
            yield parse_instruction(line.strip())


with open('22.input') as f:
    instructions = list(parse(f))

deck = list(range(10007))

# part 1
for instr in instructions:
    deck = instr(deck)
print(deck.index(2019))
