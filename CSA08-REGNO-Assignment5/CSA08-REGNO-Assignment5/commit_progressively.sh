#!/bin/sh
# Run ONE step per work session so the commit history shows progress.
#   sh commit_progressively.sh A     -> Part A design
#   sh commit_progressively.sh 1     -> B1,  2 -> B2,  3 -> B3,  4 -> B4
#   sh commit_progressively.sh readme
# First time only:
#   git init && git branch -M main
#   git remote add origin https://github.com/<your-username>/CSA08-<RegisterNumber>-Assignment5.git
case "$1" in
  A) git add PartA_Design && git commit -m "Part A: design, pseudocode and analysis" ;;
  1) git add B1_Cleaning && git commit -m "B1: cleaning pipeline, SQLite, charts, pandas comparison" ;;
  2) git add B2_Adversarial && git commit -m "B2: adversarial files, SQL injection, tricky sentences" ;;
  3) git add B3_Loops_vs_Libraries_vs_SQL && git commit -m "B3: loops vs pandas vs SQL, profiling" ;;
  4) git add B4_Final_Decision && git commit -m "B4: sentiment, summariser, index, final decision" ;;
  readme) git add README.md requirements.txt .gitignore commit_progressively.sh && git commit -m "Add main README and requirements" ;;
  *) echo "use A, 1, 2, 3, 4 or readme"; exit 1 ;;
esac
git push -u origin main
