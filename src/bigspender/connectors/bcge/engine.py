import datetime as dt
import os

import requests

from bigspender.auth import cookies_for_domains
from bigspender.connectors import Transaction
from bigspender.connectors.bcge import model


def _flatten_bookingstimegroup_response(data: dict) -> list[model.BCGEBooking]:
    groups: model.BCGEBookingsTimegroupResponse = (
        model.BCGEBookingsTimegroupResponse.from_dict(data)
    )
    out = []
    for g in groups.data:
        if g.items is not None:
            out += g.items
    return out


def _flatten_scheduledbookings_response(data: dict) -> list[model.BCGEScheduledBooking]:
    events: model.BCGEScheduledBookingsResponse = (
        model.BCGEScheduledBookingsResponse.from_dict(data)
    )
    return events.data or []


class BCGEAccount:
    def fetch(
        self, accountId: str, dateFrom: dt.date, dateTo: dt.date
    ) -> list[Transaction]:
        cookies = cookies_for_domains(
            ".bcge.ch",
            "connect.bcge.ch",
            "www.bcge.ch",
        )

        url = f"https://www.bcge.ch/next/api/v4/accounts/{accountId}/bookingstimegroup"
        response = requests.get(
            url,
            params={
                "group": "MONTH",
                "firstGroupsWithDetails": 3,
                "limit": 100,
            },
            cookies=cookies,
        )
        response.raise_for_status()
        completed = _flatten_bookingstimegroup_response(response.json())
        completed = [
            Transaction(
                date=e.valueDate.to("local").date(),
                merchant=e.merchant(),
                amount=e.signed_amount(),
                scheduled=False,
            )
            for e in completed
            if dateFrom <= e.valueDate.to("local").date() <= dateTo
        ]

        url = f"https://www.bcge.ch/next/api/v4/accounts/{accountId}/scheduledbookings"
        response = requests.get(url, cookies=cookies)
        response.raise_for_status()
        scheduled = _flatten_scheduledbookings_response(response.json())
        scheduled = [
            Transaction(
                date=e.valueDate.to("local").date(),
                merchant=e.merchant(),
                amount=e.signed_amount(),
                scheduled=True,
            )
            for e in scheduled
            if dateFrom <= e.valueDate.to("local").date() <= dateTo
        ]

        result = completed + scheduled
        result.sort(key=lambda t: t.date, reverse=True)
        return result

    def dump(
        self,
        account_id: str,
        transactions: list[Transaction],
        path: str | None = None,
        sep=";",
    ):
        today = dt.date.today().strftime("%Y-%m-%d")
        out_path = path or f"./out/{today}-transactions-bcge-{account_id}.csv"

        os.makedirs(os.path.dirname(out_path), exist_ok=True)

        with open(out_path, "w") as fd:
            fd.write(
                "\n".join(
                    f"{t.date}{sep}{t.merchant}{sep}{t.amount}{sep}{t.scheduled}"
                    for t in transactions
                )
            )
