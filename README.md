# bigspender

Fetch bank transactions from BCGE and Viseca One, using browser cookies from your active sessions, and dump the data to CSV files suitable for further import (for example, into [Actual Budget](https://actualbudget.org/)).

> [!IMPORTANT]
> This script does NOT send your secrets anywhere other than the banking APIs, and only fetches the transactions based on existing short-lived access. You need to do the rest by yourself.

## Usage

1. Create your own `config.toml`, based on the existing example.
2. Log into your accounts through the browser and copy account IDs. Keep in mind that the cookies are valid only for a few minutes.
3. Set up and run the script:

```
uv sync
uv run bigspender
```

4. Fetched transactions will be saved in the `out` directory.

### Account IDs

| Provider | Account ID |
| :-- | :-- |
| [BCGE](https://www.bcge.ch/en/home) | Long hash string from HTML (`{ "accountId": "31d3...4094" }`). Changes on every login. |
| [Viseca One](https://one.viseca.ch) | Obscured card no. (example: `123456ABCDEF7890`). Constant. |
