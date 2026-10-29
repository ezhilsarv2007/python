# Q5 – Canteen Functions, Parameters and Scope

Run: `python q5_canteen.py`

The first function demonstrates the mutable default-list bug. The corrected function uses `None` and creates a fresh list for each customer. The program also demonstrates positional, keyword and default arguments, returning multiple values, and local/global/nonlocal scope.

**Complexity:** Appending one item to a Python list is O(1) amortised time. Each customer has a separate order list, using O(m) space for m items in that order.
