# Q7 – Diagnose, Redesign and Validate

## Selected program
The plain recursive temple-steps program from Q6 is selected because it recalculates the same smaller stair counts many times.

## Design objective
For n=30, return the same answer while reducing the number of repeated function calls. For n=1,000, calculate the answer without depending on Python's recursion depth.

## Redesign
The revised solution uses a loop and stores only the previous two answers. This removes repeated work and does not need a recursion stack or a full cache.

Run: `python q7_redesign.py`

**Complexity:** Original plain recursion is O(φⁿ) time. The redesigned loop is O(n) time and O(1) extra space. The trade-off is that the loop does not preserve the recursive structure, but it is more suitable for large n.
