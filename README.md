# P03 — Hotel booking app

Modular Python version of the P03 tutorial. No dependencies beyond Python 3.10+.

Run from the project root:

```powershell
python hotel_booking.py
python hotel_booking.py --race
```

The `--race` example deliberately demonstrates a double-booking bug for Step 8. Do not add a lock until that step.

`domain/` contains hotel rules and entities; `application/` coordinates use cases; `infrastructure/` provides in-memory storage and simulated email; `demo.py` drives the examples.
