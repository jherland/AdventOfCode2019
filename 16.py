from itertools import chain, cycle, islice, repeat


def fft(digits, offset=0, length=8, repeats=1):
    digits = [int(d) for d in digits]
    total_len = len(digits) * repeats
    cache = {}  # map (depth, i) -> digit
    for i, d in enumerate(digits * repeats):  # fill top row
        cache[(0, i)] = d
    for depth in range(100):  # fill rightmost column
        cache[(depth + 1, total_len - 1)] = cache[(depth, total_len - 1)]
    filled = [0] + [total_len - 1] * 100

    def fft_pattern(reps):
        pattern = chain.from_iterable(repeat(d, reps) for d in [0, 1, 0, -1])
        return islice(cycle(pattern), 1, total_len + 1)

    def fft_digit_slow(depth, i):
        total = sum(
            fft_digit(depth - 1, j) * p
            for j, p in enumerate(fft_pattern(i + 1)) if p)
        return abs(total) % 10

    def fft_digit_fast(depth, i):
        assert i >= total_len / 2
        if filled[depth - 1] > i:
            fft_digit_fast(depth - 1, i)  # compute row above
        for j in reversed(range(i, filled[depth])):
            total = cache[(depth, j + 1)] + cache[(depth - 1, j)]
            cache[(depth, j)] = abs(total) % 10
        filled[depth] = i
        return cache[(depth, i)]

    def fft_digit(depth, i):
        try:
            return cache[(depth, i)]
        except KeyError:
            assert depth > 0 and i < filled[depth]
        if i >= total_len / 2:  # In the right half
            return fft_digit_fast(depth, i)
        else:
            cache[(depth, i)] = fft_digit_slow(depth, i)
            return cache[(depth, i)]

    return [fft_digit(100, i) for i in range(offset, offset + length)]


with open('16.input') as f:
    digits = f.read().rstrip()

# part 1
print(''.join(str(d) for d in fft(digits)))

# part 2
offset = int(digits[:7])
print(''.join(str(d) for d in fft(digits, offset=offset, repeats=10000)))
