from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class PaymentRequest:
    reservation_id: str
    amount: int


@dataclass(frozen=True)
class PaymentResult:
    successful: bool
    transaction_id: str | None = None


class IPaymentProcessor(Protocol):
    def pay(self, request: PaymentRequest) -> PaymentResult:
        ...


__all__ = [
    "PaymentRequest",
    "PaymentResult",
    "IPaymentProcessor",
]