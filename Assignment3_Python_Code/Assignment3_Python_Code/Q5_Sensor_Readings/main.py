import random
import time
import sys

readings = [1.5, 2.5, 7.0, 9.2, 55.0, -60.0, 4.0, 8.5]

# Version 1: normal loop and append.
valid_c = []
for value in readings:
    if -50 <= value <= 50:
        valid_c.append(value)
valid_f = []
for value in valid_c:
    valid_f.append((value * 9 / 5) + 32)

# Version 2: list comprehensions.
clean_c = [value for value in readings if -50 <= value <= 50]
clean_f = [(value * 9 / 5) + 32 for value in clean_c]

# Version 3: filter() and map() with lambda.
filtered = list(filter(lambda value: -50 <= value <= 50, readings))
mapped_f = list(map(lambda value: (value * 9 / 5) + 32, filtered))

print("Valid Celsius:", clean_c)
print("Fahrenheit:", clean_f)
print("Using map/filter:", mapped_f)
print("All versions match:", valid_c == clean_c == filtered and valid_f == clean_f == mapped_f)

# enumerate() gives the minute number (starting from 1).
alarm_minutes = [minute for minute, value in enumerate(readings, start=1)
                 if -50 <= value <= 50 and not 2 <= value <= 8]
print("Alarm minutes:", alarm_minutes)

# Dictionary and set comprehensions.
fahrenheit_by_minute = {minute: (value * 9 / 5) + 32
                        for minute, value in enumerate(clean_c, start=1)}
unique_valid = {value for value in readings if -50 <= value <= 50}
print("Fahrenheit dictionary:", fahrenheit_by_minute)
print("Unique valid readings:", unique_valid)

# Timing the loop, comprehension and map/filter approaches.
for size in (10000, 100000, 1000000):
    data = [random.uniform(-60, 60) for _ in range(size)]

    start = time.perf_counter()
    loop_result = []
    for value in data:
        if -50 <= value <= 50:
            loop_result.append(value)
    loop_time = time.perf_counter() - start

    start = time.perf_counter()
    comp_result = [value for value in data if -50 <= value <= 50]
    comp_time = time.perf_counter() - start

    start = time.perf_counter()
    filter_result = list(filter(lambda value: -50 <= value <= 50, data))
    filter_time = time.perf_counter() - start

    print(f"{size}: loop={loop_time:.5f}s, comprehension={comp_time:.5f}s, filter={filter_time:.5f}s")
    assert loop_result == comp_result == filter_result

generator = (value for value in readings if -50 <= value <= 50)
print("List memory:", sys.getsizeof(clean_c), "bytes")
print("Generator memory:", sys.getsizeof(generator), "bytes")
print("All valid test:", [x for x in [2, 3, 4] if -50 <= x <= 50])
print("All invalid test:", [x for x in [60, -70] if -50 <= x <= 50])
