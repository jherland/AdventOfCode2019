from collections import deque
from dataclasses import dataclass
from pprint import pprint
from string import ascii_uppercase
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


def adjacents(pos):
    """Return coords adjacent to 'pos'."""
    yield pos + Up
    yield pos + Right
    yield pos + Down
    yield pos + Left


@dataclass
class DonutMaze:
    spaces: Dict[Coord, Set[Coord]]  # map coords -> set(adjacent coords)
    labels: Dict[str, Set[Coord]]  # map NN -> spaces adjacent to NN labels

    @staticmethod
    def _raw_parse(f):
        pos = Coord(0, 0)
        for c in f.read():
            if c == '\n':
                pos = Coord(0, pos.y + 1)
                continue
            if c != ' ':
                yield pos, c
            pos += Right

    @classmethod
    def parse(cls, f):
        chars = dict(cls._raw_parse(f))

        def adj_spaces(pos):
            return {p for p in adjacents(pos) if chars.get(p) == '.'}

        # Find open spaces in maze, and their trivial adjacencies
        spaces = {pos: adj_spaces(pos) for pos, c in chars.items() if c == '.'}

        # Identify labels and their adjacent spaces
        label_chars = {pos for pos, c in chars.items() if c in ascii_uppercase}
        labels = {}  # map label name -> adjacent space
        for pos in label_chars:
            near_spaces = adj_spaces(pos)
            if not near_spaces:
                continue
            assert len(near_spaces) == 1
            near = near_spaces.pop()
            label_start = pos - (near - pos)
            label = ''.join(sorted([chars[label_start], chars[pos]]))
            labels.setdefault(label, set()).add(near)

        # Add adjacencies due to labeled jumps
        for label, near in labels.items():
            try:
                a, b = near
            except ValueError:  # Label points to only one space, no jump
                assert len(near) == 1
                continue
            spaces[a].add(b)
            spaces[b].add(a)

        return cls(spaces, labels)

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
        return dist[end]


with open('20.input') as f:
    maze = DonutMaze.parse(f)

# pprint(maze.spaces)
# pprint(maze.labels)
print(maze.shortest_path(maze.labels['AA'].pop(), maze.labels['ZZ'].pop()))
