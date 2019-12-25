from collections import namedtuple

Coord = namedtuple('Coord', ['x', 'y'])


def parse(f):
    x, y = 0, 0
    for c in f.read():
        if c == '\n':
            x = 0
            y += 1
            continue
        yield Coord(x, y), c == '#'
        x += 1


def adjacents(pos):
    yield Coord(pos.x + 1, pos.y)
    yield Coord(pos.x, pos.y + 1)
    yield Coord(pos.x - 1, pos.y)
    yield Coord(pos.x, pos.y - 1)


def adjacents2(level, pos):
    def top_row(level):
        for i in range(5):
            yield level, Coord(i, 0)

    def bottom_row(level):
        for i in range(5):
            yield level, Coord(i, 4)

    def left_col(level):
        for i in range(5):
            yield level, Coord(0, i)

    def right_col(level):
        for i in range(5):
            yield level, Coord(4, i)

    for a in adjacents(pos):
        if a == Coord(2, 2):
            if pos.y == 1:
                yield from top_row(level + 1)
            elif pos.y == 3:
                yield from bottom_row(level + 1)
            elif pos.x == 1:
                yield from left_col(level + 1)
            elif pos.x == 3:
                yield from right_col(level + 1)
            else:
                raise NotImplementedError
        if a.y == -1:
            yield level - 1, Coord(2, 1)
        elif a.y == 5:
            yield level - 1, Coord(2, 3)
        elif a.x == -1:
            yield level - 1, Coord(1, 2)
        elif a.x == 5:
            yield level - 1, Coord(3, 2)
        else:
            yield level, a


def step_one(pos, world):
    bugs_adjacent = sum(world.get(p, False) for p in adjacents(pos))
    if world[pos]:
        return bugs_adjacent == 1
    else:
        return bugs_adjacent in {1, 2}


def step(world):
    return {pos: step_one(pos, world) for pos in world.keys()}


def new_level():
    return {
        Coord(x, y): False
        for y in range(5) for x in range(5) if (x, y) != (2, 2)
    }


def step2_one(level, pos, worlds):
    bugs_adjacent = sum(
        worlds.get(level, {}).get(p, False)
        for level, p in adjacents2(level, pos))
    if worlds[level][pos]:
        return bugs_adjacent == 1
    else:
        return bugs_adjacent in {1, 2}


def step2_world(level, worlds):
    return {pos: step2_one(level, pos, worlds) for pos in world.keys()}


def step2(worlds):
    worlds = worlds.copy()
    inside = max(worlds.keys()) + 1
    outside = min(worlds.keys()) - 1
    worlds[inside] = new_level()
    worlds[outside] = new_level()
    return {level: step2_world(level, worlds) for level in worlds.keys()}


def bbox(points):
    topleft = Coord(min(p.x for p in points), min(p.y for p in points))
    botright = Coord(max(p.x for p in points), max(p.y for p in points))
    return topleft, botright


def draw(world):
    out = []
    topleft, botright = bbox(world.keys())
    for y in range(topleft.y, botright.y + 1):
        for x in range(topleft.x, botright.x + 1):
            pos = Coord(x, y)
            if pos not in world:
                out.append('?')
            elif world[pos]:
                out.append('#')
            else:
                out.append('.')
        out.append('\n')
    return ''.join(out)


def draw2(worlds):
    for level, world in sorted(worlds.items()):
        print(f'{level}:')
        print(draw(world))


def scan(bbox):
    topleft, botright = bbox
    for y in range(topleft.y, botright.y + 1):
        for x in range(topleft.x, botright.x + 1):
            yield Coord(x, y)


def biodiversity_rating(world):
    total = 0
    for exponent, pos in enumerate(scan(bbox(world))):
        if world[pos]:
            total += pow(2, exponent)
    return total
    return sum(
        pow(2, exp) for exp, pos in enumerate(scan(bbox(world))) if world[pos])


with open('24.input') as f:
    world = dict(parse(f))

# part 1
seen = set()
part1 = world
while draw(part1) not in seen:
    seen.add(draw(part1))
    part1 = step(part1)
print(biodiversity_rating(part1))

# part 2
del world[2, 2]
worlds = {0: world}
for _ in range(200):
    worlds = step2(worlds)
bugs = 0
for level, world in worlds.items():
    bugs += sum(world.values())
print(bugs)
