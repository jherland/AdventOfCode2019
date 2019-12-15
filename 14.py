from collections import defaultdict, namedtuple
from math import ceil

Chemical = namedtuple('Chemical', ['amount', 'unit'])
Reaction = namedtuple('Reaction', ['ins', 'out'])


def parse(f):
    def parsechem(s):
        amount, unit = s.strip().split(' ')
        return Chemical(int(amount), unit)

    for line in f:
        ins, out = line.split('=>')
        yield Reaction({parsechem(i) for i in ins.split(',')}, parsechem(out))


with open('14.input') as f:
    reactions = {r.out.unit: r for r in parse(f)}  # map unit -> Reaction

distances = {'ORE': 0}  # sort units by max reaction distance from ORE
while len(distances) <= len(reactions):
    for unit in set(reactions.keys()) - set(distances.keys()):
        input_units = (i.unit for i in reactions[unit].ins)
        try:
            distances[unit] = max(distances[iu] for iu in input_units) + 1
        except KeyError:
            pass


def ore_needed(fuel):
    needed = defaultdict(int)
    needed['FUEL'] = fuel
    while needed:
        unit = max(needed.keys(), key=lambda k: distances[k])
        amount = needed[unit]
        if unit == 'ORE':
            return amount
        del needed[unit]
        instances = ceil(amount / reactions[unit].out.amount)
        for i in reactions[unit].ins:
            needed[i.unit] += i.amount * instances


def bsearch(lo, hi, too_high):
    mid = lo
    while hi > lo + 1:
        mid = lo + (hi - lo) // 2
        if too_high(mid):
            hi = mid
        else:
            lo = mid
    return mid


# part 1
print(ore_needed(1))

# part 2
ore = 1000000000000
print(bsearch(1, ore, lambda fuel: ore_needed(fuel) > ore))
