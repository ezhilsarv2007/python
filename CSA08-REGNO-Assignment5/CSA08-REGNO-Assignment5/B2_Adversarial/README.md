# B2 - Engineer adversarial data

Run: `python complete_the_code.py` and `python adversarial.py`. Outputs: `output_complete_the_code.txt`, `output.txt`. The bad test files are written to `adversarial_files/`.

## Complete the Code
TODO 1: `con.executemany("INSERT INTO aq (station, day, pm25) VALUES (?, ?, ?)", readings)` then `con.commit()`.
TODO 2: `SELECT AVG(pm25) FROM aq WHERE station = ?` with `(name,)`. Output: `54.0 108.0` then `None`.

Why the injection attempt returns None: with `?` the whole text `Adyar' OR '1'='1` is sent as ONE value, not as SQL. The database looks for a station literally named `Adyar' OR '1'='1`, finds no rows, and `AVG` of no rows is NULL, which Python shows as `None`.

## Bad files (output section 1)
| file | naive loader | safe loader |
|---|---|---|
| missing column | `KeyError: 'pm25'` | clear message naming the missing column |
| wrong delimiter (`;`) | `KeyError: 'station'` | `csv.Sniffer` finds `;` and loads it |
| cp1252 / utf-16 encoding | `UnicodeDecodeError` | tries utf-8-sig, utf-16, cp1252 and loads it |
| empty file | returns `[]` quietly | rejected with "file is empty" |

What it shows: a program that assumes a perfect file crashes with an unhelpful error, or worse, silently returns nothing (the empty file). The loader has to check the structure before trusting the data, and report problems in words the operator can act on.

## Quote in a station name (output section 2)
- Built with `+`: `St. Mary's Road` gives `OperationalError: near "s": syntax error` because the quote ends the string early. The input `Adyar' OR '1'='1` turns the query into `WHERE station = 'Adyar' OR '1'='1'`, which is true for every row, so it returns 78.8 (the average of ALL data).
- With `?`: the real name works (70.0) and the injection text is harmless (`None`).
This shows that user text must never be joined into SQL; placeholders let the database treat it only as data. SQLite's `execute()` also refuses stacked statements (`; DROP TABLE`), but the `OR` trick still works without them.

## executemany vs execute in a loop
| rows | loop | executemany |
|---|---|---|
| 10,000 | 0.010 s | 0.005 s |
| 100,000 | 0.091 s | 0.059 s |
| 500,000 | 0.546 s | 0.268 s |
Both are O(n); executemany is faster by a constant factor (about 2x) because the Python call overhead per row is gone.

## Sentiment scorer vs tricky sentences (output section 3)
It was wrong on 10 of 13. Failures: sarcasm (positive words used as mockery), double negatives (`never not helpful` is flipped only once because only the word right before is checked), negator too far (`not very good`, `not at all clean`), mixed opinions (it can only output one label), and slang with no word-list match. It worked on direct cases (`No smoke today, air is clean`).
What each reveals: the scorer reads words, not meaning. It has no idea of tone, no scope for negation, and a fixed vocabulary. It is fine for a first quick sort of complaints, but results must not be treated as exact.
