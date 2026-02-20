import datetime
import re
import tomllib
from pathlib import Path

from bigspender.connectors.bcge import BCGEAccount
from bigspender.connectors.viseca import VisecaAccount

STATE_FILE = Path(".bigspender.state")


def parse_date_range(cfg: dict) -> tuple[datetime.date, datetime.date]:
    today = datetime.date.today()

    if cfg.get("mode") == "incremental":
        if STATE_FILE.exists():
            with open(STATE_FILE, "rb") as f:
                state = tomllib.load(f)
            last_run = datetime.date.fromisoformat(state["last_run"])
            return last_run, today

    if "range" in cfg:
        m = re.fullmatch(r"(\d+)([dwm])", cfg["range"])
        if not m:
            raise ValueError(
                f"Invalid date.range format: {cfg['range']!r} (valid examples: '14d', '2w', '1m')"
            )
        n, unit = int(m.group(1)), m.group(2)
        days = {"d": n, "w": n * 7, "m": n * 30}[unit]
        return today - datetime.timedelta(days=days), today

    if "from" in cfg and "to" in cfg:
        return datetime.date.fromisoformat(cfg["from"]), datetime.date.fromisoformat(
            cfg["to"]
        )

    raise ValueError("[date] must be either 'range', or 'from' + 'to'")


def save_last_run(date: datetime.date) -> None:
    STATE_FILE.write_text(f'last_run = "{date.isoformat()}"\n')


def main():
    with open("config.toml", "rb") as f:
        config = tomllib.load(f)

    date_cfg = config.get("date", {})
    date_from, date_to = parse_date_range(date_cfg)
    incremental = date_cfg.get("mode") == "incremental"

    print(f"Fetching transactions from {date_from} to {date_to}")

    accounts = config.get("account", [])

    for acc in accounts:
        acc_id = acc["id"]

        match acc["type"]:
            case "viseca":
                connector = VisecaAccount()
            case "bcge":
                connector = BCGEAccount()
            case unknown:
                raise ValueError(f"Unknown account type: {unknown!r}")
        transactions = connector.fetch(acc_id, dateFrom=date_from, dateTo=date_to)
        connector.dump(acc_id, transactions)

    if incremental:
        save_last_run(date_to)


if __name__ == "__main__":
    main()
