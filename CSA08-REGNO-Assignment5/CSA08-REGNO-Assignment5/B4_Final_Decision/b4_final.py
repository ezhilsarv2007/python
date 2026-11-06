# B4 - final engineering decision: AI on complaints, index on the database
import math
import os
import pickle
import random
import sqlite3
import time
from collections import Counter, defaultdict

import numpy as np
import pandas as pd

from complaints_data import COMPLAINTS
from sentiment import label, score, summarise, first_k, top_words, words_of, STOPWORDS

HERE = os.path.dirname(os.path.abspath(__file__))


# =====================================================================
# B4.1 - sentiment scorer and summariser on 54 complaints
# =====================================================================
def part_ai():
    print("=" * 74)
    print("B4.1 SENTIMENT SCORER on", len(COMPLAINTS), "complaints")
    print("=" * 74)
    texts = [t for t, _ in COMPLAINTS]
    truth = [l for _, l in COMPLAINTS]
    guess = [label(t) for t in texts]
    agree = sum(g == h for g, h in zip(guess, truth))
    print(f"agree with my own labels: {agree} of {len(texts)}  ({100 * agree / len(texts):.1f}%)")

    print("\nconfusion (rows = my label, columns = scorer):")
    kinds = ["positive", "negative", "neutral"]
    print(f"  {'':<10}" + "".join(f"{k:>10}" for k in kinds))
    for k in kinds:
        print(f"  {k:<10}" + "".join(f"{sum(1 for g, h in zip(guess, truth) if h == k and g == c):>10}" for c in kinds))

    print("\nwhere the scorer disagrees with me:")
    for t, g, h in zip(texts, guess, truth):
        if g != h:
            print(f"  me={h:<8} scorer={g:<8} | {t[:95]}")
    print("\nWhy: sarcasm, mixed opinions, negator not directly before the word ('not very good'),")
    print("and slang or words that are not in the word list. Questions and requests with a stray")
    print("positive word ('helpful staff ... not working') also get pushed to positive.")

    print("\n" + "=" * 74)
    print("B4.1 SUMMARISER: most-frequent-words vs first-two-sentences")
    print("=" * 74)
    important = set(top_words(texts, 12))
    print("12 most frequent important words:", sorted(important))
    show = [0, 1, 10, 24]
    for i in show:
        print(f"\ncomplaint {i + 1}: {texts[i]}")
        print(f"   frequent-words summary: {summarise(texts[i], important)}")
        print(f"   first-2-sentences     : {first_k(texts[i])}")

    def quality(fn):
        """average share of the complaint's own important words that survive in the summary"""
        shares, shorter = [], 0
        for t in texts:
            all_hits = [w for w in words_of(t) if w in important]
            if not all_hits:
                continue
            kept = [w for w in words_of(fn(t)) if w in important]
            shares.append(len(kept) / len(all_hits))
            shorter += len(fn(t)) < len(t)
        return sum(shares) / len(shares), shorter

    qa, sa = quality(lambda t: summarise(t, important))
    qb, sb = quality(first_k)
    print(f"\nshare of important-word mentions kept in the summary (higher = better):")
    print(f"   frequent-words method : {qa:.3f}   (summary shorter than original for {sa} complaints)")
    print(f"   first-k method        : {qb:.3f}   (summary shorter than original for {sb} complaints)")

    def per_complaint_time(fn, reps=300):
        t = time.perf_counter()
        for _ in range(reps):
            for text in texts:
                fn(text)
        return (time.perf_counter() - t) / (reps * len(texts))

    ts = per_complaint_time(label)
    tsum = per_complaint_time(lambda t: summarise(t, important))
    tk = per_complaint_time(first_k)
    print(f"\ntime per complaint:  sentiment {ts * 1e6:.1f} us | summariser {tsum * 1e6:.1f} us | first-k {tk * 1e6:.1f} us")
    print(f"projected for 50,000 complaints a month: sentiment {ts * 50000:.2f} s, summariser {tsum * 50000:.2f} s")

    # ---- alternative: naive Bayes, leave-one-out ----
    print("\n" + "=" * 74)
    print("ALTERNATIVE: a trained model (naive Bayes, written by hand) - leave-one-out test")
    print("=" * 74)

    def train(items):
        class_count = Counter(l for _, l in items)
        word_count = defaultdict(Counter)
        vocab = set()
        for t, l in items:
            for w in words_of(t):
                if w not in STOPWORDS:
                    word_count[l][w] += 1
                    vocab.add(w)
        return class_count, word_count, vocab

    def predict(model, text):
        class_count, word_count, vocab = model
        n = sum(class_count.values())
        best, best_lp = None, -1e18
        for c in class_count:
            total = sum(word_count[c].values())
            lp = math.log(class_count[c] / n)
            for w in words_of(text):
                if w in vocab:
                    lp += math.log((word_count[c][w] + 1) / (total + len(vocab)))
            if lp > best_lp:
                best, best_lp = c, lp
        return best

    right = 0
    for i, (t, l) in enumerate(COMPLAINTS):
        model = train(COMPLAINTS[:i] + COMPLAINTS[i + 1:])
        right += predict(model, t) == l
    print(f"naive Bayes leave-one-out accuracy on the same 54 complaints: {right} of 54 ({100 * right / 54:.1f}%)")
    model = train(COMPLAINTS)
    t = time.perf_counter()
    for _ in range(300):
        for text in texts:
            predict(model, text)
    tn = (time.perf_counter() - t) / (300 * len(texts))
    size_nb = len(pickle.dumps(model))
    size_lex = len(pickle.dumps(sorted(set(__import__("sentiment").POSITIVE) | set(__import__("sentiment").NEGATIVE))))
    print(f"time per complaint: {tn * 1e6:.1f} us (lexicon scorer: {ts * 1e6:.1f} us)")
    print(f"size of model: naive Bayes {size_nb / 1024:.1f} KB vs word list {size_lex / 1024:.2f} KB")
    print("note: only 54 training examples, so this is a rough guide. A real model needs thousands of")
    print("labelled complaints; a pre-trained language model would need hundreds of MB of memory.")


