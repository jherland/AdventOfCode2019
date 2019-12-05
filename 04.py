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


def apply_preds_to_digits(*preds):
    return lambda n: all(pred(str(n)) for pred in preds)


with open('04.input') as f:
    lo, hi = tuple(map(int, f.read().rstrip().split('-', 1)))

# part 1
part1 = apply_preds_to_digits(monoton_incr, item_repeated)
print(len(list(filter(part1, range(lo, hi)))))

# part 2
part2 = apply_preds_to_digits(monoton_incr, item_repeated_once)
print(len(list(filter(part2, range(lo, hi)))))
