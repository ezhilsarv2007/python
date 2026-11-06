# CSA08 - Python Programming - Assignment 5 (CO5)
Data acquisition, cleaning, analysis and AI applications - City Air-Quality Monitoring Network

| | |
|---|---|
| Name | <YOUR NAME> |
| Register number | <REGISTER NUMBER> |
| Python version | 3.12 |
| GitHub link | https://github.com/<your-username>/CSA08-<RegisterNumber>-Assignment5 |

## Libraries (see requirements.txt)
csv, sqlite3, statistics, re, io, time, cProfile, pickle, logging (standard library) and pandas, numpy, matplotlib (installed with `pip install -r requirements.txt`).

## Folders
| folder | content |
|---|---|
| PartA_Design | design, rules, pseudocode, chart choices, alternative-concept analysis (A1-A5) and one small supporting measurement script (print vs logging) |
| B1_Cleaning | Complete the Code, cleaning pipeline, SQLite, SQL queries, 6 charts, pandas comparison |
| B2_Adversarial | Complete the Code, bad files, SQL injection, executemany timing, tricky sentences |
| B3_Loops_vs_Libraries_vs_SQL | loops vs pandas vs SQL at 3 sizes, cProfile |
| B4_Final_Decision | Complete the Code, sentiment and summariser on 54 complaints, naive Bayes comparison, index test |

Every program has an `output*.txt` file with the real output of the run. Each Part B folder has a README.md with the written answers.

## How to run (from inside the task folder)
```
cd B1_Cleaning                      && python complete_the_code.py && python cleaning_pipeline.py && python pandas_vs_loops.py
cd B2_Adversarial                   && python complete_the_code.py && python adversarial.py
cd B3_Loops_vs_Libraries_vs_SQL     && python compare_methods.py
cd B4_Final_Decision                && python complete_the_code.py && python b4_final.py
cd PartA_Design                     && python print_vs_logging.py
```
(`pandas_vs_loops.py` loads one million rows, so it takes about 20 seconds. `compare_methods.py` takes about 10 seconds.)

## Short result of each task
- B1: cleaning rules tested on a 13-row file with every problem (13 rows -> 10); one month for 4 stations cleaned (2,981 -> 2,976 rows), stored with executemany, 3 SQL questions answered, 6 charts interpreted. Complete the Code matches the expected output. pandas was 12x faster than loops at 100,000 rows and used about half the memory.
- B2: the safe loader rejects missing-column and empty files and detects the delimiter and encoding. String-built SQL is broken by a quote and injectable; the ? version is safe. The word-list scorer got 10 of 13 tricky sentences wrong.
- B3: loops, pandas, SQL and the running sum agree at all sizes. For 1,051,200 readings pandas took 0.47 s, SQL 1.85 s (0.58 s of it the query), the running sum 1.52 s and the plain loops 2.47 s.
- B4: the scorer agreed with my labels on 42 of 54 complaints (77.8%). An index on (station, day) made the monthly-average query 527x faster.

## Timings
Timings change a little on every run and depend on the computer. The numbers in the READMEs come from the saved output files.

## Screenshots
Run each program on your own machine and save a terminal screenshot into the `screenshots` folder of that task.
