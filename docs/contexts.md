
# P05 — Bounded Contexts

## Step 2 — The Hotel's Words

| Term | Meaning |
|---|---|
| Room | A hotel room that guests can book. |
| Room ID | A unique identifier for a room, e.g. R7. |
| Room Type | A category such as Standard or Deluxe. |
| Guest | A person who books a room. |
| Reservation | A booking made by a guest. |
| Stay | The period between check-in and check-out. |
| Check-in | The date a guest starts their stay. |
| Check-out | The date a guest leaves the room. |
| Available | A room can be booked for the requested dates. |
| Unavailable | A room cannot be booked for the requested dates. |
| Confirmed | A reservation has been accepted. |
| Cancelled | A reservation is no longer active. |
| Overlap | Two reservations share at least one night. |
| Price | The cost of staying in a room. |
| Deposit | An advance payment for a reservation. |
| Payment | Money received from a guest. |
| Refund | Money returned to a guest. |
| Notification | A message sent to a guest. |
| Email | A notification delivered by email. |
| SMS | A notification delivered by text message. |
| Sent | A notification was sent through a channel. |



## Step 3 — Four Bounded Contexts

### 1. Rooms

**Responsibility:** Manages physical hotel rooms,
room types, and maintenance status.

**Owns:**
- Room ID
- Room Type
- Room Status
- Maintenance Schedule

**Rules:**
- Each room must have a unique ID.
- Rooms under maintenance cannot be booked.

### 2. Reservations

**Responsibility:** Manages bookings, guest stays,
reservation dates, and cancellations.

**Owns:**
- Reservation
- Guest
- Stay
- Check-in and Check-out
- Reservation Status

**Rules:**
- Check-out must be after check-in.
- Confirmed reservations cannot overlap.
- Cancelled reservations do not block dates.

### 3. Payments

**Responsibility:** Manages pricing, deposits,
payments, and refunds.

**Owns:**
- Price
- Deposit
- Payment
- Refund
- Payment Status

**Rules:**
- Payment amounts must be valid.
- Deposit requirements follow hotel policy.

### 4. Notifications

**Responsibility:** Manages booking notifications
sent through email or SMS.

**Owns:**
- Notification
- Email
- SMS
- Delivery Status

**Rules:**
- Booking confirmations trigger notifications.
- Failed notification attempts are recorded.



## Step 4 — Same Word, Different Meaning

### Room

- Rooms: A physical hotel room with a type, ID,
  and maintenance status.
- Reservations: A room identified by Room ID
  and reserved for a specific stay period.

### Cancel

- Reservations: Cancel an existing reservation.
- Payments: Cancel a pending payment or
  process a refund when appropriate.
- Notifications: Cancel a scheduled message
  that has not yet been sent.

### Confirmed / Paid / Sent

- Confirmed (Reservations): The booking has
  been successfully accepted.
- Paid (Payments): The required payment
  has been completed.
- Sent (Notifications): The message has been
  submitted to the delivery channel.

These statuses are independent.

A confirmed reservation does not automatically
mean that a payment is completed or that
a notification has been delivered.



## Step 5 — Rule Owners

| Rule | Owner | Reason |
|---|---|---|
| R1: Every room has a unique ID. | Rooms | Rooms manages room identities. |
| R2: A room under maintenance is unavailable. | Rooms | Rooms owns maintenance information. |
| R3: Check-out must be after check-in. | Reservations | Reservations validates stay dates. |
| R4: Confirmed reservations cannot overlap. | Reservations | Reservations owns booking conflicts. |
| R5: Deluxe rooms have a different nightly price. | Payments | Payments owns pricing rules in this design. |
| R6: A booking may require a 30% deposit. | Payments | Payments manages deposits. |
| R7: A guest receives a booking confirmation message. | Notifications | Notifications manages message delivery. |
| R8: Failed notifications must be recorded. | Notifications | Notifications tracks delivery failures. |

### Booking Rule

Reservations owns the rule that prevents
overlapping confirmed reservations.

Rooms provides room information and
maintenance status.

Payments manages financial requirements.

Notifications sends confirmation messages.

Each rule has one primary business owner.
Other contexts communicate with that owner
instead of duplicating its rules.



## Step 7 — Between Contexts

### 1. Reservations → Rooms

**Purpose:** Check whether a room exists and is
operational for the requested stay dates.

**Request: CheckRoomStatus**
- roomId: string
- checkIn: date
- checkOut: date

**Response:**
- exists: boolean
- operational: boolean
- reason: string (optional)

Reservations uses this information to decide
whether a booking request can continue.

### 2. Reservations → Payments

**Purpose:** Calculate the booking price and
request the required deposit.

**Request: RequestDeposit**
- reservationId: string
- roomType: string
- nights: integer
- amount: decimal
- currency: string

**Response:**
- paymentId: string
- paymentStatus: string
- paidAmount: decimal

Payments owns pricing, deposits and payment
processing rules.

### 3. Reservations → Notifications

**Purpose:** Request a booking confirmation
message after a reservation is confirmed.

**Event: ReservationConfirmed**
- reservationId: string
- guestContact: string
- roomId: string
- checkIn: date
- checkOut: date

Notifications uses this event to create and
send a message to the guest.

### Integration Principles

- Each context owns its business rules.
- Contexts exchange only necessary data.
- Reservations does not manage payments directly.
- Notifications does not modify reservations.
- A notification failure does not automatically
  cancel a confirmed reservation.
