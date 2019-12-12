from dataclasses import dataclass
from math import gcd
from typing import NamedTuple


class Coord(NamedTuple):
    x: int = 0
    y: int = 0
    z: int = 0

    def __str__(self):
        return f'({self.x}, {self.y}, {self.z})'

    def __add__(self, other):
        return Coord(self.x + other.x, self.y + other.y, self.z + other.z)


@dataclass(frozen=True)
class Moon:
    pos: Coord
    vel: Coord = Coord()

    @classmethod
    def parse(cls, line):
        xyz = list(map(str.strip, line.strip('<> \n').split(',')))
        assert len(xyz) == 3
        assert xyz[0].startswith('x=')
        assert xyz[1].startswith('y=')
        assert xyz[2].startswith('z=')
        return cls(Coord(*[int(s[2:]) for s in xyz]))

    def __str__(self):
        return f'M[p={self.pos}, v={self.vel}]'

    def apply_gravity(self, others):
        delta = [0, 0, 0]
        for o in others:
            for i in range(3):
                if o.pos[i] > self.pos[i]:
                    delta[i] += 1
                elif o.pos[i] < self.pos[i]:
                    delta[i] -= 1
        return Moon(self.pos, self.vel + Coord(*delta))

    def apply_velocity(self):
        return Moon(self.pos + self.vel, self.vel)

    def potential_energy(self):
        return sum(abs(c) for c in self.pos)

    def kinetic_energy(self):
        return sum(abs(c) for c in self.vel)

    def total_energy(self):
        return self.potential_energy() * self.kinetic_energy()


moons = []
with open('12.input') as f:
    for line in f:
        moons.append(Moon.parse(line))

x_seen = set([tuple((m.pos.x, m.vel.x) for m in moons)])
y_seen = set([tuple((m.pos.y, m.vel.y) for m in moons)])
z_seen = set([tuple((m.pos.z, m.vel.z) for m in moons)])


def step(moons):
    moons = [m.apply_gravity(moons) for m in moons]
    moons = [m.apply_velocity() for m in moons]
    x_seen.add(tuple((m.pos.x, m.vel.x) for m in moons))
    y_seen.add(tuple((m.pos.y, m.vel.y) for m in moons))
    z_seen.add(tuple((m.pos.z, m.vel.z) for m in moons))
    return moons


# part 1
for i in range(1000):
    moons = step(moons)
print(sum(m.total_energy() for m in moons))

# part 2
num_seen = len(x_seen) + len(y_seen) + len(z_seen)
while True:
    moons = step(moons)
    new_seen = len(x_seen) + len(y_seen) + len(z_seen)
    if new_seen == num_seen:
        break
    num_seen = new_seen
periods = (len(x_seen), len(y_seen), len(z_seen))
xyperiod = periods[0] * periods[1] // gcd(periods[0], periods[1])
allperiod = xyperiod * periods[2] // gcd(xyperiod, periods[2])
print(allperiod)
