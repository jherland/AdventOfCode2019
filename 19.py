from functools import partial
from itertools import product
from typing import NamedTuple

from intcode import IntCode

with open('19.input') as f:
    program = IntCode.from_file(f)

pulled = {}  # map (x, y) -> pulled


class Coord(NamedTuple):
    x: int
    y: int

    def __add__(self, other):
        return Coord(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Coord(self.x - other.x, self.y - other.y)

    def __floordiv__(self, denom):
        assert isinstance(denom, int)
        return Coord(self.x // denom, self.y // denom)


def tractor_beam(pos):
    if pos not in pulled:
        pulled[pos] = program.setup(list(pos), []).run().outputs.pop() == 1
    return pulled[pos]


def find_bbox(points):
    xmin = min(p.x for p in points)
    ymin = min(p.y for p in points)
    xmax = max(p.x for p in points)
    ymax = max(p.y for p in points)
    return Coord(xmin, ymin), Coord(xmax, ymax)


def draw(*highlights, bbox=None):
    highlights = set(highlights)
    topleft, botright = find_bbox(pulled.keys()) if bbox is None else bbox
    for y in range(topleft.y, botright.y + 1):
        for x in range(topleft.x, botright.x + 1):
            pos = Coord(x, y)
            if pos not in pulled:
                pixel = ' '
            elif pulled[pos]:
                pixel = '█'
            else:
                pixel = '░'
            if pos in highlights:
                pixel = f'\u001b[33;1m{pixel}\u001b[0m'
            print(pixel, end='')
        print()


def find_first(pos, adjust, pred):
    """Binary search pos, and find where pred goes from False to True"""
    lo = pos
    while not pred(pos):
        lo = pos
        n = adjust(pos + pos)
        pos = n
    # pred goes from False to True between lo and pos, binary search:
    hi = pos
    while True:
        pos = adjust(lo + (hi - lo) // 2)
        if pos in {lo, hi}:
            return hi
        if pred(pos):
            hi = pos
        else:
            lo = pos


def probe(pos, delta):
    """Return last pos in delta direction that is still within beam.

    If pos if not within beam, return first pos in -delta direction that is
    within beam.
    """
    if tractor_beam(pos):
        while tractor_beam(pos + delta):
            pos += delta
    else:
        while not tractor_beam(pos - delta):
            pos -= delta
        pos -= delta
    return pos


def adjust_bl(pos):
    pos = probe(pos, Coord(-1, 0))
    pos = probe(pos, Coord(0, 1))
    return pos


def square_within(square, bl):
    assert tractor_beam(bl)
    result = tractor_beam(Coord(bl.x + square - 1, bl.y + 1 - square))
    # draw(bl)
    return result


def square_corners(square, bl):
    return [
        Coord(bl.x, bl.y + 1 - square),  # top left
        Coord(bl.x + square - 1, bl.y + 1 - square),  # top right
        bl,  # bottom left
        Coord(bl.x + square - 1, bl.y),  # bottom right
    ]


# part 1
print(sum(tractor_beam(Coord(x, y)) for x, y in product(range(50), range(50))))

# part 2
square = 100
bl = max(pos for pos, p in pulled.items() if p)
bl = find_first(bl, adjust_bl, partial(square_within, square))
tl, tr, bl, br = square_corners(square, bl)
for corner in [tl, tr, bl, br]:
    assert tractor_beam(corner)
assert not (tractor_beam(bl + Coord(-1, 0)) and tractor_beam(bl + Coord(0, 1)))
assert not (tractor_beam(tr + Coord(1, 0)) and tractor_beam(tr + Coord(0, -1)))
print(tl.x * 10000 + tl.y)
