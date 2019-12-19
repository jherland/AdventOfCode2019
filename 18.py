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


Up = Coord(0, -1)
Right = Coord(1, 0)
Down = Coord(0, 1)
Left = Coord(-1, 0)


class Vault:
    def __init__(
            self,
            spaces: Set[Coord],
            entrance: Coord,
            keys: Dict[str, Coord],
            doors: Dict[str, Coord],
    ):
        self.spaces = spaces
        self.entrance = entrance
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
        entrance = [pos for pos, c in w.items() if c == '@'].pop()
        keys = {c: pos for pos, c in w.items() if c in set(ascii_lowercase)}
        doors = {
            c.lower(): pos
            for pos, c in w.items() if c in set(ascii_uppercase)
        }
        return cls(spaces, entrance, keys, doors)

    def draw(self):
        xmin = min(p.x for p in self.spaces)
        ymin = min(p.y for p in self.spaces)
        xmax = max(p.x for p in self.spaces)
        ymax = max(p.y for p in self.spaces)
        for y in range(ymin - 1, ymax + 2):
            for x in range(xmin - 1, xmax + 2):
                pos = Coord(x, y)
                if pos == self.entrance:
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
        xmin = min(p.x for p in self.spaces)
        ymin = min(p.y for p in self.spaces)
        xmax = max(p.x for p in self.spaces)
        ymax = max(p.y for p in self.spaces)
        for y in range(ymin, ymax + 1):
            for x in range(xmin, xmax + 1):
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
            assert len(dist) == len(self.spaces)
            return dist, prev

        def trace_path(prev, pos):
            assert pos in prev
            while pos in prev:
                yield pos
                pos = prev[pos]

        self._paths = {}
        points = sorted([self.entrance] + list(self.keys.values()))
        all_doors = set(self.doors.values())
        for i, a in enumerate(points):
            dist, prev = dijkstra(a)
            for b in points[i + 1:]:
                assert a < b
                path = set(trace_path(prev, b))
                self._paths[(a, b)] = (len(path), all_doors & path)

    def path(self, a, b, open_doors):
        a, b = min(a, b), max(a, b)
        path_len, doors = self._paths[(a, b)]
        if doors - open_doors:
            return None
        return path_len

    def held_karp(self):
        # Consider subsets S of keys and for key k in S, let D(S, k) be the
        # minimum path length, starting at entrance, visiting all keys in S
        # and finishing at key k. (Automatically exclude paths that traverse
        # doors whose keys have not already been traversed).
        D = {}  # map (tuple(sorted(keys)), k) -> path_len
        allkeys = tuple(sorted(self.keys.keys()))

        # First phase: Make one-element subsets for each key
        for key, pos in self.keys.items():
            path_len = self.path(self.entrance, pos, set())
            if path_len is not None:
                D[((key, ), key)] = path_len

        # Second phase: Grow subsets to encompass all keys
        for subset_size in range(2, len(allkeys) + 1):
            for subset in combinations(allkeys, subset_size):
                #  print(f'subset {subset}')
                assert subset == tuple(sorted(subset))
                for key in subset:
                    # Find shortest path from entrance -> subset -> key
                    prev = tuple(k for k in subset if k != key)
                    opened = {self.doors[k] for k in prev if k in self.doors}
                    #  print(f'  {prev} -> {key}')
                    candidates = []
                    for p in prev:
                        try:
                            prev_len = D[(prev, p)]
                        except KeyError:  # no path
                            continue
                        #  print(f'      path({p}, {key}, {opened})')
                        last = self.path(self.keys[p], self.keys[key], opened)
                        if last is None:
                            continue
                        candidates.append(prev_len + last)
                    #  print(f'    {candidates}')
                    if candidates:
                        D[(subset, key)] = min(candidates)
                        #  print(f'D[{subset}, {key}] = {D[(subset, key)]}')

        # Third phase: Extract the shortest path that visit all keys.
        return min(D[(allkeys, key)] for key in allkeys if (allkeys, key) in D)


with open('18.input') as f:
    vault = Vault.parse(f)

# part 1
# vault.draw()
vault.calculate_all_paths()
# print(len(vault._paths))
print(vault.held_karp())
