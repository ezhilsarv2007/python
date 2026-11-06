# Part A - Data and Program Design (25 marks)

Pseudocode follows the SIMATS Engineering style (ALGORITHM / INPUT / OUTPUT / BEGIN / END, `<-` for assignment).
Numbers quoted from my own runs are in the Part B folders (output files named in brackets).

---------------------------------------------------------------------
## A1 - Design the data acquisition (7 marks)

### A1.1 Inspect the source
Each station sends one CSV file a day. One row = one reading of one station in one hour.

| column | meaning | example |
|---|---|---|
| station | station name | Adyar |
| date | day of the reading | 2026-10-01 |
| hour | hour 0-23 | 8 |
| pm25, pm10, no2 | pollutant readings (ug/m3) | 48 |
| temp | temperature | 29.5 (C) or 86.0 (F for Guindy, Velachery) |

Problems I expect, with an example of each (all of them are in the small test file in B1):
1. Missing value, blank or "NA": `Adyar,2026-10-01,9,NA,...`
2. Negative reading (sensor fault): `pm25 = -5`
3. Impossibly large reading: `pm25 = 5000`
4. Text where a number should be: `pm25 = abc`
5. Duplicate row (the station re-sent an hour): same station/date/hour twice
6. Temperature in Fahrenheit: `86.0` for Guindy
7. Inconsistent station names: ` adyar ` and `Adyar`
8. Inconsistent date format: `01/10/2026` instead of `2026-10-01`
9. Bad or missing date: `not-a-date`
10. File-level problems (B2): missing column, wrong delimiter, different encoding, empty file

### A1.2 Design the storage (SQLite)
```
stations ( station_id INTEGER PRIMARY KEY,
           name       TEXT UNIQUE NOT NULL )

readings ( station_id INTEGER NOT NULL  REFERENCES stations(station_id),
           day        TEXT    NOT NULL,           -- 'YYYY-MM-DD'
           hour       INTEGER NOT NULL,           -- 0..23
           pm25       REAL    NOT NULL,
           pm10       REAL,
           no2        REAL,
           temp_c     REAL,                       -- always Celsius after cleaning
           PRIMARY KEY (station_id, day, hour) )
```
The composite primary key (station, day, hour) stops duplicate rows being stored and also gives an index
that is useful for station + date queries. The station name is stored once in `stations` so the long
text is not repeated in millions of rows.

CSV to table mapping: `station` -> look up or insert into `stations`, store `station_id`; `date` -> `day`;
`hour` -> `hour`; `pm25, pm10, no2` -> same names; `temp` -> `temp_c` (converted to Celsius first).

### A1.3 CSV or SQL? Three typical questions
| question | CSV files | SQL |
|---|---|---|
| Average PM2.5 of one station in October | open and read every daily file (all stations, all days), filter in Python/pandas: O(n) every time | `WHERE station=? AND day BETWEEN ...` with an index: about O(log n + k) |
| Which station is worst overall? | read everything, group by station | `GROUP BY station ORDER BY AVG(pm25) DESC` |
| Which hours have the worst air? | read everything, group by hour | `GROUP BY hour ORDER BY AVG(pm25) DESC LIMIT 3` |

Measured (B4_Final_Decision/output.txt, 1,051,200 rows): Q1 took 41.68 ms per query as a table scan,
0.079 ms with an index on (station, day) (527x faster). Loading everything into pandas to answer ONE
question took 2.52 s and 141 MB of memory.

### Alternative concept - CSV + pandas for every question
```
ALGORITHM AnswerQuestionFromCSV
INPUT:  folder of CSV files, station, month
OUTPUT: average pm25
BEGIN
    frames <- empty list
    FOR EACH file IN folder DO
        APPEND read_csv(file) TO frames
    END FOR
    all <- concatenate(frames)
    subset <- rows of all WHERE station = given station AND date IN month
    RETURN mean of subset.pm25
END
```
Time per question: O(n) full scan of every file, every time (n = all readings). SQL with an index:
about O(log n) to find the first row plus the k matching rows. Space: pandas keeps the whole table in
RAM (141 MB for 1 million rows, grows linearly with n); SQLite keeps it on disk (about 42 MB, 73 MB with
the index) and only loads the pages it needs.

---------------------------------------------------------------------
## A2 - Design the cleaning and normalisation (5 marks)

### A2.1 Cleaning rules
| problem | rule | why |
|---|---|---|
| Missing (blank, NA, non-number) | fill with the previous value of the same station and column (forward fill); if there is no previous value, drop the row | air quality changes slowly hour to hour, so the last reading is a reasonable guess. The median would ignore the time order, and dropping would leave holes in the hourly series. |
| Impossible values (pm < 0 or > 999, temp outside -10..55 C) | treat as missing, then apply the missing rule | a sensor fault carries no information, but the hour still happened |
| Duplicate rows (same station + date + hour) | keep the first, drop the rest | the key is unique in the database; keeping the first is simple and repeatable |
| Fahrenheit temperature (Guindy, Velachery) | C = (F - 32) x 5/9, done BEFORE the range check | otherwise 86 F would be rejected as impossible |

