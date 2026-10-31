
# P05 — Quality Scenarios

## Stakeholders

- Guest — wants to book a room without conflicts.
- Receptionist — manages bookings and cancellations.
- Hotel Manager — wants reliable hotel operations.
- Developer — needs a system that is easy to maintain.

## Quality Scenarios

### S1 — Performance
When a guest searches for an available room, the system responds within 2 seconds under 100 concurrent requests.

### S2 — Reliability
When two guests try to reserve the same room for overlapping dates, only one reservation can be confirmed.

### S3 — Maintainability
A new room pricing rule can be added without changing the Notifications module.

### S4 — Availability
The booking system should be available at least 99.9% of the time per month.

### S5 — Security
An unauthorized user cannot cancel another guest's reservation.

### S6 — Testability
Each business context can be tested independently using automated tests.
