def pairwise_items(seq):
    return zip(seq, seq[1:])


def consecutive_runs(seq):
    run = seq[0]
    for prev, cur in pairwise_items(seq):
        if prev == cur:
            run += cur
        else:
            yield run
            run = cur
    yield run


def item_repeated(seq):
    return any(a == b for a, b in pairwise_items(seq))


def item_repeated_once(seq):
    return any(len(run) == 2 for run in consecutive_runs(seq))


def monoton_incr(seq):
    return all(a <= b for a, b in pairwise_items(seq))


with open('04.input') as f:
    lo, hi = tuple(map(int, f.read().rstrip().split('-', 1)))

# part 1
part1 = lambda n: item_repeated(str(n)) and monoton_incr(str(n))
print(len(list(filter(part1, range(lo, hi)))))

# part 2
part2 = lambda n: item_repeated_once(str(n)) and monoton_incr(str(n))
print(len(list(filter(part2, range(lo, hi)))))
