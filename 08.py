from collections import Counter
from pathlib import Path

data = Path('08.input').read_text().rstrip()
w, h = 25, 6
layers = [data[i:i + w * h] for i in range(0, len(data), w * h)]

# part 1
fewest0 = min(map(Counter, layers), key=lambda c: c['0'])
print(fewest0['1'] * fewest0['2'])


# part 2
def merge(layers, transp='2'):
    for pixels in zip(*layers):
        yield next(filter(lambda p: p != transp, pixels))


def render(w, h, img, pixelmap={'0': '  ', '1': '██'}):
    for y in range(h):
        print(''.join([pixelmap[p] for p in img[w * y:w * (y + 1)]]))


merged = render(w, h, list(merge(layers)))
