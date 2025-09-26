import subprocess

def analyze_news_with_ollama(news_text):
    """
    Calls local Ollama (phi3) to score sentiment (0–100).
    """
    prompt = f"""You are a financial analyst.
    Based on the following news, rate the sentiment for the stock on a scale of 0–100,
    where 0 = Strong Sell, 50 = Hold, 100 = Strong Buy.
    
    News: {news_text}
    
    Answer with only the number.
    """
    
    result = subprocess.run(
        ["ollama", "run", "phi3"],
        input=prompt.encode("utf-8"),
        capture_output=True
    )
    
    try:
        score = int(result.stdout.decode("utf-8").strip())
        return max(0, min(100, score))  # Clamp between 0–100
    except:
        return 50  # fallback = neutral
