# Capacity estimate: hotel booking app

These are estimates from assumptions, not measurements. P08 measures the real app.

## Assumptions

| Assumption | Value | Reason |
|---|---|---|
| Visitors per day | 1,440 | The booking page today: about one visitor a minute |
| Searches per visitor | 20 | Guests try several dates |
| Bookings per day | 20 | 40 rooms, most stays are two nights |
| Peak factor | 10 | Friday evenings and holiday sales |
| Queries per search | 40 | FindFreeRooms asks once per room |

## Results

| Number | Calculation | Result |
|---|---|---|
| Searches, average | 1,440 * 20 / 86,400 | 0.33 per second |
| Searches, peak | 0.33 * 10 | 3.33 per second = 200 a minute (S1) |
| Database queries, peak | 3.33 * 40 | 133 per second |
| Storage | 20 * 365 * 600 bytes | 4.38 MB a year |
| Bandwidth, peak | 3.33 * 2 KB; 0.17 * 2 MB | Search 6.67 KB/s, photos 333 KB/s |

## To measure later

- p95 of 1,000 searches for 12-14 Nov, target <= 1 s (S1): P08.
- Database queries per search (GET /stats): P08.
