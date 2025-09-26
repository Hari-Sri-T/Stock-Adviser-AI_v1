import yfinance as yf
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow import keras

# Load trained LSTM model
model = keras.models.load_model("model/best_multivariate_lstm.keras")

FEATURES = ["close", "open", "high", "low", "volume"]
TIME_STEP = 60

def get_stock_data(symbol="GOOG"):
    """
    Fetches last 90 days of stock data from Yahoo Finance.
    No API key needed.
    """
    df = yf.download(symbol, period="90d", interval="1d")
    df = df.rename(columns={
        "Close": "close", "Open": "open", "High": "high", "Low": "low", "Volume": "volume"
    })
    return df[FEATURES]

def preprocess_data(df):
    """
    Scales data and returns last TIME_STEP days in correct shape.
    """
    scaler = MinMaxScaler((0, 1))
    scaled = scaler.fit_transform(df)
    X = scaled[-TIME_STEP:]
    return np.expand_dims(X, axis=0), scaler

def predict_next_close(df):
    """
    Uses the LSTM model to predict next closing price.
    """
    X, scaler = preprocess_data(df)
    pred = model.predict(X)
    
    # Inverse transform (only 'close' column)
    dummy = np.zeros((1, len(FEATURES)))
    dummy[:, 0] = pred.ravel()
    predicted_close = scaler.inverse_transform(dummy)[:, 0][0]
    
    return float(predicted_close)
