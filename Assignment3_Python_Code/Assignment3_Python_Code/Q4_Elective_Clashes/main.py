import random
import time

ai_elective = {"192311001", "192311004", "192311007", "192311009"}
iot_elective = {"192311002", "192311004", "192311009", "192311010"}
all_students = {f"1923110{i:02d}" for i in range(1, 11)}

# Set operators give the required groups.
both = ai_elective & iot_elective
exactly_one = ai_elective ^ iot_elective
neither = all_students - (ai_elective | iot_elective)

print("clash      :", sorted(both))
print("exactly one:", sorted(exactly_one))
print("neither    :", sorted(neither))

# The same result using set methods.
both_method = ai_elective.intersection(iot_elective)
one_method = ai_elective.symmetric_difference(iot_elective)
neither_method = all_students.difference(ai_elective.union(iot_elective))
print("Methods give same result:", both == both_method and exactly_one == one_method and neither == neither_method)

# Membership timing for list and set.
for size in (10000, 100000, 1000000):
    numbers = list(range(size))
    number_set = set(numbers)
    target = size - 1

    start = time.perf_counter()
    target in numbers
    list_time = time.perf_counter() - start

    start = time.perf_counter()
    target in number_set
    set_time = time.perf_counter() - start
    print(f"{size} values: list={list_time:.8f}s, set={set_time:.8f}s")

# Empty and identical elective checks.
print("Empty electives:", set() & set())
print("Identical electives:", ai_elective & ai_elective)
