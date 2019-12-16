from collections import namedtuple
from itertools import chain
from time import sleep
import sys

from intcode import IntCode

Coord = namedtuple('Coord', ['x', 'y'])
Open, Wall, Oxygen = 0, 1, 2


def bbox(coords):
    xmin = xmax = ymin = ymax = 0
    for coord in coords:
        if coord is None:
            continue
        x, y = coord
        xmin, xmax = min(xmin, x), max(xmax, x)
        ymin, ymax = min(ymin, y), max(ymax, y)
    return Coord(xmin, ymin), Coord(xmax, ymax)


def draw(world, droid, target):
    def pixel(coord):
        if coord == droid:
            return '\u001b[33;1m()\u001b[0m'
        elif coord == target:
            return '\u001b[31;1m()\u001b[0m'
        elif coord not in world:  # unexplored
            return '  '
        elif world[coord] == Wall:
            return '\u001b[30;1m░░\u001b[0m'
        elif world[coord] == Open:
            return '\u001b[34m██\u001b[0m'
        elif world[coord] == Oxygen:
            return '\u001b[34;1m██\u001b[0m'
        else:
            raise NotImplementedError()

    (xmin, ymin), (xmax, ymax) = bbox(
        list(world.keys()) + [droid, target, (-10, -10), (10, 10)])
    for y in range(ymin, ymax + 1):
        for x in range(xmin, xmax + 1):
            print(pixel((x, y)), end='')
        print()
    print()
    sys.stdout.flush()


def neighbors(pos):
    return {
        1: Coord(pos.x, pos.y - 1),  # north
        2: Coord(pos.x, pos.y + 1),  # south
        3: Coord(pos.x - 1, pos.y),  # west
        4: Coord(pos.x + 1, pos.y),  # east
    }


class FoundTarget(Exception):
    pass


class Explorer:
    def __init__(self, draw=False):
        self._draw = draw
        self.droid = Coord(0, 0)
        self.target = None  # unknown
        self.world = {self.droid: Open}  # (x, y) -> Open/Wall/Oxygen
        self.dir = None
        self.breadcrumbs = []  # directions from start to current droid pos

    def draw(self, override=True):
        if self._draw or override:
            draw(self.world, self.droid, self.target)
            sleep(0.01)

    def next_step(self):
        self.draw(False)
        self.backtrack = False  # explore
        for d, pos in neighbors(self.droid).items():
            if pos not in self.world:
                self.dir = d
                return self.dir

        self.backtrack = True  # backtrack
        opposite = {1: 2, 2: 1, 3: 4, 4: 3}
        self.dir = opposite[self.breadcrumbs.pop()]
        return self.dir

    def next_result(self, status):
        pos = neighbors(self.droid)[self.dir]
        if status == 0:  # hit a wall
            self.world[pos] = Wall
        else:  # moved one step
            self.world[pos] = Open
            self.droid = pos
            if not self.backtrack:
                self.breadcrumbs.append(self.dir)
            if status == 2 and self.target is None:  # found target
                self.target = pos
                raise FoundTarget(self.target)

    def explore(self, program):
        p = program.prepare(inputs=self.next_step, outputs=self.next_result)
        try:
            p.run()  # explore to find target
        except FoundTarget:
            ret = self.target, self.breadcrumbs[:]
        try:
            p.run()  # explore the rest of the maze
        except IndexError:  # done
            pass
        return ret

    def spread_oxygen(self):
        self.world[self.target] = Oxygen  # start spreading from self.target
        oxygenated = {self.target}
        remaining = {pos for pos, state in self.world.items() if state == Open}
        steps = 0
        while remaining:
            adjacent = chain(*[neighbors(pos).values() for pos in oxygenated])
            spread = remaining.intersection(adjacent)
            oxygenated |= spread
            remaining -= spread
            for pos in spread:
                self.world[pos] = Oxygen
            steps += 1
            self.draw(False)
        return steps


with open('15.input') as f:
    program = IntCode.from_file(f)

explorer = Explorer(draw=False)
target, path = explorer.explore(program)

# part 1
print(len(path))

# part 2
print(explorer.spread_oxygen())
