def masses():
    with open('01.input') as f:
        for line in f:
            yield int(line.rstrip())


def fuel(mass):
    return max(0, int(mass / 3) - 2)


def acc_fuel(mass):
    f = fuel(mass)
    if f > 0:
        f += acc_fuel(f)
    return f


# part1
print(sum(map(fuel, masses())))

# part2
print(sum(map(acc_fuel, masses())))
