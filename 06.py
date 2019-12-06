def parse_orbits(f):
    for line in f:
        parent, child = line.rstrip().split(')')
        assert (len(parent), len(child)) == (3, 3)
        yield parent, child


orbits = {}  # map parent -> set of children
parents = {}  # child -> parent

with open('06.input') as f:
    for p, c in parse_orbits(f):
        orbits.setdefault(p, set()).add(c)
        parents[c] = p

depths = {}


def find_depths(parent, depth):
    depths[parent] = depth
    for child in orbits.get(parent, set()):
        find_depths(child, depth + 1)


find_depths('COM', 0)


def up(obj):
    if obj in parents:
        parent = parents[obj]
        yield parent
        yield from up(parent)


# part 1
print(sum(depths.values()))

# part 2
you_to_root = list(up('YOU'))
san_to_root = list(up('SAN'))

print(len(set(you_to_root).symmetric_difference(set(san_to_root))))
