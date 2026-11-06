# word-list sentiment scorer and extractive summariser (used by B2 and B4)
import re
from collections import Counter

POSITIVE = {"good", "great", "clean", "fast", "helpful", "improved", "better", "excellent",
            "quick", "polite", "safe", "happy", "thanks", "fresh", "resolved", "pleasant"}
NEGATIVE = {"bad", "dirty", "slow", "rude", "smoke", "smoky", "broken", "terrible", "worse",
            "worst", "dust", "dusty", "noise", "noisy", "stink", "smell", "burning", "ignored",
            "unsafe", "delay", "delayed", "pollution", "polluted", "choking", "toxic", "blocked"}
NEGATORS = {"not", "never", "no", "isnt", "wasnt", "didnt", "dont", "cant", "cannot"}

STOPWORDS = {"the", "a", "an", "is", "are", "was", "were", "and", "or", "of", "to", "in", "on",
             "at", "for", "it", "this", "that", "from", "with", "by", "be", "been", "has", "have",
             "had", "very", "so", "but", "as", "my", "our", "we", "i", "you", "they", "there",
             "again", "also", "still", "every", "all", "since", "near", "after", "while"}


def words_of(text):
    text = text.lower().replace("'", "")             # isn't -> isnt
    return re.findall(r"[a-z0-9]+", text)


def score(text):
    """+1 per positive word, -1 per negative word; a negator right before a word flips it."""
    words = words_of(text)
    total = 0
    for i, w in enumerate(words):
        value = 1 if w in POSITIVE else -1 if w in NEGATIVE else 0
        if value and i > 0 and words[i - 1] in NEGATORS:
            value = -value
        total += value
    return total


def label(text):
    s = score(text)
    return "positive" if s > 0 else "negative" if s < 0 else "neutral"


def sentences_of(text):
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p]


def top_words(texts, k=10):
    counts = Counter(w for t in texts for w in words_of(t) if w not in STOPWORDS and len(w) > 2)
    return [w for w, _ in counts.most_common(k)]


def summarise(text, important, n_sentences=2):
    """Pick the n sentences that contain the most 'important' (frequent) words."""
    sents = sentences_of(text)
    if len(sents) <= n_sentences:
        return " ".join(sents)
    scored = []
    for i, s in enumerate(sents):
        hits = sum(1 for w in words_of(s) if w in important)
        scored.append((hits, -i, s))                  # more hits first, earlier sentence wins ties
    best = sorted(scored, reverse=True)[:n_sentences]
    chosen = sorted(best, key=lambda x: -x[1])        # keep original order
    return " ".join(s for _, _, s in chosen)


def first_k(text, n_sentences=2):
    return " ".join(sentences_of(text)[:n_sentences])
