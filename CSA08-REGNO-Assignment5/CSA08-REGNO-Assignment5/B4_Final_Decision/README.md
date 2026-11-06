# B4 - Final engineering decision

Run: `python complete_the_code.py` and `python b4_final.py` (about 20 seconds). Outputs: `output_complete_the_code.txt`, `output.txt`. The 54 complaints with my labels are in `complaints_data.py`; `sentiment.py` holds the scorer and summariser.

## Complete the Code
TODO 1: for each word take +1 / -1 / 0 from the word lists, flip the sign when the previous word is in NEGATORS, add to `total`. The output matches the expected output (positive, negative, negative, positive).
A complaint labelled wrongly: `The bus was not very good.` is labelled positive. `very` sits between `not` and `good`, so `good` is not directly after a negator and counts as +1. A negator should have a longer reach (a few words) or use sentence structure.

## B4.1 Sentiment and summariser on 54 complaints
- Agreement with my own reading: 42 of 54 (77.8%). Confusion table and each disagreement are in `output.txt`. Errors are sarcasm, slang, mixed opinions, questions that contain a stray positive word, and a negator that is too far away. (Please re-read the 54 labels and change any you disagree with, then run again, because the agreement count is only meaningful with your own labels.)
- Summariser (sentences with the most frequent important words) vs first two sentences: the share of important words kept was 0.990 vs 0.973. The two methods give the same summary when the main point is at the start, and differ when it is not (complaint 11: the frequent-words version keeps "It should not be on the road" instead of "Passengers were coughing"). The quality difference on my short complaints is small.
- Time per complaint: sentiment 5.0 us, frequent-words summary 7.9 us, first-k 2.3 us. For 50,000 complaints a month that is about 0.25 s and 0.39 s.

## B4.2 Index on (station, day)
Table of 1,051,200 readings (120 stations x one year). Slowest query: average PM2.5 of one station in October.
| | time per query | plan |
|---|---|---|
| no index | 41.68 ms | SCAN readings |
| index on (station, day) | 0.079 ms | SEARCH ... USING INDEX |
The query became 527x faster. Costs: building the index took 0.58 s, the file grew from 41.6 MB to 73.3 MB, and inserting 200,000 rows took 0.31 s with the index vs 0.17 s without it. Answering the same kind of question by loading everything into pandas took 2.52 s and 141 MB.

## B4.3 Production decision (100 more stations every 15 minutes, 50,000 complaints a month)
New volume: about 100 x 96 x 365 = 3.5 million new readings a year, plus the existing 12 stations.
- Storage: keep the cleaned readings in a database (SQLite is enough for a few million rows with one writer; switch to PostgreSQL if several programs must write at the same time) with the (station, day) index. The index made the monthly query 527x faster for 1.8x the file size and slightly slower inserts, which is a good trade.
- Cleaning: clean each incoming file once, when it arrives, and store only clean rows. pandas cleaned 1,000,000 rows in 1.3 s against 15.4 s for loops, so use pandas for the batch step and keep the loop version as the readable reference and test.
- Analysis: daily summaries with SQL GROUP BY (0.58 s for 1.05 M rows) or a running sum if only mean, min and max are needed.
- AI: the word-list scorer takes about 0.25 s a month for 50,000 complaints and agreed with my labels 77.8% of the time, so it is good enough to sort complaints into rough groups and to show a trend. It is not good enough to act on a single complaint automatically: sarcasm, mixed and negation-distance errors need a trained model. My hand-written naive Bayes scored only 51.9% (leave-one-out) because 54 complaints are too few to train on, so I cannot claim from my data that a trained model is better. Decision: use the word list now, have staff correct a sample of labels every month, and train a model once a few thousand labelled complaints exist, then compare it against the word list on the same test set.

## Alternative concept - first k sentences as the summary
Time is O(1) in the length of the complaint (it only finds the first k sentences; measured 2.3 us) against O(words) for the frequent-words summariser (7.9 us), and space is O(k sentences) vs O(words) for the word counts. On my 54 complaints the summaries were almost equally good (0.973 vs 0.990). First-k is the better choice when complaints start with the main point; the frequent-words version is better when the main point is later in the text.
