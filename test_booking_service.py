"""P06: tests preserving P04 booking behaviour."""

import unittest
from datetime import date

from hotel_booking.rooms import Room
from hotel_booking.reservations import (
    Guest,
    DateRange,
    BookingService,
)
from hotel_booking.reservations.internal import InMemoryReservationStore
from hotel_booking.notifications.internal import (
    EmailNotificationSender,
    SmsNotificationSender,
)


R7 = Room("R7", "Standard")
R8 = Room("R8", "Deluxe")

MAYA = Guest("Maya", "maya@example.com")
OMAR = Guest("Omar", "omar@example.com")
NORA = Guest("Nora", "nora@example.com")


def nov(check_in: int, check_out: int) -> DateRange:
    return DateRange(
        date(2026, 11, check_in),
        date(2026, 11, check_out)
    )


class FakeNotificationSender:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.sent: list[str] = []

    def send_confirmation(self, confirmation) -> None:
        if self.fail:
            raise RuntimeError("The mail server is down.")

        self.sent.append(confirmation.reservation_id)


def new_service(failing_sender: bool = False):
    store = InMemoryReservationStore()
    sender = FakeNotificationSender(failing_sender)

    return BookingService([R7, R8], store, sender), store, sender


class BookingServiceTests(unittest.TestCase):

    def test_maya_gets_r7_when_it_is_free(self):
        service, _, _ = new_service()

        self.assertEqual(
            "Accepted R101",
            str(service.reserve(MAYA, R7, nov(12, 14)))
        )

    def test_omar_is_refused_when_a_night_is_shared(self):
        service, store, _ = new_service()

        service.reserve(MAYA, R7, nov(12, 14))

        self.assertEqual(
            "Unavailable",
            str(service.reserve(OMAR, R7, nov(13, 15)))
        )

        self.assertEqual(1, store.count())

    def test_nora_can_arrive_on_the_day_maya_leaves(self):
        service, _, _ = new_service()

        service.reserve(MAYA, R7, nov(12, 14))

        self.assertEqual(
            "Accepted R102",
            str(service.reserve(NORA, R7, nov(14, 16)))
        )

    def test_check_out_must_be_after_check_in(self):
        service, store, _ = new_service()

        self.assertEqual(
            "InvalidDates",
            str(service.reserve(OMAR, R8, nov(15, 15)))
        )

        self.assertEqual(0, store.count())

    def test_cancelling_frees_the_room_again(self):
        service, _, _ = new_service()

        service.reserve(MAYA, R7, nov(12, 14))

        self.assertTrue(service.cancel("R101"))

        self.assertIn(
            R7,
            service.find_free_rooms(nov(12, 14))
        )

    def test_one_confirmation_per_accepted_booking(self):
        service, _, sender = new_service()

        service.reserve(MAYA, R7, nov(12, 14))
        service.reserve(OMAR, R7, nov(13, 15))
        service.reserve(NORA, R7, nov(14, 16))

        self.assertEqual(["R101", "R102"], sender.sent)

    def test_a_failed_confirmation_keeps_the_booking(self):
        service, store, _ = new_service(failing_sender=True)

        result = service.reserve(MAYA, R7, nov(12, 14))

        self.assertEqual("Accepted R101", str(result))
        self.assertTrue(result.notification_failed)
        self.assertEqual(1, store.count())

    def test_sms_confirmations_need_no_change_to_booking_service(self):
        sms = SmsNotificationSender()
        service = BookingService(
            [R7, R8],
            InMemoryReservationStore(),
            sms,
        )

        service.reserve(MAYA, R7, nov(12, 14))

        self.assertEqual(1, sms.sent)


if __name__ == "__main__":
    unittest.main()
