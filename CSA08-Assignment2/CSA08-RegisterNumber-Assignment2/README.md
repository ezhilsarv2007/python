# CSA08 – Python Programming Assignment 2 (CO2)

**Student name:** Ezhil  
**Register number:** Replace with your register number  
**Python version:** Python 3.10 or later  
**Libraries:** Python standard library only (`time`, `functools`, `sys`, `statistics`).

## Assignment overview
This repository contains Q1–Q7 for the State Electricity Subsidy, Bank OTP, Vehicle Registration Validator, SMS Statement Builder, Canteen Order System, Temple Steps Recursion, and Day-4 Redesign tasks.

## Folder structure
- `Q1_Decisions/` – separate `if` statements and `if-elif-else`
- `Q2_OTP_Loops/` – `while`, `for`, loop controls and changed condition
- `Q3_Number_Plate/` – string normalisation, validation and formatting
- `Q4_SMS_Statement/` – `+=`, `join()` and timing comparison
- `Q5_Canteen_Functions/` – parameters, mutable defaults and scope
- `Q6_Temple_Recursion/` – plain recursion, memoisation and iteration
- `Q7_Redesign/` – diagnose and redesign the slow recursive solution

## How to run
Open a terminal in this repository and run, for example:

```bash
python Q1_Decisions/q1_subsidy.py
python Q2_OTP_Loops/q2_otp.py
python Q3_Number_Plate/q3_validator.py
python Q4_SMS_Statement/q4_statement.py
python Q5_Canteen_Functions/q5_canteen.py
python Q6_Temple_Recursion/q6_temple.py
python Q7_Redesign/q7_redesign.py
```

No external packages are needed. `requirements.txt` is intentionally empty because all programs use the Python standard library.

## Important submission notes
1. Replace the register-number placeholder and check your name.
2. Run every program on your own computer.
3. Save screenshots of your own terminal output in the matching `outputs/` folder.
4. Q4 and Q7 timings depend on the computer. Use the timings printed by your own run in your report.
5. Commit each question separately as you complete it. Do not upload everything as one final commit.
6. Create the GitHub repository with the required name: `CSA08-<RegisterNumber>-Assignment2`.
7. Add the faculty as a collaborator if the repository is private, and paste the working GitHub link into your report.

## Suggested Git commit sequence
```bash
git add Q1_Decisions && git commit -m "Complete Q1 subsidy decisions"
git add Q2_OTP_Loops && git commit -m "Complete Q2 OTP loops"
git add Q3_Number_Plate && git commit -m "Complete Q3 vehicle number validator"
git add Q4_SMS_Statement && git commit -m "Complete Q4 SMS statement comparison"
git add Q5_Canteen_Functions && git commit -m "Complete Q5 functions and scope"
git add Q6_Temple_Recursion && git commit -m "Complete Q6 recursion investigation"
git add Q7_Redesign && git commit -m "Complete Q7 redesign and validation"
```

**Note:** The example outputs are provided to help check the programs. Run them yourself and capture genuine screenshots before submission.
