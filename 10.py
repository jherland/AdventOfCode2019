from collections import namedtuple
from functools import partial
from math import atan2, tau

Point = namedtuple('Point', ['x', 'y'])


def parse(s):
    for y, line in enumerate(s.split('\n')):
        for x, c in enumerate(line):
            if c == '#':
                yield Point(x, y)


def dist(p1, p2):
    # manhattan distance is good enough for ordering purposes
    return abs(p2.y - p1.y) + abs(p2.x - p1.x)


def angle(p1, p2):
    # want angle in CW direction, with "up" (-y) as 0 => flip x and -y coords
    return atan2(p2.x - p1.x, p1.y - p2.y) % tau


with open('10.input') as f:
    points = set(parse(f.read()))

all_angles = {p1: {angle(p1, p2) for p2 in points - {p1}} for p1 in points}
station, angles = max(all_angles.items(), key=lambda kv: len(kv[1]))

# part 1
print(len(angles))

# part 2
angle200 = sorted(angles)[199]
aim_at = {p for p in points - {station} if angle(station, p) == angle200}
casualty = min(aim_at, key=partial(dist, station))
print(casualty.x * 100 + casualty.y)
