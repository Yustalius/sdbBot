import random
a = 1
b = 0
c = 0
d = 0
i = 0
while (a != b) | (a != c) | (a != d):
    i += 1
    a = random.randint(0, 99)
    b = random.randint(0, 99)
    c = random.randint(0, 99)
    d = random.randint(0, 99)
    print(f'{i}: {a} и {b} и {c} и {d}')