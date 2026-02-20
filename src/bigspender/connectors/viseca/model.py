from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class VisecaPfmCategory:
    id: str
    name: str
    description: str
    lightColor: str
    mediumColor: str
    color: str
    imageUrl: str
    transparentImageUrl: str


@dataclass_json
@dataclass
class VisecaTransaction:
    transactionId: str
    date: str
    amount: float
    currency: str
    isBilled: bool
    stateType: str
    details: str
    type: str
    showTimestamp: bool
    pfmCategory: VisecaPfmCategory
    originalAmount: float | None = None
    originalCurrency: str | None = None
    merchantName: str | None = None
    prettyName: str | None = None
    isOnline: bool | None = None
    conversionRate: float | None = None
    conversionRateDate: str | None = None
    approved3DS: bool | None = None
    cardId: str | None = None
    maskedCardNumber: str | None = None
    valutaDate: str | None = None
    productScheme: str | None = None
    mcc: str | None = None
    mccpfm: str | None = None
    cardAccountNr: str | None = None

    def date_str(self) -> str:
        return self.date.split("T")[0]

    def merchant(self) -> str:
        return (self.merchantName or self.details or self.type or "Unknown").replace(
            ",", " "
        )


@dataclass_json
@dataclass
class VisecaTransactionsResponse:
    totalCount: int
    list: list[VisecaTransaction]
