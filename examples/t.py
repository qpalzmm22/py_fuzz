import collections

data = collections.defaultdict(set)
coverage = collections.defaultdict(set)

idx = 0

while True:
    idx += 1
    prev = input()
    curr = input()
    data[0].add((prev, curr))
    coverage.add((data, idx))
    print(data[0])
    

