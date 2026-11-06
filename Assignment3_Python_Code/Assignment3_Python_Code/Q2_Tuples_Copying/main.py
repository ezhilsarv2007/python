import copy
import sys
import time

rows, cols = 3, 4

# This is the incorrect way: all rows refer to the same list.
bad = [[0] * cols] * rows
bad[0][1] = 7

# Each row is created separately.
good = [[0 for _ in range(cols)] for _ in range(rows)]
good[0][1] = 7

print("bad :", bad)
print("good:", good)
print("Same row in bad?", bad[0] is bad[1])
print("Same row in good?", good[0] is good[1])

# Tuples can be dictionary keys because they cannot be changed.
stops = {
    (13.0827, 80.2707): "Chennai Central",
    (13.0418, 80.2341): "T. Nagar"
}
print("Stop name:", stops[(13.0418, 80.2341)])

# A list cannot be a dictionary key because it is mutable.
try:
    sample = {[13.0418, 80.2341]: "T. Nagar"}
except TypeError as error:
    print("List key error:", error)

original = [[1, 2], [3, 4]]
alias = original
shallow = copy.copy(original)
slice_copy = original[:]
deep = copy.deepcopy(original)
original[0][0] = 99
print("Alias:", alias)
print("Shallow copy:", shallow)
print("Slice copy:", slice_copy)
print("Deep copy:", deep)

# Unpacking tuples in a loop.
for latitude, longitude in stops:
    print("Coordinates:", latitude, longitude)

# A tuple cannot be changed, but a list inside it can be changed.
mixed = ("bus stop", [10, 20])
mixed[1].append(30)
print("Tuple containing a list:", mixed)

# Basic memory and timing comparison.
values = list(range(1000))
tuple_values = tuple(values)
print("List size:", sys.getsizeof(values), "bytes")
print("Tuple size:", sys.getsizeof(tuple_values), "bytes")

for kind, make in (("list", list), ("tuple", tuple)):
    start = time.perf_counter()
    data = make(range(100000))
    creation_time = time.perf_counter() - start
    start = time.perf_counter()
    item = data[50000]
    index_time = time.perf_counter() - start
    print(f"{kind}: item={item}, create={creation_time:.6f}s, index={index_time:.8f}s")
