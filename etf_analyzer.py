#!/usr/bin/env python3
"""
ETF Analyzer — heat chart of key indicators for top 10 ETF holdings.
Usage: python etf_analyzer.py [TICKER]   (default: XLE)
"""

import sys
import warnings
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Top 10 holdings for common ETFs (fallback if yfinance can't scrape them)
# ---------------------------------------------------------------------------
KNOWN_HOLDINGS = {
    "XLE": [
        "XOM", "CVX", "EOG", "SLB", "MPC",
        "PSX", "PXD", "VLO", "WMB", "OXY",
    ],
}


def get_holdings(etf_ticker: str) -> list[str]:
    """Return top 10 holdings for the ETF."""
    ticker = etf_ticker.upper()
    if ticker in KNOWN_HOLDINGS:
        return KNOWN_HOLDINGS[ticker]
    # Generic attempt via yfinance (works for some ETFs)
    try:
        etf = yf.Ticker(ticker)
        holdings = etf.funds_data.top_holdings
        if holdings is not None and not holdings.empty:
            return holdings.index.tolist()[:10]
    except Exception:
        pass
    print(f"[WARN] Could not fetch holdings for {ticker}. Add them to KNOWN_HOLDINGS.")
    sys.exit(1)


def fetch_indicators(symbols: list[str]) -> pd.DataFrame:
    """Pull Trailing P/E, Forward P/E, price, and 52-wk range from yfinance."""
    rows = []
    for sym in symbols:
        info = yf.Ticker(sym).info
        trailing_pe = info.get("trailingPE")
        forward_pe  = info.get("forwardPE")
        current     = info.get("currentPrice") or info.get("regularMarketPrice")
        week52_high = info.get("fiftyTwoWeekHigh")
        week52_low  = info.get("fiftyTwoWeekLow")

        ratio = None
        if trailing_pe and forward_pe and forward_pe != 0:
            ratio = round(trailing_pe / forward_pe, 2)

        rows.append({
            "Symbol":         sym,
            "Trailing P/E":   trailing_pe,
            "Forward P/E":    forward_pe,
            "TTM/Fwd Ratio":  ratio,
            "52W High":       week52_high,
            "52W Low":        week52_low,
            "Current Price":  current,
        })
        print(f"  {sym}: trailing={trailing_pe}, forward={forward_pe}, price={current}")

    return pd.DataFrame(rows).set_index("Symbol")


def normalize(series: pd.Series) -> pd.Series:
    """Min-max normalize a series to [0, 1], NaN stays NaN."""
    mn, mx = series.min(), series.max()
    if mx == mn:
        return series * 0.5
    return (series - mn) / (mx - mn)


def plot_heat_chart(df: pd.DataFrame, etf_ticker: str) -> None:
    pe_cols   = ["Trailing P/E", "Forward P/E", "TTM/Fwd Ratio"]
    price_cols = ["52W High", "Current Price", "52W Low"]
    all_cols  = pe_cols + price_cols

    # Build normalized matrix (each column normalized independently)
    norm_df = df[all_cols].copy()
    for col in all_cols:
        norm_df[col] = normalize(df[col])

    fig, ax = plt.subplots(figsize=(13, 6))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")

    cmap = plt.cm.RdYlGn
    mat  = norm_df.values.astype(float)

    im = ax.imshow(mat, cmap=cmap, aspect="auto", vmin=0, vmax=1)

    # Axes labels
    ax.set_xticks(range(len(all_cols)))
    ax.set_xticklabels(all_cols, color="white", fontsize=10, rotation=25, ha="right")
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(df.index, color="white", fontsize=11, fontweight="bold")

    # Cell annotations — show the raw value
    for r, sym in enumerate(df.index):
        for c, col in enumerate(all_cols):
            val = df.loc[sym, col]
            if pd.isna(val):
                label = "N/A"
            elif col in price_cols:
                label = f"${val:,.2f}"
            else:
                label = f"{val:.2f}"
            brightness = mat[r, c] if not np.isnan(mat[r, c]) else 0.5
            txt_color = "black" if 0.35 < brightness < 0.75 else "white"
            ax.text(c, r, label, ha="center", va="center",
                    color=txt_color, fontsize=9, fontweight="bold")

    # Divider between P/E block and price block
    ax.axvline(x=2.5, color="#0d1117", linewidth=3)

    # Column group labels
    ax.text(1, -0.9, "── Valuation ──", ha="center", va="center",
            color="#aaaaaa", fontsize=9, transform=ax.transData)
    ax.text(4, -0.9, "── Price Range ──", ha="center", va="center",
            color="#aaaaaa", fontsize=9, transform=ax.transData)

    cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label("Relative rank within column  (green = higher)", color="white", fontsize=9)
    cbar.ax.yaxis.set_tick_params(color="white")
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color="white")

    ax.set_title(f"{etf_ticker} — Top 10 Holdings Heat Chart",
                 color="white", fontsize=15, fontweight="bold", pad=18)

    plt.tight_layout()
    out_file = f"{etf_ticker.lower()}_heat_chart.png"
    plt.savefig(out_file, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"\nChart saved → {out_file}")
    plt.show()


def main():
    ticker = sys.argv[1].upper() if len(sys.argv) > 1 else "XLE"
    print(f"\nFetching top 10 holdings for {ticker}...")
    holdings = get_holdings(ticker)
    print(f"Holdings: {holdings}\n")
    print("Fetching indicators...")
    df = fetch_indicators(holdings)
    print("\n--- Raw Data ---")
    print(df.to_string())
    plot_heat_chart(df, ticker)


if __name__ == "__main__":
    main()
