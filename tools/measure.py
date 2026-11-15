"""Measure 1,000 HTTP searches and compare GET /stats counters."""

import http.client
import json
import math
import sys
import time

SEARCHES = 1000
NAMES = ("searches", "databaseQueries", "cacheHits", "cacheMisses")

check_in, check_out = (
    sys.argv[1:3]
    if len(sys.argv) >= 3
    else ("2026-11-12", "2026-11-14")
)

connection = http.client.HTTPConnection("localhost", 5080)


def get(path: str) -> str:
    connection.request("GET", path)
    response = connection.getresponse()
    body = response.read().decode("utf-8")

    if response.status != 200:
        sys.exit(f"GET {path} answered {response.status}: {body}")

    return body


before = json.loads(get("/stats"))

times = []
started = time.perf_counter()

for _ in range(SEARCHES):
    start = time.perf_counter()

    get(
        f"/rooms/availability?"
        f"checkIn={check_in}&checkOut={check_out}"
    )

    times.append((time.perf_counter() - start) * 1000)

total = time.perf_counter() - started

after = json.loads(get("/stats"))
connection.close()

times.sort()

p95 = times[math.ceil(0.95 * SEARCHES) - 1]

difference = ",".join(
    f'"{name}":{after[name] - before[name]}'
    for name in NAMES
)

print(f"{SEARCHES} searches for {check_in} to {check_out}")
print(f"Average: {sum(times) / SEARCHES:.1f} ms")
print(f"p95: {p95:.1f} ms")
print(f"Total: {total:.1f} s")
print(f"GET /stats difference: {{{difference}}}")