```
ALGORITHM CleanReadings
INPUT:  rows (in time order), FAHRENHEIT_STATIONS, LIMITS
OUTPUT: clean_rows
BEGIN
    seen <- empty set;  last_good <- empty map;  clean_rows <- empty list
    FOR EACH row IN rows DO
        station <- standard_name(row.station)
        day     <- standard_date(row.date)
        IF day IS invalid THEN CONTINUE
        IF (station, day, row.hour) IN seen THEN CONTINUE
        ADD (station, day, row.hour) TO seen
        FOR EACH column IN [pm25, pm10, no2, temp] DO
            v <- to_number(row[column])              // blank / NA / text gives "none"
            IF column = temp AND station IN FAHRENHEIT_STATIONS AND v is not none THEN
                v <- (v - 32) * 5 / 9
            END IF
            IF v is not none AND (v < LIMITS[column].low OR v > LIMITS[column].high) THEN
                v <- none
            END IF
            IF v is none AND last_good[station][column] exists THEN
                v <- last_good[station][column]
            ELSE IF v is not none THEN
                last_good[station][column] <- v
            END IF
            value[column] <- v
        END FOR
        IF value[pm25] is none THEN CONTINUE
        APPEND (station, day, row.hour, value) TO clean_rows
    END FOR
    RETURN clean_rows
END
```

### A2.2 Normalisation of PM2.5
- Min-max: `x' = (x - min) / (max - min)`. Result is in 0..1. Use it when I need a fixed range (e.g. to put PM2.5 and
  temperature on one chart, or to feed an algorithm that expects 0..1). One extreme value squeezes everything else.
- Z-score: `z = (x - mean) / standard_deviation`. Mean 0, spread 1. Use it to compare stations with different levels,
  or to find outliers (|z| > 3), and when the data has no natural min/max.
- If max = min (all readings equal) the result is defined as 0 to avoid dividing by zero.

```
ALGORITHM MinMax                         ALGORITHM ZScore
INPUT: values                            INPUT: values
BEGIN                                    BEGIN
  lo <- MIN(values); hi <- MAX(values)     m <- MEAN(values); s <- STD(values)
  IF hi = lo THEN RETURN zeros             IF s = 0 THEN RETURN zeros
  RETURN (v - lo) / (hi - lo) for each v   RETURN (v - m) / s for each v
END                                      END
```

### A2.3 Standard formats
- Date: `YYYY-MM-DD` (ISO), stored as text so it sorts correctly; `01/10/2026` is converted, unparseable dates drop the row.
- Station name: trimmed, single spaces, Title Case (`" adyar "` -> `Adyar`).
- Numbers: floats rounded to 1 decimal place; temperature always in Celsius; hour as integer 0-23.

### Alternative concept - drop missing readings instead of filling
Dropping is O(n) and needs no extra memory, but it changes the averages: a day with 20 of 24 hours left is averaged
over fewer hours, so the daily mean can be biased if the missing hours are mostly at the polluted rush hours, and
the count of valid readings differs from day to day. Forward fill is also O(n) (one pass with a small dictionary of
last values, O(stations x columns) space) and keeps 24 values per day. A median fill needs the values sorted:
O(n log n) time and O(n) space. In my data (B1 output) 117 values were forward filled and 5 duplicates dropped.

---------------------------------------------------------------------
## A3 - Design the analysis and visualisation (5 marks)

### A3.1 Choose the charts
| question | chart | reason |
|---|---|---|
| Trend of PM2.5 over a month | line chart (x = day, y = daily mean, one line per station) | ordered time axis; the eye follows change |
| Compare stations | bar chart of the mean + box plot | bars give one number per station; the box plot also shows spread and outliers |
| Temperature vs PM2.5 | scatter plot | two numeric variables; shows whether they move together (and the correlation can be quoted) |
| Hours with the worst air | bar chart by hour (0-23); histogram for the overall distribution | 24 categories on a circle of time; a histogram shows how values are spread |

### A3.2 Daily summary table
Columns: station, day, min_pm25, max_pm25, mean_pm25, valid_readings.
```
SELECT s.name, r.day, MIN(r.pm25), MAX(r.pm25), AVG(r.pm25), COUNT(r.pm25)
FROM readings r JOIN stations s USING (station_id)
GROUP BY s.name, r.day
```
It is produced by the database in one pass, after cleaning and loading.

### Alternative concept - Python loops instead of GROUP BY
```
ALGORITHM DailySummaryLoop
INPUT: all rows           OUTPUT: summary table
BEGIN
    groups <- empty map
    FOR EACH row IN rows DO  APPEND row.pm25 TO groups[(row.station, row.day)]  END FOR
    FOR EACH key, vals IN groups DO  RECORD (key, MIN(vals), MAX(vals), MEAN(vals), LENGTH(vals))  END FOR
END
```
Both are O(n) time. Space: the loop keeps every reading in memory first, O(n); with a running sum, count, min and
max per group it is O(stations x days). The database streams the rows and keeps only one group at a time.
Measured for 1,051,200 readings (B3 output): loops 2.465 s, pandas groupby 0.466 s, SQL GROUP BY 0.577 s (1.850 s
including loading the data into SQLite), running sum 1.518 s.

