parents = {}  # child -> parent

with open('06.input') as f:
    for line in f:
        parent, child = line.rstrip().split(')')
        parents[child] = parent


def to_root(obj):
    if obj in parents:
        parent = parents[obj]
        yield parent
        yield from to_root(parent)


# part 1
print(sum(len(list(to_root(obj))) for obj in parents.keys()))

# part 2
print(len(set(to_root('YOU')).symmetric_difference(set(to_root('SAN')))))
