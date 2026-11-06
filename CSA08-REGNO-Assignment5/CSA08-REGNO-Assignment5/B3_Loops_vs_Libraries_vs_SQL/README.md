# B3 - Loops vs libraries vs SQL

Run: `python compare_methods.py` (about 10 seconds). Output: `output.txt`. The big test CSV files are created and deleted by the program.

## B3.1 Correctness
On 1 station x 3 days, plain loops (csv + statistics.mean), pandas groupby, SQL GROUP BY and the running-sum version give the same daily means (54.321, 58.642, 57.317). At every larger size the program also checks that all four agree.

## B3.2 Timing (a year of hourly data per station)
| stations | rows | loops | pandas | SQL load | SQL query | SQL total | running sum |
|---|---|---|---|---|---|---|---|
| 1 | 8,760 | 0.019 s | 0.008 s | 0.014 s | 0.003 s | 0.017 s | 0.017 s |
| 12 | 105,120 | 0.242 s | 0.051 s | 0.138 s | 0.041 s | 0.178 s | 0.147 s |
| 120 | 1,051,200 | 2.465 s | 0.466 s | 1.274 s | 0.577 s | 1.850 s | 1.518 s |

All of them grow about 10x when the rows grow 10x (O(n)), but pandas has the smallest constant and plain loops the biggest. The SQL query alone is almost as fast as pandas, but loading the data into SQLite costs more than the query.

## B3.3 Profile (cProfile, plain Python, 12 stations, 0.652 s in total)
- By own time: `csv.DictReader.__next__` is the top entry (0.138 s) followed by `statistics._sum` (0.071 s) and `by_loops` itself (0.070 s).
- By cumulative time: `statistics.mean` (through `_sum`, 0.303 s) costs about as much as reading the whole file. It does exact fraction arithmetic (`as_integer_ratio`, `Fraction`), which is slow for 100,000 floats.
So the slowest single function is the CSV reader, and the slowest step overall is `statistics.mean`.

## B3.4 Trade-off
- Plain loops: no libraries, easy to understand, but slowest, and keeps every reading in memory.
- pandas: shortest code and fastest, but it loads the whole file into memory and needs the library.
- SQL: the data stays in a database and can be queried again and again; best when the same data is queried many times, with an index, but the load step costs time.
For a quick one-time analysis I would use pandas (fastest to write and run). For a daily automated report I would load each day's cleaned data into SQLite once and run GROUP BY queries, because the database is the permanent record, can be indexed and does not need the whole history in memory.

## Alternative concept - one pass with running sum and count
`by_running_sum` keeps `total[(station, day)]` and `count[(station, day)]` and divides at the end. Time O(n), same as storing all readings and calling `statistics.mean` (the second step is O(n) too). Space is O(stations x days) for two numbers per group, instead of O(n) for every reading. Measured at 1,051,200 rows: 1.518 s vs 2.465 s (it also avoids the slow exact arithmetic in `statistics.mean`). Its limit is that it only works for statistics that can be updated incrementally (mean, sum, count, min, max), not for the median.
