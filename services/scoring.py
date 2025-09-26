def get_price_trend_score(predicted_close, last_close):
    """
    Converts price trend into score (0–100).
    """
    pct_change = ((predicted_close - last_close) / last_close) * 100
    
    if pct_change > 2:
        return 90
    elif pct_change > 0.5:
        return 70
    elif pct_change > -0.5:
        return 50
    elif pct_change > -2:
        return 30
    else:
        return 10

def combine_scores(trend_score, sentiment_score, w_sentiment=0.6, w_trend=0.4):
    """
    Combines trend + sentiment into a final weighted score.
    """
    return w_sentiment * sentiment_score + w_trend * trend_score

def map_to_recommendation(final_score, trend_score=None, sentiment_score=None):
    """
    Maps final score → Buy / Hold / Sell with hybrid rules:
    - Normal thresholds: Buy ≥ 70, Hold ≥ 40, else Sell
    - Override: if trend or sentiment ≥ 85 and final_score ≥ 60 → Buy
    """
    # Strong sentiment override
    if sentiment_score is not None and sentiment_score >= 85 and final_score >= 60:
        return "Buy"

    # Strong trend override
    if trend_score is not None and trend_score >= 85 and final_score >= 60:
        return "Buy"

    # Normal thresholds
    if final_score >= 70:
        return "Buy"
    elif final_score >= 40:
        return "Hold"
    else:
        return "Sell"