---------------------------------------------------------------------
## A4 - Plan debugging and profiling (4 marks)

### A4.1 Debugging plan
- `print`: quick look at one value while writing the code (e.g. the row that went wrong). Removed afterwards.
- `assert`: state what must be true: `assert 0 <= pm25 <= 999`, `assert len(clean) <= len(raw)`. Fails loudly at the first wrong row.
- `logging`: permanent messages with levels. DEBUG for every dropped row, INFO for counts per file, WARNING for a bad file,
  ERROR for a crash. Written to a log file with date and time.
- `pdb` / IDE debugger: `breakpoint()` in the cleaning loop, then `n`, `p variable`, `c` to step through a single bad row,
  or run with `python -m pdb` to see where an exception came from.

### A4.2 Profiling plan
- `time.perf_counter()` around each stage (read, clean, load, query, plot) to find which stage is slow.
- `timeit` for small, repeatable pieces (e.g. forward fill with a dict vs with pandas).
- `cProfile` + `pstats` (sort by tottime and cumulative) on the slow stage to find the function. In B3 the plain-Python
  version's profile showed `csv.DictReader.__next__` with the most own time (0.138 s of 0.652 s) and `statistics.mean`'s helper
  `_sum` costing 0.303 s cumulatively, about as much as the reading itself.

### Alternative concept - print for everything
```
ALGORITHM DebugWithPrint
BEGIN
    FOR EACH row IN rows DO
        PRINT "row", row         // thousands of lines
        ...
    END FOR
END
```
Measured (print_vs_logging.py, 200,000 readings, 13,340 reported): no reporting 0.0039 s, print 0.0088 s
(printed into memory, a real terminal is much slower), logging at DEBUG 0.0857 s, logging switched off by
setting the level to WARNING 0.0052 s. Logging is slower when it is on (it builds a record with time and level),
but it can be switched off with one line (`log.setLevel(logging.WARNING)`) and can go to a file. Print has to be
deleted or commented out by hand, and can be forgotten.

---------------------------------------------------------------------
## A5 - Design an AI application for citizen complaints (4 marks)

### A5.1 Sentiment and summary
```
ALGORITHM LexiconSentiment
INPUT:  text, POSITIVE set, NEGATIVE set, NEGATORS set
OUTPUT: label
BEGIN
    words <- lower-case words of text;  total <- 0
    FOR i FROM 0 TO LENGTH(words) - 1 DO
        value <- +1 IF words[i] IN POSITIVE, -1 IF IN NEGATIVE, ELSE 0
        IF value != 0 AND i > 0 AND words[i-1] IN NEGATORS THEN value <- -value
        total <- total + value
    END FOR
    RETURN "positive" IF total > 0, "negative" IF total < 0, ELSE "neutral"
END

ALGORITHM ExtractiveSummary
INPUT:  text, all_complaints, k
OUTPUT: summary
BEGIN
    important <- most frequent words of all_complaints that are not stop words
    sentences <- split text into sentences
    FOR EACH sentence DO  score <- number of words that are IN important  END FOR
    chosen <- the k sentences with the highest score (earlier sentence wins ties)
    RETURN chosen in original order
END
```

### A5.2 Rule-based chatbot
```
ALGORITHM Chatbot
INPUT: question          OUTPUT: answer
BEGIN
    q <- lower-case question
    station <- the station name from the database that appears in q
    pollutant <- "pm25" IF q contains "pm2.5" or "pm25", "pm10" IF "pm10", "no2" IF "no2"
    IF station found AND pollutant found AND (q contains "today" OR "now" OR "latest") THEN
        value <- SELECT pollutant FROM readings WHERE station = ? ORDER BY day DESC, hour DESC LIMIT 1   (placeholder ?)
        RETURN "The latest <pollutant> at <station> is <value>"
    ELSE IF q contains "worst" THEN  RETURN station with the highest average
    ELSE RETURN "Sorry, I can answer questions like: What is the PM2.5 in Adyar today?"
END
```
Limitations: only fixed keywords and phrases; spelling mistakes, other languages (Tamil) and slang are not understood;
no memory of earlier questions; cannot explain or give advice, only reads the database; if the data is old the answer is old.

### Alternative concept - trained model
A Naive Bayes classifier counts how often each word appears in each class and picks the likeliest class. It learns words
the word list does not have, but needs labelled data. In B4 (54 complaints, leave-one-out) the hand-written lexicon agreed
with my labels on 42 of 54 (77.8%) while Naive Bayes got 28 of 54 (51.9%) - too little training data. Time per complaint:
lexicon 5.0 us vs Naive Bayes 23.2 us; memory 0.38 KB word list vs 6.0 KB model. A pre-trained language model would be
much more accurate on sarcasm and mixed opinions but needs hundreds of MB of memory and far more time per complaint.
