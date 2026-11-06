POSITIVE = {"good", "clean", "fast", "helpful", "improved"}
NEGATIVE = {"bad", "dirty", "slow", "rude", "smoke", "broken"}
NEGATORS = {"not", "never", "no"}


def score(text):
    """+1 per positive word, -1 per negative word; a preceding negator flips it."""
    words = text.lower().replace(".", " ").replace(",", " ").split()
    total = 0
    # TODO 1: For each word, find its value (+1, -1 or 0); if the previous word is a
    #   negator, flip the sign; add it to total
    for i, w in enumerate(words):
        if w in POSITIVE:
            value = 1
        elif w in NEGATIVE:
            value = -1
        else:
            value = 0
        if i > 0 and words[i - 1] in NEGATORS:
            value = -value
        total += value
    return total


def label(text):
    s = score(text)
    return "positive" if s > 0 else "negative" if s < 0 else "neutral"


for c in ["Roads are clean and the bus was fast.",
          "Smoke from the factory, air is bad.",
          "The staff were not helpful.",
          "Not bad, service improved."]:
    print(f"{label(c):8} | {c}")

print()
print("--- a complaint the scorer gets wrong ---")
wrong = "The bus was not very good."
print(f"{label(wrong):8} | {wrong}")
print("The person is unhappy (should be negative) but 'very' sits between 'not' and 'good',")
print("so the negator is no longer the previous word and 'good' counts as +1.")
