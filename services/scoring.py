def get_price_trend_score(predicted_close, last_close):
    """ Converts price trend into score (0–100). """
    pct_change = ((predicted_close - last_close) / last_close) * 100
    if pct_change > 2: return 90
    elif pct_change > 0.5: return 70
    elif pct_change > -0.5: return 50
    elif pct_change > -2: return 30
    else: return 10

def get_valuation_score(current_price, graham_number):
    """
    Converts Graham Number valuation into a score (0-100).
    A high score means the stock is undervalued.
    """
    if graham_number is None or current_price is None:
        return 50  # Neutral if data is unavailable

    if current_price < graham_number * 0.75: # Significantly undervalued
        return 90
    elif current_price < graham_number: # Undervalued
        return 75
    elif current_price < graham_number * 1.25: # Fairly valued
        return 50
    elif current_price < graham_number * 1.5: # Overvalued
        return 30
    else: # Significantly overvalued
        return 10

def combine_scores(trend_score, sentiment_score, valuation_score,
                   w_trend=0.3, w_sentiment=0.4, w_valuation=0.3):
    """
    Combines trend, sentiment, AND valuation into a final weighted score.
    """
    return (w_trend * trend_score) + \
           (w_sentiment * sentiment_score) + \
           (w_valuation * valuation_score)

def map_to_recommendation(final_score, trend_score=None, sentiment_score=None):
    """ Maps final score → Buy / Hold / Sell with hybrid rules """
    if (sentiment_score is not None and sentiment_score >= 85 and final_score >= 60) or \
       (trend_score is not None and trend_score >= 85 and final_score >= 60):
        return "Strong Buy"

    if final_score >= 70: return "Buy"
    elif final_score >= 40: return "Hold"
    else: return "Sell"