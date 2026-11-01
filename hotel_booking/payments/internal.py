from . import PaymentRequest, PaymentResult


class SimulatedPaymentProcessor:
    """Simulates payments without transferring real money."""

    def __init__(self) -> None:
        self.transactions = 0

    def pay(self, request: PaymentRequest) -> PaymentResult:
        self.transactions += 1

        return PaymentResult(
            successful=True,
            transaction_id=f"TX{self.transactions:03d}",
        )