def parse_move(s):
    direction, num_steps = s[0], int(s[1:])
    assert direction in {'U', 'R', 'D', 'L'}
    assert num_steps >= 0
    return direction, num_steps


def parse_wires(f):
    yield from (map(parse_move, line.rstrip().split(',')) for line in f)


def step(pos, dir):
    dx, dy = {'U': (0, +1), 'R': (+1, 0), 'D': (0, -1), 'L': (-1, 0)}[dir]
    return pos[0] + dx, pos[1] + dy


def trace_moves(moves, pos=(0, 0)):
    for d, l in moves:
        for _ in range(l):
            pos = step(pos, d)
            yield pos


def mhdist(p1, p2=(0, 0)):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


with open('03.input') as f:
    w1, w2 = [list(trace_moves(moves)) for moves in parse_wires(f)]
crossings = set(w1) & set(w2)

# part 1
print(min(mhdist(c) for c in crossings))

# part 2
print(min(w1.index(c) + 1 + w2.index(c) + 1 for c in crossings))
