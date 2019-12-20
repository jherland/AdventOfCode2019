from collections import deque
from dataclasses import dataclass
from string import ascii_uppercase
from typing import Dict, NamedTuple, Optional, Set, Tuple


class Coord(NamedTuple):
    x: int
    y: int
    z: int

    def __add__(self, other):
        return Coord(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Coord(self.x - other.x, self.y - other.y, self.z - other.z)


Up = Coord(0, -1, 0)
Right = Coord(1, 0, 0)
Down = Coord(0, 1, 0)
Left = Coord(-1, 0, 0)


def adjacents(pos):
    """Return coords adjacent to 'pos'."""
    yield pos + Up
    yield pos + Right
    yield pos + Down
    yield pos + Left


def bbox(points):
    xmin = min(p.x for p in points)
    ymin = min(p.y for p in points)
    zmin = min(p.z for p in points)
    xmax = max(p.x for p in points)
    ymax = max(p.y for p in points)
    zmax = max(p.z for p in points)
    return Coord(xmin, ymin, zmin), Coord(xmax, ymax, zmax)


@dataclass
class DonutMaze:
    spaces: Dict[Coord, Set[Coord]]  # map: coords -> set(adjacent coords)
    # map: z -> label -> (outer, inner or None)
    labels: Dict[int, Dict[str, Tuple[Optional[Coord]]]]

    @staticmethod
    def _raw_parse(f, z=0):
        pos = Coord(0, 0, z)
        for c in f.read():
            if c == '\n':
                pos = Coord(0, pos.y + 1, z)
                continue
            if c != ' ':
                yield pos, c
            pos += Right

    @classmethod
    def parse(cls, f, z=0):
        chars = dict(cls._raw_parse(f, z))

        def adj_spaces(pos):
            return {p for p in adjacents(pos) if chars.get(p) == '.'}

        # Find open spaces in maze, and their trivial adjacencies
        spaces = {pos: adj_spaces(pos) for pos, c in chars.items() if c == '.'}
        tl, br = bbox(spaces)

        def on_edge(pos):
            return pos.x in {tl.x, br.x} or pos.y in {tl.y, br.y}

        # Identify labels and their adjacent spaces
        label_chars = {pos for pos, c in chars.items() if c in ascii_uppercase}
        labels = {}  # map label name -> adjacent space
        for pos in label_chars:
            near_spaces = adj_spaces(pos)
            if not near_spaces:
                continue
            assert len(near_spaces) == 1
            near = near_spaces.pop()
            other_char = pos - (near - pos)
            label = ''.join(sorted([chars[other_char], chars[pos]]))
            outer, inner = labels.get(label, (None, None))
            if on_edge(near):
                labels[label] = (near, inner)
            else:
                labels[label] = (outer, near)

        return cls(spaces, {z: labels})

    def clone(self, z=0):
        return DonutMaze(
            {
                Coord(pos.x, pos.y, z): {Coord(a.x, a.y, z) for a in adj}
                for pos, adj in self.spaces.items()
            },
            {
                z: {
                    label: (
                        Coord(outer.x, outer.y, z),
                        Coord(inner.x, inner.y, z) if inner else None,
                    )
                    for label, (outer, inner) in self.labels[0].items()
                }
            },
        )

    def merge(self, other):
        assert not set(self.spaces.keys()) & set(other.spaces.keys())
        self.spaces.update(other.spaces)
        assert len(other.labels) == 1
        other_level, = other.labels.keys()
        assert other_level not in self.labels
        self.labels.update(other.labels)

    def dijkstra(self, start):
        dist = {start: 0}
        prev = {}
        process = deque([start])
        while process:
            cur = process.popleft()
            d = dist[cur]
            for a in self.spaces[cur]:
                if a in dist:
                    assert dist[a] <= d + 1
                else:
                    dist[a] = d + 1
                    prev[a] = cur
                    process.append(a)
        return dist, prev

    def shortest_path(self, start, end):
        dist, _ = self.dijkstra(start)
        try:
            return dist[end]
        except KeyError:
            return None


with open('20.input') as f:
    maze = DonutMaze.parse(f)

# part 1
part1 = maze.clone()
# Add all jumps as adjacencies
for label, (outer, inner) in part1.labels[0].items():
    assert outer is not None
    if inner is None:
        assert label in {'AA', 'ZZ'}
    else:
        part1.spaces[outer].add(inner)
        part1.spaces[inner].add(outer)

print(part1.shortest_path(maze.labels[0]['AA'][0], maze.labels[0]['ZZ'][0]))

# part 2
part2 = maze.clone()
for level in range(25):
    part2.merge(maze.clone(level + 1))
    # Connect all inner ports at level to outer ports at level + 1
    for label in part2.labels[level].keys():
        if label in {'AA', 'ZZ'}:
            continue
        _, inner = part2.labels[level][label]
        outer, _ = part2.labels[level + 1][label]
        part2.spaces[outer].add(inner)
        part2.spaces[inner].add(outer)

print(part2.shortest_path(maze.labels[0]['AA'][0], maze.labels[0]['ZZ'][0]))
