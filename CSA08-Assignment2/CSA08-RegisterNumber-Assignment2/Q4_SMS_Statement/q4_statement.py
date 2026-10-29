"""Q4: Compare ways to build a monthly SMS statement."""
import time
from statistics import mean


def build_plus(parts):
    text = ""
    for part in parts:
        text += part + ";"
    return text


def build_join(parts):
    return ";".join(parts) + ";"


def build_fstring(parts):
    lines = []
    for index, part in enumerate(parts):
        lines.append(f"{part};")
    return "".join(lines)


def measure(function, parts, repeats=3):
    times = []
    result = ""
    for run in range(repeats):
        start = time.perf_counter()
        result = function(parts)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
    return result, mean(times)


if __name__ == "__main__":
    for size in [1000, 10000, 200000]:
        items = [f"Item{i}:Rs{i % 50}" for i in range(size)]
        plus_text, plus_time = measure(build_plus, items)
        join_text, join_time = measure(build_join, items)
        f_text, f_time = measure(build_fstring, items)

        print("\nNumber of lines:", size)
        print("All methods create same text:", plus_text == join_text == f_text)
        print("Output length:", len(join_text))
        print("+= average time :", round(plus_time, 6), "seconds")
        print("join average time:", round(join_time, 6), "seconds")
        print("f-string average:", round(f_time, 6), "seconds")
