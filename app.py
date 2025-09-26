from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import logging
import subprocess
import yfinance as yf
import pandas as pd

app = Flask(__name__)
CORS(app)
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

@app.route("/stocks", methods=["GET"])
def get_stocks():
    """
    Returns filtered stock search results with robust error handling.
    """
    from services.finnhub_service import search_stocks, get_company_logo, finnhub_client
    
    if not finnhub_client:
        error_message = "Finnhub client not initialized. Please check if the FINNHUB_API_KEY is set correctly in the backend environment."
        logging.error(error_message)
        return jsonify({"error": error_message}), 500

    query = request.args.get("q", "").strip()
    results = []
    processed_symbols = set()

    try:
        stocks_to_fetch = []
        if ',' in query and query:
            stocks_to_fetch = [s.strip() for s in query.split(',')]
        elif query:
            search_results = search_stocks(query)
            for item in search_results:
                symbol = item.get("symbol")
                if not symbol or symbol in processed_symbols: continue
                if item.get("type") != "Common Stock": continue
                if '.' in symbol: continue
                stocks_to_fetch.append(symbol)
                processed_symbols.add(symbol)
        
        for symbol in stocks_to_fetch:
            if not symbol: continue
            try:
                profile = get_company_logo(symbol, get_full_profile=True)
                if profile and profile.get('name'):
                     results.append({
                        "symbol": symbol,
                        "name": profile.get('name'),
                        "logo": profile.get('logo')
                    })
            except Exception as e:
                logging.warning(f"Could not fetch full profile for {symbol}, skipping: {e}")

        return jsonify(results)

    except Exception as e:
        error_message = f"An unexpected error occurred on the server while fetching stocks: {e}"
        logging.error(error_message, exc_info=True)
        return jsonify({"error": error_message}), 500

# --- NEW ENDPOINT FOR HISTORICAL DATA ---
@app.route("/history", methods=["GET"])
def get_history():
    """
    Fetches historical stock data for a given symbol and period.
    """
    symbol = request.args.get("symbol")
    period = request.args.get("period", "1y") # Default to 1 year

    if not symbol:
        return jsonify({"error": "Stock symbol is required."}), 400

    try:
        # Fetch data using yfinance
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period, interval="1d")

        if hist.empty:
            return jsonify({"error": f"No historical data found for symbol {symbol} with period {period}."}), 404

        # Reset index to make 'Date' a column
        hist.reset_index(inplace=True)
        
        # Convert timestamps to a more readable format (YYYY-MM-DD)
        hist['Date'] = hist['Date'].dt.strftime('%Y-%m-%d')

        # Prepare data for JSON response
        data = {
            'dates': hist['Date'].tolist(),
            'prices': hist['Close'].tolist()
        }
        return jsonify(data)
    except Exception as e:
        logging.error(f"Error fetching history for {symbol}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


def summarize_news_with_llm(symbol, articles):
    """
    Summarize multiple news articles using Ollama phi3.
    """
    if not articles:
        return "No significant news found."
    news_text = "\n".join([f"- {a['title']}: {a['description']}" for a in articles if a.get('title') and a.get('description')])
    prompt = f"Summarize the following latest news about {symbol} into 2–3 key points. Be concise and objective.\n\nNews:\n{news_text}"
    try:
        result = subprocess.run(["ollama", "run", "phi3"], input=prompt.encode("utf-8"), capture_output=True, check=True)
        return result.stdout.decode("utf-8").strip() or "Summary not available."
    except Exception as e:
        logging.error(f"News summarization with Ollama failed: {e}")
        return "News summary could not be generated due to a local AI model error."

def generate_explanation(symbol, last_close, predicted_close, trend_score,
                         sentiment_score, final_score, recommendation, news_text):
    """
    Uses Ollama LLM (phi3) to explain reasoning in natural language.
    """
    prompt = f"""You are a stock analyst assistant.
    Task: Explain in **3–5 sentences max** why the recommendation for {symbol} is "{recommendation}".
    Only use:
    - Price trend (last close: {last_close}, predicted close: {predicted_close})
    - Trend score: {trend_score}
    - Sentiment score: {sentiment_score}
    - Final score: {final_score}
    - Key news (summarized below)
    News: {news_text[:400]}
    Rules:
    - Do NOT mention unrelated companies or crypto.
    - Do NOT invent extra details. Be factual and concise. Use simple language.
    - Explain it in Bulletin Points. Stay focused on {symbol}.
    """
    try:
        result = subprocess.run(["ollama", "run", "phi3"], input=prompt.encode("utf-8"), capture_output=True, check=True)
        return result.stdout.decode("utf-8").strip() or "Explanation not available."
    except Exception as e:
        logging.error(f"LLM explanation with Ollama failed: {e}")
        return "Explanation not available due to a local AI model error."

@app.route("/analyze", methods=["GET"])
def analyze():
    from services.stock_service import get_stock_data, predict_next_close
    from services.news_service import get_company_news
    from services.sentiment_service import analyze_news_with_ollama
    from services.scoring import get_price_trend_score, combine_scores, map_to_recommendation

    symbol = request.args.get("symbol", "GOOG")
    try:
        logging.info(f"--- Starting analysis for {symbol} ---")
        df = get_stock_data(symbol)
        last_close = float(df["close"].iloc[-1])
        predicted_close = predict_next_close(df)
        trend_score = get_price_trend_score(predicted_close, last_close)
        logging.info(f"Last close={last_close}, Predicted={predicted_close}, TrendScore={trend_score}")

        articles = get_company_news(symbol)
        logging.info(f"Fetched {len(articles)} news articles for {symbol}")
        news_text = " ".join([a['title'] + " " + a['description'] for a in articles if a.get('description')])
        sentiment_score = analyze_news_with_ollama(news_text)
        logging.info(f"Sentiment score: {sentiment_score}")

        news_summary = summarize_news_with_llm(symbol, articles)
        final_score = combine_scores(trend_score, sentiment_score)
        recommendation = map_to_recommendation(final_score, trend_score=trend_score, sentiment_score=sentiment_score)
        logging.info(f"Final score: {final_score}, Recommendation: {recommendation}")

        explanation = generate_explanation(symbol, last_close, predicted_close, trend_score, sentiment_score, final_score, recommendation, news_text)
        logging.info("Generated explanation with LLM")

        result = {
            "symbol": symbol, "last_close": last_close, "predicted_close": predicted_close,
            "trend_score": trend_score, "sentiment_score": sentiment_score, "final_score": final_score,
            "recommendation": recommendation, "latest_news_summary": news_summary, "explanation": explanation
        }
        logging.info(f"--- Finished analysis for {symbol} ---")
        return jsonify(result)
    except Exception as e:
        error_message = f"An error occurred during analysis for {symbol}: {e}"
        logging.error(error_message, exc_info=True)
        return jsonify({"error": error_message}), 500

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)

