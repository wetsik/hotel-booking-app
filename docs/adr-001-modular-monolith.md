# ADR-001: Modular Monolith

## Status
Accepted

## Context
The Hotel Booking application was previously organized
into technical layers: domain, application, infrastructure.

In P05, four bounded contexts were identified:
Rooms, Reservations, Payments, and Notifications.

The code needed explicit module boundaries to prevent
unwanted dependencies.

## Decision
We will use a Modular Monolith architecture.

The application is divided into four business modules:
- Rooms
- Reservations
- Payments
- Notifications

Each module exposes public contracts through __init__.py.

Internal implementations are kept in internal.py.

The main.py file is the Composition Root.
It creates implementations and injects dependencies.

Import Linter checks the module boundaries automatically.

## Consequences

### Positive
- Clear separation of responsibilities.
- Easier testing and maintenance.
- Implementations can be replaced.
- Architecture violations are detected automatically.

### Negative
- More files and interfaces.
- Additional architecture configuration.
- Developers must respect module boundaries.

## Verification
- 8 unit tests pass.
- Original demo behaviour is preserved.
- Race Condition demonstration is preserved.
- Import Linter: 3 kept, 0 broken.