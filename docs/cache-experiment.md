# Cache experiment: the free-room search

PostgreSQL is the source of truth.
Redis will cache availability results for 30 seconds.

## Measurements

1,000 sequential searches for 12-14 November 2026.

| Run | Searches | Database queries | Cache hits | Average | p95 |
|---|---|---|---|---|---|
| No cache | 1,000 | 2,000 | 0 | 10.6 ms | 14.8 ms |
| Cache-aside, TTL 30 s | 1,000 | 2 | 999 | 5.5 ms | 8.4 ms |

## Baseline observations

- Total measurement time: 10.6 seconds.
- Database queries per search: 2.
- Cache hits: 0.
- Cache misses: 0.
- S1 latency target: p95 <= 1,000 ms.
- Result: latency target met in the sequential test.
- Measurements were collected locally with tools/measure.py.

## Cache experiment observations

- Redis reduced average latency from 10.6 ms to 5.5 ms (48.1%).
- p95 decreased from 14.8 ms to 8.4 ms (43.2%).
- Database queries decreased from 2,000 to 2 (99.9%).
- Cache hits: 999.
- Cache misses: 1.
- Total execution time with Redis: 5.5 seconds.
- Energy savings have not been measured directly.

## Next experiment

Demonstrate a stale availability result after a successful booking.

## Stale result (Step 5, before invalidation)

1. Empty cache. Search 12-14 Nov: R7 and R8 (cache miss).
2. Maya books R7: HTTP 201, reservation R101.
3. Search again within 30 seconds: R7 and R8. STALE: R7 is already booked.
4. Omar tries to book R7: HTTP 409 Unavailable.

Booking reads PostgreSQL, not Redis, so double booking is prevented.
