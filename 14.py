from dataclasses import dataclass
from math import ceil
from typing import Set


@dataclass(order=True, frozen=True)
class Chemical:
    unit: str
    quantity: int

    def __str__(self):
        return f'{self.quantity} {self.unit}'

    def __hash__(self):
        return hash(self.unit)  # DON'T INCLUDE QUANTITY

    def __add__(self, other):
        assert other.unit == self.unit
        return Chemical(self.unit, self.quantity + other.quantity)

    def __sub__(self, other):
        assert other.unit == self.unit
        assert other.quantity <= self.quantity
        return Chemical(self.unit, self.quantity - other.quantity)

    def __mul__(self, num):
        assert isinstance(num, int)
        return Chemical(self.unit, self.quantity * num)

    @classmethod
    def parse(cls, s):
        quantity, unit = s.split(' ')
        return cls(unit, int(quantity))


@dataclass
class Reaction:
    makes: Chemical
    needs: Set[Chemical]

    def __str__(self):
        return f'{self.makes} <= ' + ', '.join(map(str, self.needs))

    @classmethod
    def parse(cls, line):
        needs, makes = line.rstrip().split(' => ')
        needs = needs.split(', ')
        return cls(Chemical.parse(makes), {Chemical.parse(n) for n in needs})

    def takes(self, unit):
        return any(unit == c.unit for c in self.needs)

    def instances(self, chemical):
        """How many instances of this are needed to make the given quantity"""
        assert chemical.unit == self.makes.unit
        return ceil(chemical.quantity / self.makes.quantity)

    def ingredients(self, instances):
        """Return the ingredients needed to make the given chemical"""
        return {ingr * instances for ingr in self.needs}


class Factory:
    def __init__(self, reactions, *initial_ingredients):
        self.reactions = reactions
        self.vat = {}  # map unit -> Chemical
        for chemical in initial_ingredients:
            self.add(chemical)

    def __str__(self):
        return ', '.join(map(str, self.vat.values()))

    def __getitem__(self, unit):
        return self.vat.get(unit, Chemical(unit, 0))

    def add(self, chemical):
        self.vat[chemical.unit] = self[chemical.unit] + chemical

    def take(self, chemical):
        #  print(f'  take({chemical}) from {self}')
        while self[chemical.unit] < chemical:  # must produce
            need = chemical - self[chemical.unit]
            #  half = Chemical(need.unit, ceil(need.quantity * 9 / 10))
            self.produce(need)
        self.vat[chemical.unit] -= chemical
        if self.vat[chemical.unit].quantity == 0:
            del self.vat[chemical.unit]
        return chemical

    def produce(self, chemical):
        #  print(f'  produce({chemical}) from {self}')
        reaction = self.reactions[chemical.unit]
        instances = reaction.instances(chemical)
        taken = set()
        try:
            for ingredient in reaction.ingredients(instances):
                taken.add(self.take(ingredient))
        except KeyError:  # Not enough ingredients
            for ingredient in taken:
                self.add(ingredient)
            raise
        self.add(reaction.makes * instances)


def parse(f):
    for line in f:
        r = Reaction.parse(line)
        yield r.makes.unit, r


with open('14.input') as f:
    reactions = dict(parse(f))

# part 1
init_ore = Chemical('ORE', 1000000000000)
f = Factory(reactions, init_ore)
fuel = f.take(Chemical('FUEL', 1))
print(init_ore - f['ORE'])

# part 2
try:
    while fuel < Chemical('FUEL', 2000000):
        fuel += f.take(Chemical('FUEL', 10000))
except KeyError:
    pass
try:
    while fuel < Chemical('FUEL', 2800000):
        fuel += f.take(Chemical('FUEL', 100))
except KeyError:
    pass
try:
    while True:
        fuel += f.take(Chemical('FUEL', 1))
except KeyError:
    pass
print(fuel)
