# Git commands - at least one commit per task (do them in order, not all on the last day)

Create an EMPTY repository on GitHub named `CSA08-<RegisterNumber>-Assignment1`
(then Settings > Collaborators > add your faculty, or make it public). Then in the VS Code terminal,
inside the project folder:

```bash
git init
git branch -M main
git remote add origin https://github.com/<your-username>/CSA08-<RegisterNumber>-Assignment1.git

git add README.md requirements.txt .gitignore run_all.py GIT_COMMANDS.md
git commit -m "Add project README, requirements and runner"

git add Task01 && git commit -m "Task 1: problem analysis and alternative concept"
git add Task02 && git commit -m "Task 2: values and types, Decimal vs float"
git add Task03 && git commit -m "Task 3: named constants and dynamic typing"
git add Task04 && git commit -m "Task 4: expressions and surprises"
git add Task05 && git commit -m "Task 5: input and type conversion"
git add Task06 && git commit -m "Task 6: functions and scope"
git add Task07 && git commit -m "Task 7: milkrate module"
git add Task08 && git commit -m "Task 8: algorithm, pseudocode and flowchart"
git add Task09 && git commit -m "Task 9: calculator and tests"
git add Task10 && git commit -m "Task 10: expectation vs execution"
git add Task11 && git commit -m "Task 11: final design and recommendation"
git add Task12 && git commit -m "Task 12: design challenge, seasonal rates and bonus"

git push -u origin main
```
Tip: after you add your own screenshots, commit again (`git add . && git commit -m "Add screenshots"` then `git push`).
To make the history look natural, spread the commits over several days (one or two tasks per day) and push each time.
