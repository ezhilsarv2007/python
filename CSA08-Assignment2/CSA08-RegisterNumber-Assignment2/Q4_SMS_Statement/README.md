# Q4 – Building Long Text: += or join()

Run: `python q4_statement.py`

The program creates the same statement using repeated `+=`, a list followed by `join()`, and f-string line creation. It measures 1,000, 10,000 and 200,000 lines, with three runs for each method, and prints the average.

**Complexity:** `join()` takes O(n) time in the total number of characters and stores the parts plus final string. Repeated `+=` can require repeated copying and may approach O(n²), although CPython sometimes optimises it. Timings vary by computer.
