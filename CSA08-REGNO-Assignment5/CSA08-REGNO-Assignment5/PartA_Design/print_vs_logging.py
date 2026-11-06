# supporting measurement for A4 (not a replacement for the pseudocode in PartA_Design.md)
# how much time do thousands of print() / logging calls add to a cleaning loop?
import io
import logging
import sys
import time

N = 200_000
data = [float(i % 300) - 20 for i in range(N)]       # some negative values to "report"


def plain():
    bad = 0
    for v in data:
        if v < 0:
            bad += 1
    return bad


def with_print():
    bad = 0
    for v in data:
        if v < 0:
            bad += 1
            print("negative reading", v)
    return bad


def with_logging():
    bad = 0
    for v in data:
        if v < 0:
            bad += 1
            log.debug("negative reading %s", v)
    return bad


def timed(fn):
    t = time.perf_counter()
    r = fn()
    return time.perf_counter() - t, r


log = logging.getLogger("clean")
log.propagate = False
handler = logging.StreamHandler(io.StringIO())
log.addHandler(handler)

print(f"readings: {N}, of which {plain()} are negative (each one is reported)\n")
t0, _ = timed(plain)

real_stdout = sys.stdout
sys.stdout = io.StringIO()                      # so the output does not flood the screen
t1, _ = timed(with_print)
sys.stdout = real_stdout

log.setLevel(logging.DEBUG)
t2, _ = timed(with_logging)
log.setLevel(logging.WARNING)                    # switched off with ONE line
t3, _ = timed(with_logging)

print(f"{'version':<44}{'time':>9}{'extra':>9}")
print(f"{'no reporting at all':<44}{t0:>8.4f}s{'':>9}")
print(f"{'print() for every negative reading':<44}{t1:>8.4f}s{t1 - t0:>8.4f}s")
print(f"{'logging.debug, level DEBUG (switched on)':<44}{t2:>8.4f}s{t2 - t0:>8.4f}s")
print(f"{'logging.debug, level WARNING (switched off)':<44}{t3:>8.4f}s{t3 - t0:>8.4f}s")
print("\nprint() has to be deleted or commented out by hand; logging is switched off by changing the level.")
