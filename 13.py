from functools import partial
from time import sleep

from intcode import IntCode


class Game:
    Tiles = [' ', '#', '█', '-', 'O']

    def __init__(self):
        self.tiles = {}  # (x, y) -> tile
        self.score = 0
        self.ball = 0  # x coord of ball
        self.paddle = 0  # x coord of paddle
        self._buffer = []

    def set_tile(self, x, y, tile):
        if x == -1 and y == 0:
            self.score = tile
        else:
            assert x >= 0 and y >= 0 and tile in range(5)
            self.tiles[(x, y)] = tile
            if tile == 3:
                self.paddle = x
            elif tile == 4:
                self.ball = x

    def size(self):
        return tuple(max(i) for i in zip(*self.tiles.keys()))

    def draw(self):
        w, h = self.size()
        print(f'Score: {self.score}')
        for y in range(h):
            for x in range(w):
                print(self.Tiles[self.tiles.get((x, y), 0)], end='')
            print('#')

    def buffer(self, n):
        self._buffer.append(n)
        if len(self._buffer) == 3:
            self.set_tile(*self._buffer)
            self._buffer = []

    def interact(self, draw):
        if draw:
            self.draw()
            sleep(0.02)
        if self.ball < self.paddle:
            return -1
        elif self.ball > self.paddle:
            return 1
        else:
            return 0

    def run(self, program, draw=True):
        program.setup(partial(self.interact, draw), self.buffer).run()


with open('13.input') as f:
    program = IntCode.from_file(f)

# part 1
game = Game()
game.run(program)
print(sum(map(lambda t: t == 2, game.tiles.values())))

# part 2
game = Game()
game.run(program.setup(mem={0: 2}), draw=False)
print(game.score)
