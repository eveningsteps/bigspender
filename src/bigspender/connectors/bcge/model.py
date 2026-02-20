from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
import re

import arrow


@dataclass_json
@dataclass
class BCGEAmount:
    value: float | None
    currency: str


@dataclass_json
@dataclass
class BCGEBooking:
    id: str
    valueDate: arrow.Arrow = field(metadata=config(decoder=arrow.get))
    description: str
    type: str
    bookingAmount: BCGEAmount
    balance: BCGEAmount
    isWagePayment: bool
    area: str
    amount: BCGEAmount | None
    beneficiaryAddress: list[str] | None
    senderAddress: list[str] | None
    notification: list[str]

    def date(self) -> str:
        return self.valueDate.format("YYYY-MM-DD")

    def signed_amount(self) -> float:
        val = self.bookingAmount.value or 0.0
        match self.type:
            case "DEBIT":
                return -val
            case "CREDIT":
                return val
            case _:
                raise ValueError(f"Unknown BCGE transaction type for {self}")

    def merchant(self) -> str:
        # Explicit wage payment flag
        if self.isWagePayment:
            return "Salary"

        desc = self.description

        # Card payment / refund:
        # "Paiement 18.02.2026 11:25 SBB EasyRide Card number: 111111******1111"
        # "Paiement 15.02.2026 12:43 Coop Zurich Card number: ... Amount: USD 21.62"
        # "Remboursement 08.01.2026 00:00 PAYPAL *MERCHNT Card number: ..."
        card_match = re.match(
            r"^(?:Paiement|Payment|Remboursement)\s+\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}\s+(.+?)\s+Card number:",
            desc,
        )
        if card_match:
            return card_match.group(1)

        # Twint: "Twint Zalando 04000..."
        twint_match = re.match(r"^Twint\s+(.+?)\s+\d{10,}$", desc)
        if twint_match:
            return twint_match.group(1)

        # Payment order / Standing order / Debit LSV+ — use beneficiary name
        if self.beneficiaryAddress:
            return self.beneficiaryAddress[0]

        # Credit — use sender name
        if self.type == "CREDIT" and self.senderAddress:
            addr = self.senderAddress
            if addr and addr[0].startswith("/"):
                # First element is IBAN-like ("/C/CH..."), name is at index 1
                return addr[1] if len(addr) > 1 else desc
            elif addr:
                return addr[0]

        return desc


@dataclass_json
@dataclass
class BCGEBookingsTimegroup:
    timeGroupId: str
    year: int
    month: int
    day: int | None
    kind: str
    nrOfDays: int
    hasMore: bool
    items: list[BCGEBooking] | None


@dataclass_json
@dataclass
class BCGEBookingsTimegroupResponse:
    data: list[BCGEBookingsTimegroup]


@dataclass_json
@dataclass
class BCGEScheduledBooking:
    id: str
    valueDate: arrow.Arrow = field(metadata=config(decoder=arrow.get))
    description: str
    type: str
    bookingAmount: BCGEAmount
    balance: BCGEAmount

    def date(self) -> str:
        return self.valueDate.format("YYYY-MM-DD")

    def signed_amount(self) -> float:
        val = self.bookingAmount.value or 0.0
        match self.type:
            case "DEBIT":
                return -val
            case "CREDIT":
                return val
            case _:
                raise ValueError(f"Unknown BCGE transaction type for {self}")

    def merchant(self) -> str:
        # "Purchase CHF, Coop-1240 Zurich Zurich, 19.02.2026 14:22, card: 111111******1111"
        purchase_match = re.match(
            r"^Purchase\s+\w+,\s+(.+),\s+\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2},\s+card:",
            self.description,
        )
        if purchase_match:
            return purchase_match.group(1)
        return self.description


@dataclass_json
@dataclass
class BCGEScheduledBookingsResponse:
    data: list[BCGEScheduledBooking]
