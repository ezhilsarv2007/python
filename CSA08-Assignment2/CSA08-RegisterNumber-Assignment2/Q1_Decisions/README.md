# Q1 – Decisions with Many Boundaries

Run: `python q1_subsidy.py`

The program checks eight sample households, including 100, 101, 200 and 201 units. It compares separate `if` statements with one `if-elif-else` chain. The first method can print more than one decision if conditions overlap. The second method selects one branch only.

**Complexity:** For a fixed number of rules, each decision is O(1) time and O(1) extra space. A lookup list searched from the beginning is O(k) time and O(k) space for k slabs. `match-case` with a fixed number of cases is also O(1) for this small rule set.
