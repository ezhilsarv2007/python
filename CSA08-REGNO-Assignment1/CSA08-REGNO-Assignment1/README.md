# CSA08 - Assignment 1: Payment Calculator for a Village Milk Co-operative

| | |
|---|---|
| **Name** | `<YOUR NAME>` |
| **Register number** | `<YOUR REGISTER NUMBER>` |
| **Course** | CSA08 - Python programming (CO1) |
| **Python version** | Python 3.12 (check yours with `python --version`; any 3.9+ works) |
| **Libraries** | None outside the standard library (see `requirements.txt`) |
| **Repository** | `CSA08-<RegisterNumber>-Assignment1` |

## How to run
From the repository root run `python run_all.py` to execute every task and refresh each `TaskXX/output.txt`
and the output section of each `TaskXX/README.md`. Or run one task at a time:

| Task | Folder | Command(s) | Result in one line |
|---|---|---|---|
| 1 | `Task01` | `python task01_analysis.py` | Inputs, outputs, constants, rules, assumptions; separate variables do not scale, a list of tuples does |
| 2 | `Task02` | `python interactive_session.py`, `python task02_complete_code.py`, `python task02_alternatives.py` | float total 33400.30000000061 vs Decimal 33400.30; Decimal from a string is exact |
| 3 | `Task03` | `python task03_constants.py` | One `rates.py` for all rates; no true constants in Python; dynamic typing demonstrated |
| 4 | `Task04` | `python task04_expressions.py` | `round()` gives correct steps; `int()` and `floor()` give wrong rates |
| 5 | `Task05` | `python task05_input.py` (or `--live`) | `input()` is a string; str-check vs try/except compared |
| 6 | `Task06` | `python task06_functions.py` | Functions with docstrings; scope demonstrated; call overhead negligible |
| 7 | `Task07` | `python milkrate.py`, `python use_milkrate.py`, `python copied_functions_demo.py` | Expected table reproduced; `__name__` guard demonstrated |
| 8 | `Task08` | `python algorithm.py` | Hand trace total Rs 917.50 = program total |
| 9 | `Task09` | `python milk_calculator.py --file entries.csv`, `python test_milk_calculator.py`, `python task09_manual_vs_assert.py` | 26/26 tests pass; 5-entry hand total Rs 1977.55 |
| 10 | `Task10` | `python task10_compare.py` | Rounding rule matters more than float error; Decimal 4-8x slower but fast enough |
| 11 | `Task11` | `python task11_final_design.py` | Recommend Decimal + half-up per payment + JSON rate card |
| 12 | `Task12` | `python task12_design_challenge.py` | MODIFY: RateCard per season, fractional steps, bonus function; 16/16 tests pass |

## Folder layout
```
CSA08-<RegisterNumber>-Assignment1/
|-- README.md  requirements.txt  run_all.py  GIT_COMMANDS.md
|-- Task01 ... Task12/   (each: source .py files, input files, README.md, output.txt, screenshots/)
```
Put your own screenshots of each program running in `TaskXX/screenshots/`.

## Note on the assumptions
SNF limits (7.0-10.0), the 1000-litre per-entry cap, half-up rounding, and the bonus being paid on all litres in every season are assumptions; they are written in the task READMEs and should be stated in the report.
