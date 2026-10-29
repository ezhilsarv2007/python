# Q3 – Vehicle Registration Number Validator

Run: `python q3_validator.py`

Only the string operations listed in the assignment are used for normalisation and validation. No regular expressions are used. A valid registration has 2 state letters, 2 district digits, 1–2 series letters and 4 final digits.

**Complexity:** Normalising and validating a plate of length L takes O(L) time and O(L) space for the new normalised string. A regular expression full match is also O(L) for this fixed pattern, but slicing makes each section easy to inspect.
