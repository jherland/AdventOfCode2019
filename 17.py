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


def pairwise(seq):
    return zip(seq, seq[1:])


def valid_plan(plan):
    """Check if plan is valid"""
    main, *subs = plan
    if len(','.join(map(str, main))) > 20:
        print(f'main is too long: {len(main)}')
        return False
    if set(main) - {'A', 'B', 'C'}:
        print(f'main is not valid: {main}')
        return False
    for sub in subs:
        if len(','.join(map(str, sub))) > 20:
            print(f'sub is too long: {len(sub)}')
            return False
        if set(sub) - ({'L', 'R'} | set(range(1, 13))):
            print(f'sub is not valid: {sub}')
            return False
    return True


class ASCII:
    def __init__(self, program):
        self.program = program
        self.scaffold = set()
        self.robot = (None, None)  # (position, direction)
        self.pos = Coord(0, 0)

        self.program.prepare(outputs=self._buildmap).run()

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

    def follow(self, start):
        pos, dir = start
        yield start
        been = set()  # where we've already been
        while True:
            been.add(pos)
            next_pos = pos + dir  # try to keep going in same direction
            if next_pos not in self.scaffold:  # oops, must turn
                neighbors = self.find_neighbors(pos) - been
                assert len(neighbors) <= 1
                if not neighbors:  # nowhere left to go
                    break
                next_pos = neighbors.pop()
                dir = next_pos - pos
            pos = next_pos
            yield pos, dir

    def moves(self):
        """Yield L/R/# moves for traversing the scaffolding."""
        run = 0
        traversal = list(self.follow(self.robot))
        for (ppos, pdir), (cpos, cdir) in pairwise(traversal):
            if pdir == cdir:  # keep going in same direction:
                run += 1
            else:
                if run:
                    yield str(run)
                run = 1
                # turn left or right?
                if cdir == turn_left(pdir):
                    yield 'L'
                else:
                    assert cdir == turn_right(pdir)
                    yield 'R'
        yield str(run)

    def traverse(self, plan):
        assert valid_plan(plan)
        planstr = '\n'.join(','.join(map(str, p)) for p in plan) + '\nn\n'
        inputs = [ord(c) for c in planstr]
        return self.program.prepare(inputs, [], mem={0: 2}).run().outputs.pop()

    def score_plan(self, plan):
        """Yield (pos, direction) we've followed the entire scaffold."""
        if not valid_plan(plan):
            return 9999
        pos, dir = self.robot
        uncovered = self.scaffold - {self.robot[0]}
        main, *subs = plan
        for name in main:
            sub = subs[{'A': 0, 'B': 1, 'C': 2}[name]]
            #  print(f' main: {name}: {sub}')
            for instr in sub:
                #  print(f'  sub: {instr}')
                if instr == 'L':
                    dir = turn_left(dir)
                elif instr == 'R':
                    dir = turn_right(dir)
                else:
                    assert isinstance(instr, int)
                    while instr > 0:
                        pos += dir
                        instr -= 1
                        if pos in self.scaffold:
                            uncovered -= {pos}
                        else:
                            self.robot = pos, dir
                            return 1000 + len(uncovered)
        self.robot = pos, dir
        return len(uncovered)


def main_routines():
    """All possible main routines."""
    actions = ['A', 'B', 'C']
    for n in reversed(range(11)):
        yield from itertools.combinations_with_replacement(actions, n)


def sub_routines():
    actions = ['L', 'R', 2, 4, 6, 8, 10, 12]
    for n in range(3, 11):
        yield from itertools.combinations_with_replacement(actions, n)


def plans():
    pass


def count(iter):
    return sum(1 for _ in iter)


with open('17.input') as f:
    program = IntCode.from_file(f)

a = ASCII(program)

# part 1
print(sum(pos.x * pos.y for pos in a.find_crossings()))

# part 2
plan = [
    ['A', 'B', 'A', 'A', 'B', 'C', 'B', 'C', 'C', 'B'],
    ['L', 12, 'R', 8, 'L', 6, 'R', 8, 'L', 6],
    ['R', 8, 'L', 12, 'L', 12, 'R', 8],
    ['L', 6, 'R', 6, 'L', 12],
]
score = a.score_plan(plan)
assert score == 0
print(a.traverse(plan))
