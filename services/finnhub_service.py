import finnhub
import os
import logging

# ==============================================================================
# --- CRITICAL SETUP: FINNHUB API KEY ---
# ==============================================================================
# You MUST get a free API key from Finnhub to use this application.
# 1. Go to https://finnhub.io/register
# 2. Get your free API key.
# 3. Set it as an environment variable in your terminal before running the app:
#
#    export FINNHUB_API_KEY='your_real_api_key_here'
#
# The application will not work without a valid key.
# ==============================================================================

FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY")

finnhub_client = None
if FINNHUB_API_KEY:
    try:
        finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
        # Test the connection with a simple, low-cost API call
        finnhub_client.countries()
        logging.info("Finnhub client initialized successfully.")
    except Exception as e:
        logging.error(f"Failed to initialize or validate Finnhub client with the provided API key: {e}")
else:
    logging.error("CRITICAL: FINNHUB_API_KEY environment variable not set. The application cannot fetch stock data.")


def search_stocks(query):
    """
    Searches for stocks using the Finnhub API.
    """
    if not finnhub_client:
        logging.error("Finnhub client not initialized. Cannot search for stocks.")
        return []
    try:
        return finnhub_client.symbol_lookup(query).get('result', [])
    except Exception as e:
        logging.error(f"Finnhub search failed for '{query}': {e}")
        return []

def get_company_logo(symbol, get_full_profile=False):
    """
    Fetches the company profile from Finnhub.
    - By default, returns just the logo URL.
    - If get_full_profile is True, returns the entire profile dictionary.
    """
    if not finnhub_client:
        logging.error(f"Finnhub client not initialized. Cannot get profile for {symbol}.")
        return None
    try:
        profile = finnhub_client.company_profile2(symbol=symbol)
        
        if not profile:
            return None
        
        if get_full_profile:
            return profile
        else:
            return profile.get('logo')
            
    except Exception as e:
        # This can happen with a free key for non-US stocks or due to rate limits.
        logging.warning(f"Could not retrieve Finnhub profile for {symbol} (API limit or unsupported symbol?): {e}")
        return None