# =====================================================================
# B4.2 - index on (station, day)
# =====================================================================
def build_big_db(path, n_stations=120):
    if os.path.exists(path):
        os.remove(path)
    rng = np.random.default_rng(9)
    per = 365 * 24
    hours = np.arange(per)
    days = (pd.Timestamp("2025-01-01") + pd.to_timedelta(hours // 24, unit="D")).strftime("%Y-%m-%d").to_numpy()
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE readings (station TEXT, day TEXT, hour INTEGER, pm25 REAL)")
    for s in range(n_stations):
        pm = np.round(np.clip(rng.normal(40 + (s * 7) % 80, 15, per), 3, None), 1)
        con.executemany("INSERT INTO readings VALUES (?,?,?,?)",
                        zip([f"Station{s:03d}"] * per, days, (hours % 24).tolist(), pm.tolist()))
    con.commit()
    return con


def part_index():
    print("\n" + "=" * 74)
    print("B4.2 INDEX ON (station, day) - 120 stations x one year = 1,051,200 rows")
    print("=" * 74)
    path = os.path.join(HERE, "big.db")
    con = build_big_db(path)
    print("rows:", con.execute("SELECT COUNT(*) FROM readings").fetchone()[0])
    size_before = os.path.getsize(path)

    # slowest question: monthly average for one station
    query = "SELECT AVG(pm25) FROM readings WHERE station = ? AND day BETWEEN ? AND ?"
    params = [("Station%03d" % s, "2025-10-01", "2025-10-31") for s in range(0, 120, 6)]   # 20 different stations

    def run_all():
        t = time.perf_counter()
        results = [con.execute(query, p).fetchone()[0] for p in params]
        return (time.perf_counter() - t) / len(params), results

    print("\nquery: average PM2.5 of one station in October (20 different stations, averaged)")
    print("plan without index:", con.execute("EXPLAIN QUERY PLAN " + query, params[0]).fetchall()[0][-1])
    t_before, res_before = run_all()
    print(f"time per query WITHOUT index: {t_before * 1000:.2f} ms")

    t = time.perf_counter()
    con.execute("CREATE INDEX idx_station_day ON readings (station, day)")
    con.commit()
    t_build = time.perf_counter() - t
    size_after = os.path.getsize(path)
    print(f"index built in {t_build:.2f} s, file grew from {size_before / 1e6:.1f} MB to {size_after / 1e6:.1f} MB")
    print("plan with index   :", con.execute("EXPLAIN QUERY PLAN " + query, params[0]).fetchall()[0][-1])
    t_after, res_after = run_all()
    print(f"time per query WITH index   : {t_after * 1000:.3f} ms")
    print(f"speed-up: {t_before / t_after:.0f}x   (same answers: {res_before == res_after})")

    # CSV-style alternative: load everything into pandas just to answer one question
    t = time.perf_counter()
    df = pd.read_sql_query("SELECT * FROM readings", con)
    ans = df[(df.station == "Station000") & (df.day >= "2025-10-01") & (df.day <= "2025-10-31")]["pm25"].mean()
    t_pd = time.perf_counter() - t
    print(f"\nload-everything-into-pandas then filter (A1.3 alternative): {t_pd:.2f} s for ONE question,")
    print(f"   memory used by the DataFrame: {df.memory_usage(deep=True).sum() / 1e6:.0f} MB")

    # inserting more data with an index present
    rows = [("Station999", "2026-01-01", h % 24, 50.0) for h in range(200_000)]
    t = time.perf_counter(); con.executemany("INSERT INTO readings VALUES (?,?,?,?)", rows); con.commit()
    t_ins_with = time.perf_counter() - t
    con.execute("DROP INDEX idx_station_day")
    t = time.perf_counter(); con.executemany("INSERT INTO readings VALUES (?,?,?,?)", rows); con.commit()
    t_ins_without = time.perf_counter() - t
    print(f"\ntrade-off: inserting 200,000 rows takes {t_ins_with:.2f} s with the index and {t_ins_without:.2f} s without it")
    con.close()
    os.remove(path)

    return t_before, t_after


if __name__ == "__main__":
    part_ai()
    part_index()
