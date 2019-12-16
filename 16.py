from array import array
from itertools import chain, cycle, islice, repeat


def fft(digits, offset=0, length=8, repeats=1):
    width = len(digits) * repeats
    rows = [array('b', islice(cycle([int(d) for d in digits]), width))]
    rows += [array('b', repeat(-1, width)) for _ in range(100)]
    for y in range(100):  # fill in rightmost column
        rows[y + 1][-1] = rows[y][-1]
    rowfill = [0] + [width - 1] * 100

    def fft_pattern(reps):
        pattern = chain.from_iterable(repeat(d, reps) for d in [0, 1, 0, -1])
        return islice(cycle(pattern), 1, width + 1)

    def fft_digit_slow(depth, i):
        total = sum(
            fft_digit(depth - 1, j) * p
            for j, p in enumerate(fft_pattern(i + 1)) if p)
        return abs(total) % 10

    def fft_digit_fast(depth, i):
        assert i >= width / 2
        if rowfill[depth - 1] > i:
            fft_digit_fast(depth - 1, i)  # compute row above
        for j in reversed(range(i, rowfill[depth])):
            total = rows[depth][j + 1] + rows[depth - 1][j]
            rows[depth][j] = abs(total) % 10
        rowfill[depth] = i
        return rows[depth][i]

    def fft_digit(depth, i):
        result = rows[depth][i]
        if result >= 0:
            return result
        else:
            assert depth > 0 and i < rowfill[depth]
        if i >= width / 2:  # In the right half
            return fft_digit_fast(depth, i)
        else:
            rows[depth][i] = fft_digit_slow(depth, i)
            return rows[depth][i]

    return [fft_digit(100, i) for i in range(offset, offset + length)]


with open('16.input') as f:
    digits = f.read().rstrip()

# part 1
print(''.join(str(d) for d in fft(digits)))

# part 2
offset = int(digits[:7])
print(''.join(str(d) for d in fft(digits, offset=offset, repeats=10000)))
