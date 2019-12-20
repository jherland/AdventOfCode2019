from collections import deque
from itertools import combinations
from string import ascii_lowercase, ascii_uppercase
from typing import Dict, NamedTuple, Set


class Coord(NamedTuple):
    x: int
    y: int

    def __add__(self, other):
        return Coord(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Coord(self.x - other.x, self.y - other.y)

    def __floordiv__(self, denom):
        assert isinstance(denom, int)
        return Coord(self.x // 2, self.y // 2)


Up = Coord(0, -1)
Right = Coord(1, 0)
Down = Coord(0, 1)
Left = Coord(-1, 0)


class Vault:
    def __init__(
            self,
            spaces: Set[Coord],
            entrances: Set[Coord],
            keys: Dict[str, Coord],
            doors: Dict[str, Coord],
    ):
        self.spaces = spaces
        self.entrances = entrances
        self.keys = keys
        self.doors = doors
        self._paths = None

    @staticmethod
    def world(f):
        pos = Coord(0, 0)
        for c in f.read():
            if c == '\n':
                pos = Coord(0, pos.y + 1)
                continue
            yield pos, c
            pos += Right

    @classmethod
    def parse(cls, f):
        w = dict(cls.world(f))
        spaces = {pos for pos, c in w.items() if c != '#'}
        entrances = {pos for pos, c in w.items() if c == '@'}
        keys = {c: pos for pos, c in w.items() if c in set(ascii_lowercase)}
        doors = {
            c.lower(): pos
            for pos, c in w.items() if c in set(ascii_uppercase)
        }
        return cls(spaces, entrances, keys, doors)

    def bbox(self):
        xmin = min(p.x for p in self.spaces)
        ymin = min(p.y for p in self.spaces)
        xmax = max(p.x for p in self.spaces)
        ymax = max(p.y for p in self.spaces)
        return Coord(xmin, ymin), Coord(xmax, ymax)

    def draw(self):
        topleft, botright = self.bbox()
        for y in range(topleft.y - 1, botright.y + 2):
            for x in range(topleft.x - 1, botright.x + 2):
                pos = Coord(x, y)
                if pos in self.entrances:
                    pixel = '@'
                elif pos not in self.spaces:
                    pixel = '█'
                else:
                    objects = [k for k, p in self.keys.items() if p == pos]
                    objects += [
                        k.upper() for k, p in self.doors.items() if p == pos
                    ]
                    if len(objects):
                        pixel = objects.pop()
                    else:
                        pixel = ' '
                print(pixel * 2, end='')
            print()

    def calculate_all_paths(self):
        adjacent = {}  # map pos -> set(adjacent pos)
        topleft, botright = self.bbox()
        for y in range(topleft.y, botright.y + 1):
            for x in range(topleft.x, botright.x + 1):
                pos = Coord(x, y)
                if pos in self.spaces:
                    adj = {pos + Up, pos + Right, pos + Down, pos + Left}
                    adjacent[pos] = adj & self.spaces

        def dijkstra(start):
            dist = {start: 0}
            prev = {}
            process = deque([start])
            while process:
                cur = process.popleft()
                d = dist[cur]
                for a in adjacent[cur]:
                    if a in dist:
                        assert dist[a] <= d + 1
                    else:
                        dist[a] = d + 1
                        prev[a] = cur
                        process.append(a)
            return dist, prev

        def trace_path(prev, pos):
            if pos not in prev:
                raise ValueError(f'Cannot reach {pos}')
            while pos in prev:
                yield pos
                pos = prev[pos]

        self._paths = {}
        points = sorted(self.entrances | set(self.keys.values()))
        all_doors = set(self.doors.values())
        for i, a in enumerate(points):
            dist, prev = dijkstra(a)
            for b in points[i + 1:]:
                assert a < b
                try:
                    path = set(trace_path(prev, b))
                    self._paths[(a, b)] = (len(path), all_doors & path)
                except ValueError:
                    pass

    def path(self, a, b, open_doors):
        a, b = min(a, b), max(a, b)
        path_len, doors = self._paths[(a, b)]
        if doors - open_doors:
            return None
        return path_len

    def held_karp(self, start, keys, doors):
        # Consider subsets S of keys and for key k in S, let D(S, k) be the
        # minimum path length from start, visiting all keys in S and finishing
        # at key k. (Automatically exclude paths that traverse doors whose keys
        # have not already been traversed).
        D = {}  # map (tuple(sorted(keys)), k) -> path_len
        allkeys = tuple(sorted(keys.keys()))
        skipdoors = set(self.doors.values()) - set(doors.values())

        # First phase: Make one-element subsets for each key
        for key, pos in keys.items():
            path_len = self.path(start, pos, skipdoors)
            if path_len is not None:
                D[((key, ), key)] = path_len

        # Second phase: Grow subsets to encompass all keys
        for subset_size in range(2, len(allkeys) + 1):
            for subset in combinations(allkeys, subset_size):
                assert subset == tuple(sorted(subset))
                for key in subset:
                    # Find shortest path from entrance -> subset -> key
                    prev = tuple(k for k in subset if k != key)
                    opened = {doors[k] for k in prev if k in doors} | skipdoors
                    candidates = []
                    for p in prev:
                        try:
                            prev_len = D[(prev, p)]
                        except KeyError:  # no path
                            continue
                        last = self.path(keys[p], keys[key], opened)
                        if last is None:
                            continue
                        candidates.append(prev_len + last)
                    if candidates:
                        D[(subset, key)] = min(candidates)

        # Third phase: Extract the shortest path that visit all keys.
        return min(D[(allkeys, key)] for key in allkeys if (allkeys, key) in D)


with open('18.input') as f:
    vault = Vault.parse(f)

# part 1
# vault.draw()
vault.calculate_all_paths()
print(vault.held_karp(next(iter(vault.entrances)), vault.keys, vault.doors))

# part 2
pos = vault.entrances.pop()
for p in [pos, pos + Up, pos + Right, pos + Down, pos + Left]:
    vault.spaces.discard(p)
vault.entrances = {
    pos + Up + Left, pos + Up + Right, pos + Down + Left, pos + Down + Right
}
# vault.draw()
vault.calculate_all_paths()
topleft, botright = vault.bbox()
center = topleft + (botright - topleft) // 2
total_len = 0
quadrants = [
    lambda pos: pos.x < center.x and pos.y < center.y,  # upper left
    lambda pos: pos.x > center.x and pos.y < center.y,  # upper right
    lambda pos: pos.x < center.x and pos.y > center.y,  # lower left
    lambda pos: pos.x > center.x and pos.y > center.y,  # lower right
]
for quadrant in quadrants:
    entrance = [e for e in vault.entrances if quadrant(e)].pop()
    keys = {key: pos for key, pos in vault.keys.items() if quadrant(pos)}
    # Only consider doors whose keys are in the same quadrant. Assume other
    # doors will be unlocked by other robots
    doors = {
        door: pos
        for door, pos in vault.doors.items() if quadrant(pos) and door in keys
    }
    path_len = vault.held_karp(entrance, keys, doors)
    total_len += path_len
print(total_len)
