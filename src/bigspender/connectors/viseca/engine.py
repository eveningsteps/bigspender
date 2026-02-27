import datetime as dt
import os

import arrow
import requests

from bigspender.auth import cookies_for_domains
from bigspender.connectors import Transaction
from bigspender.connectors.viseca import model


def _parse_transactions(data: dict) -> list[model.VisecaTransaction]:
    response: model.VisecaTransactionsResponse = (
        model.VisecaTransactionsResponse.from_dict(data)
    )
    return response.list or []


class VisecaAccount:
    def fetch(self, card: str, dateFrom: dt.date, dateTo: dt.date) -> list[Transaction]:
        cookies = cookies_for_domains(
            ".one.viseca.ch",
            "one.viseca.ch",
        )

        url = f"https://api.one.viseca.ch/v1/reports/cards/{card}/transactions"
        response = requests.get(
            url,
            params={
                "stateType": "unknown",
                "offset": 0,
                "pagesize": 20,
                "dateFrom": arrow.get(dateFrom).format("YYYY-MM-DDT00:00:00") + "Z",
                "dateTo": arrow.get(dateTo).format("YYYY-MM-DDT23:59:59") + "Z",
            },
            cookies=cookies,
        )
        response.raise_for_status()

        raw = _parse_transactions(response.json())
        return [
            Transaction(
                date=arrow.get(t.date).date(),
                merchant=t.merchant(),
                amount=t.amount,
                scheduled=False,
            )
            for t in raw
            if dateFrom <= arrow.get(t.date).date() <= dateTo
        ]

    def dump(
        self,
        card: str,
        transactions: list[Transaction],
        path: str | None = None,
        sep=";",
    ):
        today = dt.date.today().strftime("%Y-%m-%d")
        out_path = path or f"./out/{today}-transactions-viseca-{card}.csv"

        os.makedirs(os.path.dirname(out_path), exist_ok=True)

        with open(out_path, "w") as fd:
            fd.write(
                "\n".join(
                    f"{t.date}{sep}{t.merchant}{sep}{t.amount}{sep}{t.scheduled}"
                    for t in transactions
                )
            )
