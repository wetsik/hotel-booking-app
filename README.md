# P03 — Hotel booking app

Modular Python version of the P03 tutorial. No dependencies beyond Python 3.10+.

Run from the project root:

```powershell
python hotel_booking.py
python hotel_booking.py --race
```

The `--race` example deliberately demonstrates a double-booking bug for Step 8. The `--race` example deliberately demonstrates a race condition that can cause double booking. This issue is intentionally left unresolved in P03 and will be addressed in P09 using database concurrency controls.

`domain/` contains hotel rules and entities; `application/` coordinates use cases; `infrastructure/` provides in-memory storage and simulated email; `demo.py` drives the examples.
