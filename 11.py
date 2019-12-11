from collections import defaultdict, namedtuple
from dataclasses import dataclass
import queue

from intcode import IntCode

Point = namedtuple('Point', ['x', 'y'])


@dataclass
class Robot:
    pos: Point = Point(0, 0)
    dir: Point = Point(0, 1)  # facing up

    def turn(self, lr):
        self.dir = {
            Point(0, 1): [Point(-1, 0), Point(1, 0)],
            Point(1, 0): [Point(0, 1), Point(0, -1)],
            Point(0, -1): [Point(1, 0), Point(-1, 0)],
            Point(-1, 0): [Point(0, -1), Point(0, 1)],
        }[self.dir][lr]

    def move(self):
        self.pos = Point(self.pos.x + self.dir.x, self.pos.y + self.dir.y)


def paint_hull(program, start_color=0):
    robot = Robot()
    hull = defaultdict(int)  # map points -> color: 0 for black, 1 for white
    hull[robot.pos] = start_color
    proc, in_q, out_q = program.start_in_subprocess()
    try:
        while True:
            in_q.put(hull[robot.pos])
            hull[robot.pos] = out_q.get(timeout=1)
            robot.turn(out_q.get(timeout=1))
            robot.move()
    except queue.Empty:
        proc.join()
    return hull


def bbox(pixels):
    x_min, x_max, y_min, y_max = None, None, None, None
    for p in pixels:
        if x_min is None or p.x < x_min:
            x_min = p.x
        if x_max is None or p.x > x_max:
            x_max = p.x
        if y_min is None or p.y < y_min:
            y_min = p.y
        if y_max is None or p.y > y_max:
            y_max = p.y
    return Point(x_min, y_min), Point(x_max, y_max)


def draw(pixels):
    botleft, topright = bbox(pixels)
    for y in range(topright.y, botleft.y - 1, -1):
        for x in range(botleft.x, topright.x + 1):
            print('██' if Point(x, y) in pixels else '  ', end='')
        print()


with open('11.input') as f:
    program = IntCode.from_file(f)

# part 1
hull = paint_hull(program)
print(len(hull))

# part 2
hull = paint_hull(program, 1)
white_pixels = {p for p, c in hull.items() if c}
draw(white_pixels)
