"""Q6: Count ways to climb stairs using recursion and iteration."""
from functools import lru_cache
import sys

calls_naive = 0
calls_memo = 0


def ways_naive(n):
    global calls_naive
    calls_naive += 1
    if n <= 1:
        return 1
    return ways_naive(n - 1) + ways_naive(n - 2)


@lru_cache(maxsize=None)
def ways_memo(n):
    global calls_memo
    calls_memo += 1
    if n <= 1:
        return 1
    return ways_memo(n - 1) + ways_memo(n - 2)


def ways_loop(n):
    if n <= 1:
        return 1
    previous_two = 1
    previous_one = 1
    for step in range(2, n + 1):
        current = previous_one + previous_two
        previous_two = previous_one
        previous_one = current
    return previous_one


print("HAND CHECK")
for number in range(1, 7):
    print("n =", number, "| ways =", ways_loop(number))

print("\nCALL COUNT COMPARISON")
for number in [10, 20, 25, 30]:
    calls_naive = 0
    calls_memo = 0
    ways_memo.cache_clear()
    answer_naive = ways_naive(number)
    answer_memo = ways_memo(number)
    print("n =", number, "| result:", answer_naive,
          "| naive calls:", calls_naive, "| memo calls:", calls_memo)

print("\nLARGE INPUT")
print("Recursion limit:", sys.getrecursionlimit())
try:
    ways_memo.cache_clear()
    print("Memoised n=1000:", ways_memo(1000))
except RecursionError:
    print("Memoised recursion reached the Python recursion limit.")
print("Loop n=1000:", ways_loop(1000))
