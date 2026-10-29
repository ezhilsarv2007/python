"""Q7: Redesign the repeated recursive stair-count calculation."""
import time


def original_recursive(n):
    if n <= 1:
        return 1
    return original_recursive(n - 1) + original_recursive(n - 2)


def redesigned_loop(n):
    if n <= 1:
        return 1
    two_steps_back = 1
    one_step_back = 1
    for step in range(2, n + 1):
        current = one_step_back + two_steps_back
        two_steps_back = one_step_back
        one_step_back = current
    return one_step_back


def measure(function, number):
    start = time.perf_counter()
    answer = function(number)
    elapsed = time.perf_counter() - start
    return answer, elapsed


print("ORIGINAL VS REDESIGNED")
for number in [10, 20, 30]:
    old_answer, old_time = measure(original_recursive, number)
    new_answer, new_time = measure(redesigned_loop, number)
    print("n =", number, "| same answer:", old_answer == new_answer)
    print("  Original recursive:", old_answer, "| time:", round(old_time, 6), "seconds")
    print("  Redesigned loop   :", new_answer, "| time:", round(new_time, 6), "seconds")

large_answer, large_time = measure(redesigned_loop, 1000)
print("\nLarge input")
print("n = 1000 | answer has", len(str(large_answer)), "digits")
print("Loop time:", round(large_time, 6), "seconds")
