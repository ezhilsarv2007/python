# Q6 – Recursion and Its Limits

Run: `python q6_temple.py`

The number of ways to climb n steps using one or two steps is calculated using plain recursion, memoised recursion and a loop. The program prints hand-check values for n=1 to 6, call counts for n=10, 20, 25 and 30, and checks the recursion limit for n=1,000.

**Complexity:** Plain recursion is O(φⁿ) time with deep recursion stack use. Memoisation is O(n) time and O(n) cache/stack space. The loop is O(n) time and O(1) extra space.
