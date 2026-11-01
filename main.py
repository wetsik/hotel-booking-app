from hotel_booking.rooms import Room
from hotel_booking.reservations import BookingService
from hotel_booking.reservations.internal import InMemoryReservationStore
from hotel_booking.notifications.internal import EmailNotificationSender
from hotel_booking.payments.internal import SimulatedPaymentProcessor


def create_application(slow_step_seconds: float = 0):
    rooms = [
        Room("R7", "Standard"),
        Room("R8", "Deluxe"),
    ]

    store = InMemoryReservationStore()
    notifications = EmailNotificationSender()
    payments = SimulatedPaymentProcessor()

    booking_service = BookingService(
        rooms=rooms,
        store=store,
        email=notifications,
        slow_step_seconds=slow_step_seconds,
    )

    return booking_service, store, notifications, payments


def main():
    service, store, notifications, payments = create_application()

    print("Hotel Booking Application")
    print(f"Rooms available: {len(service.rooms)}")
    print(f"Reservations: {store.count()}")
    print(f"Notifications sent: {notifications.sent}")
    print(f"Payments processed: {payments.transactions}")


if __name__ == "__main__":
    main()