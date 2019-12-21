import itertools
from typing import NamedTuple

from intcode import IntCode


class Coord(NamedTuple):
    x: int
    y: int

    def __add__(self, other):
        return Coord(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Coord(self.x - other.x, self.y - other.y)


Up = Coord(0, -1)
Right = Coord(1, 0)
Down = Coord(0, 1)
Left = Coord(-1, 0)


def turn_left(dir):
    return {Up: Left, Left: Down, Down: Right, Right: Up}[dir]


def turn_right(dir):
    return {Up: Right, Right: Down, Down: Left, Left: Up}[dir]


def adjacents(pos):
    """Return coords adjacent to 'pos'."""
    yield pos + Up
    yield pos + Right
    yield pos + Down
    yield pos + Left


class ASCII:
    def __init__(self, program):
        self.program = program
        self.scaffold = set()
        self.robot = (None, None)  # (position, direction)
        self.pos = Coord(0, 0)

        self.program.setup(outputs=self._buildmap).run()

    def _drawmap(self, c):
        print(chr(c), end='')

    def _buildmap(self, c):
        c = chr(c)
        assert c in set('.#\n^>v<X')

        # Find robot:
        if c in set('^>v<X'):
            direction = {'^': Up, '>': Right, 'v': Down, '<': Left, 'X': None}
            self.robot = (self.pos, direction[c])

        # Update scaffold:
        if c in set('#^>v<'):
            self.scaffold.add(self.pos)

        # Update pos:
        if c == '\n':
            self.pos = Coord(0, self.pos.y + 1)
        else:
            self.pos += Right

    def draw(self):
        for y in range(max(pos.y for pos in self.scaffold) + 1):
            for x in range(max(pos.x for pos in self.scaffold) + 1):
                pos = Coord(x, y)
                if pos == self.robot[0]:
                    dir = self.robot[1]
                    c = {Up: '^', Right: '>', Down: 'v', Left: '<'}[dir]
                    print(c, end='')
                elif pos in self.scaffold:
                    print('#', end='')
                else:
                    print(' ', end='')
            print()

    def find_neighbors(self, pos):
        return set(adjacents(pos)) & self.scaffold

    def find_crossings(self):
        for pos in self.scaffold:
            if len(self.find_neighbors(pos)) == 4:
                yield pos

    def find_path(self):
        """Find series of L/R/$num moves to visit all of self.scaffold."""
        pos, dir = self.robot
        been = set()  # where we've already visited
        run = 0  # current number of straigh-ahead moves
        while True:
            been.add(pos)
            if pos + dir in self.scaffold:  # keep going in same direction?
                run += 1
                pos += dir
            else:  # must turn
                if run:
                    yield run
                    run = 0
                neighbors = self.find_neighbors(pos) - been
                assert len(neighbors) <= 1
                if pos + turn_left(dir) in neighbors:
                    yield 'L'
                    dir = turn_left(dir)
                elif pos + turn_right(dir) in neighbors:
                    yield 'R'
                    dir = turn_right(dir)
                else:  # nowhere left to go
                    break

    def execute(self, plan):
        inputs = [ord(c) for c in '\n'.join(plan) + '\nn\n']
        return self.program.setup(inputs, [], mem={0: 2}).run().outputs.pop()


def find_repeated_prefixes(s):
    for n in itertools.count(1):
        if not s[:n] in s[n:]:
            break
    while n > 0:
        n -= 1
        yield s[:n]


def find_plan(path):
    for a in find_repeated_prefixes(path):
        if not a.endswith(','):
            continue
        apath = path.replace(a, 'A,')
        #  print(f'a = {a}, apath = {apath}')
        for b in find_repeated_prefixes(apath.lstrip('A,')):
            if not b.endswith(','):
                continue
            bpath = apath.replace(b, 'B,')
            #  print(f'  b = {b}, bpath = {bpath}')
            for c in find_repeated_prefixes(bpath.lstrip('A,B')):
                if not c.endswith(','):
                    continue
                cpath = bpath.replace(c, 'C,')
                #  print(f'    c = {c}, cpath = {cpath}')
                conditions = [
                    len(cpath.rstrip(',')) <= 20,
                    not (set(cpath) - set('ABC,')),
                    len(a.rstrip(',')) <= 20,
                    not (set(a) & set('ABC')),
                    len(b.rstrip(',')) <= 20,
                    not (set(b) & set('ABC')),
                    len(c.rstrip(',')) <= 20,
                    not (set(c) & set('ABC')),
                ]
                if all(conditions):
                    return [s.rstrip(',') for s in [cpath, a, b, c]]


with open('17.input') as f:
    program = IntCode.from_file(f)

a = ASCII(program)

# part 1
print(sum(pos.x * pos.y for pos in a.find_crossings()))

# part 2
path = ','.join(map(str, a.find_path())) + ','
plan = find_plan(path)
print(a.execute(plan))
