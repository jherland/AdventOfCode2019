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


def step1(pos, world):
    bugs_adjacent = sum(world.get(p, False) for p in adjacents(pos))
    if world[pos]:
        return bugs_adjacent == 1
    else:
        return bugs_adjacent in {1, 2}


def step(world):
    return {pos: step1(pos, world) for pos in world.keys()}


def bbox(points):
    topleft = Coord(min(p.x for p in points), min(p.y for p in points))
    botright = Coord(max(p.x for p in points), max(p.y for p in points))
    return topleft, botright


def draw(world):
    out = []
    topleft, botright = bbox(world.keys())
    for y in range(topleft.y, botright.y + 1):
        for x in range(topleft.x, botright.x + 1):
            out.append('#' if world[Coord(x, y)] else '.')
        out.append('\n')
    return ''.join(out)


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

seen = set()
while draw(world) not in seen:
    seen.add(draw(world))
    world = step(world)

#  print(draw(world))
#  print(len(seen))
print(biodiversity_rating(world))
