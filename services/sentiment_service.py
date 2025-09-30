import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env file
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-flash-lite-latest")

# RENAMED THE FUNCTION HERE
def analyze_sentiment_with_gemini(news_text: str) -> int:
    """
    Calls Gemini API to score sentiment (0–100).
    0 = Strong Sell, 50 = Hold, 100 = Strong Buy
    """
    if not news_text or not news_text.strip():
        return 50 # Return neutral if there's no news

    prompt = f"""
    You are a financial analyst.
    Based on the following news, rate the sentiment for the stock on a scale of 0–100,
    where 0 = Strong Sell, 50 = Hold, 100 = Strong Buy.

    Only output the number.

    News: {news_text}
    """

    response = model.generate_content(prompt)

    try:
        score = int(response.text.strip())
        return max(0, min(100, score))  # Clamp between 0–100
    except (ValueError, TypeError) as e:
        print("Parsing error:", e, "| Raw response:", response.text)
        return 50  # fallback = neutral