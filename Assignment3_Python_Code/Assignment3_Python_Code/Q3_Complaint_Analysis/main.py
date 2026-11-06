import random
import string
import time
from collections import Counter

calls = [
    "seeds not received seeds delayed",
    "fertiliser price high",
    "seeds price high subsidy not received",
]
STOP = {"not", "high"}

def frequencies(texts, stop_words):
    counts = {}
    for line in texts:
        words = line.lower().translate(str.maketrans("", "", string.punctuation)).split()
        for word in words:
            if word not in stop_words:
                counts[word] = counts.get(word, 0) + 1
    return counts

def top(counts, k):
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:k]

print("Word counts:", frequencies(calls, STOP))
print("Top words:", top(frequencies(calls, STOP), 3))

# Group complaints by district.
complaints = [
    ("Kancheepuram", "seeds delayed"),
    ("Chennai", "fertiliser price high"),
    ("Kancheepuram", "water shortage"),
    ("Tiruvallur", "seeds not received"),
]
by_district = {}
for district, complaint in complaints:
    by_district.setdefault(district, []).append(complaint)
print("Complaints by district:", by_district)

# A small timing comparison. The list method is slower as data grows.
for size in (1000, 10000, 100000):
    words = [random.choice(["seed", "water", "price", "crop", "loan"]) for _ in range(size)]
    start = time.perf_counter()
    counts = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1
    dict_time = time.perf_counter() - start

    start = time.perf_counter()
    list_counts = {word: words.count(word) for word in set(words)}
    list_time = time.perf_counter() - start

    start = time.perf_counter()
    counter_counts = Counter(words)
    counter_time = time.perf_counter() - start

    print(f"{size} words: dict={dict_time:.5f}s, list.count={list_time:.5f}s, Counter={counter_time:.5f}s")
    assert counts == list_counts == dict(counter_counts)

# Empty text and case handling check.
print("Empty text:", frequencies([""], STOP))
print("Mixed case:", frequencies(["SEEDS Seeds, seeds!"], STOP))
