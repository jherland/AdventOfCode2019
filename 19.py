from itertools import product
from typing import NamedTuple

from intcode import IntCode


class Coord(NamedTuple):
    x: int
    y: int

    def __add__(self, other):
        return Coord(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Coord(self.x - other.x, self.y - other.y)


with open('19.input') as f:
    program = IntCode.from_file(f)

pulled = {}  # map (x, y) -> pulled


def tractor_beam(pos):
    pulled[pos] = program.prepare(list(pos), []).run().outputs.pop() == 1
    return pulled[pos]


def bbox(points):
    xmin = min(p.x for p in points)
    ymin = min(p.y for p in points)
    xmax = max(p.x for p in points)
    ymax = max(p.y for p in points)
    return Coord(xmin, ymin), Coord(xmax, ymax)


def draw():
    topleft, botright = bbox(pulled.keys())
    for y in range(topleft.y - 1, botright.y + 2):
        for x in range(topleft.x - 1, botright.x + 2):
            pos = Coord(x, y)
            if pos not in pulled:
                pixel = ' '
            elif pulled[pos]:
                pixel = '█'
            else:
                pixel = '░'
            print(pixel, end='')
        print()


def walk(pos, delta):
    assert pulled[pos]
    before, after = pos, pos
    length = 1
    while tractor_beam(before - delta):
        before -= delta
        length += 1
    while tractor_beam(after + delta):
        after += delta
        length += 1
    return after, length


def horizontal_walk(pos):
    return walk(pos, Coord(1, 0))


def vertical_walk(pos):
    return walk(pos, Coord(0, 1))


# part 1
print(sum(tractor_beam(Coord(x, y)) for x, y in product(range(50), range(50))))

# part 2
p = max(pos for pos, p in pulled.items() if p)
w = h = 0
while w < 20 and h < 20:
    p, w = horizontal_walk(p)
    p, h = vertical_walk(p)
draw()
