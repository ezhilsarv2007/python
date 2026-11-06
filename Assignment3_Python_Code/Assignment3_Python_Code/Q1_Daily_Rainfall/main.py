import random
import time

# Create one rainfall reading for each day (in mm).
readings = [random.randint(0, 80) for _ in range(365)]

# Find the total rainfall for each week.
weekly_totals = []
for start in range(0, len(readings), 7):
    week = readings[start:start + 7]
    weekly_totals.append(sum(week))

print("Weekly totals:", weekly_totals)
if readings:
    print("Wettest day:", readings.index(max(readings)) + 1, "with", max(readings), "mm")
    print("Driest day:", readings.index(min(readings)) + 1, "with", min(readings), "mm")

# A simple moving average: calculate the average of each group of 7 days.
def naive_average(values, window=7):
    if window <= 0:
        raise ValueError("Window must be positive")
    return [sum(values[i:i + window]) / window
            for i in range(len(values) - window + 1)]

# Running sum avoids adding the same values again and again.
def running_average(values, window=7):
    if window <= 0:
        raise ValueError("Window must be positive")
    if len(values) < window:
        return []
    total = sum(values[:window])
    averages = [total / window]
    for i in range(window, len(values)):
        total += values[i] - values[i - window]
        averages.append(total / window)
    return averages

print("7-day moving averages:", [round(x, 2) for x in running_average(readings)])
dry_days = [day for day, amount in enumerate(readings, start=1) if amount == 0]
print("Dry days:", dry_days)

# Check empty and short lists.
print("Empty list result:", running_average([]))
print("Short list result:", running_average([2, 4, 6]))

# Small timing experiment for the two methods.
for size in (365, 36500, 365000):
    data = [random.randint(0, 80) for _ in range(size)]
    start = time.perf_counter()
    naive_average(data)
    naive_time = time.perf_counter() - start
    start = time.perf_counter()
    running_average(data)
    running_time = time.perf_counter() - start
    print(f"Size {size}: naive={naive_time:.5f}s, running={running_time:.5f}s")
