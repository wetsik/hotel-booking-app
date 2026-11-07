-- Rooms and Reservations own separate tables.
-- There is no foreign key between the modules.

CREATE TABLE rooms (
    number text PRIMARY KEY,
    type   text NOT NULL
);

CREATE TABLE reservations (
    id          text PRIMARY KEY,
    guest_name  text NOT NULL,
    guest_email text NOT NULL,
    room        text NOT NULL,
    check_in    date NOT NULL,
    check_out   date NOT NULL,
    status      text NOT NULL CHECK (status IN ('Confirmed', 'Cancelled')),
    CHECK (check_out > check_in)
);

INSERT INTO rooms (number, type)
VALUES ('R7', 'Standard'), ('R8', 'Deluxe');
