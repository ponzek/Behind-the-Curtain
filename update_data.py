"""Download daily OHLCV data for PLTR, LMT, RTX from Yahoo Finance and save to data/prices.csv."""
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

TICKERS = ["PLTR", "LMT", "RTX"]
OUT = Path(__file__).parent / "data" / "prices.csv"


def fetch_ticker(ticker: str, years: int = 5) -> pd.DataFrame:
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        f"?range={years}y&interval=1d&events=history"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        res = json.load(r)["chart"]["result"][0]
    q = res["indicators"]["quote"][0]
    adj = res["indicators"].get("adjclose", [{}])[0].get("adjclose", q["close"])
    df = pd.DataFrame(
        {
            "Date": [datetime.fromtimestamp(t, timezone.utc).date() for t in res["timestamp"]],
            "Ticker": ticker,
            "Close": adj,
            "Volume": q["volume"],
        }
    )
    return df.dropna()


def main():
    frames = []
    for t in TICKERS:
        frames.append(fetch_ticker(t))
        time.sleep(0.5)
    df = pd.concat(frames).drop_duplicates(["Date", "Ticker"])
    OUT.parent.mkdir(exist_ok=True)
    df.to_csv(OUT, index=False)
    print(df.groupby("Ticker")["Date"].agg(["min", "max", "count"]))


if __name__ == "__main__":
    main()
