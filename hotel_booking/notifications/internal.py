from . import Confirmation


class EmailNotificationSender:
    """Simulates email delivery."""

    def __init__(self) -> None:
        self.sent = 0

    def send_confirmation(self, confirmation: Confirmation) -> None:
        self.sent += 1


class SmsNotificationSender:
    """Simulates SMS delivery."""

    def __init__(self) -> None:
        self.sent = 0

    def send_confirmation(self, confirmation: Confirmation) -> None:
        self.sent += 1