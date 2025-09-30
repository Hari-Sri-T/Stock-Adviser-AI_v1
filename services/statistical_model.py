import numpy as np
import yfinance as yf
import logging
def get_advanced_metrics(symbol):
    """
    Master function to fetch all statistical, valuation, and daily data for a stock.
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        # 1. Basic Stats (PE, PB) - Dividend Yield removed
        valuation_stats = {
            "PE Ratio": round(info.get("trailingPE"), 2) if info.get("trailingPE") else None,
            "PB Ratio": round(info.get("priceToBook"), 2) if info.get("priceToBook") else None,
        }

        # 2. Risk Calculation
        hist_6mo = ticker.history(period="6mo", auto_adjust=True)
        if not hist_6mo.empty:
            returns = hist_6mo['Close'].pct_change()
            volatility = returns.std() * np.sqrt(252)
            risk = round(float(volatility), 4)
        else:
            risk = None

        # 3. Valuation Models (Graham Number)
        eps = info.get("trailingEps")
        bvps = info.get("bookValue")
        graham_number = None
        if eps and bvps and eps > 0 and bvps > 0:
            graham_number = round(np.sqrt(22.5 * eps * bvps), 2)

        valuation_models = {
            "graham_number": graham_number
        }

        # 4. Latest Daily Data (OHLC, Volume)
        hist_1d = ticker.history(period="1d", auto_adjust=True)
        if not hist_1d.empty:
            daily_data = {
                "open": round(hist_1d['Open'].iloc[0], 2),
                "high": round(hist_1d['High'].iloc[0], 2),
                "low": round(hist_1d['Low'].iloc[0], 2),
                "volume": int(hist_1d['Volume'].iloc[0]) 
            }
        else:
            daily_data = {"open": None, "high": None, "low": None, "volume": None}

        return {
            "valuation_stats": valuation_stats,
            "risk": risk,
            "valuation_models": valuation_models,
            "daily_data": daily_data
        }

    except Exception as e:
        logging.error(f"Failed to get advanced metrics for {symbol}: {e}")
        return None