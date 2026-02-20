import datetime
from dataclasses import dataclass


@dataclass
class Transaction:
    date: datetime.date
    merchant: str
    amount: float
    scheduled: bool
