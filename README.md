# MarketMind

Explainable AI for stock investment decision support. MarketMind splits every
Buy / Hold / Avoid verdict into three independent signals, explains each one
in its own way, and shows its own track record and limits.

## What it does

- **Technical signal:** an XGBoost model predicts 5-day direction from six
  indicators (MACD histogram, ATR %, RSI, 10-day rate of change, Stochastic %K,
  Bollinger %B). SHAP values show which indicators drove each prediction.
- **Fundamental signal:** transparent rules compare P/E and debt-to-equity with
  sector benchmarks.
- **Sentiment signal:** FinBERT classifies recent headlines, and the app lists
  each headline it read.
- **Visible formula:** the signals are combined with adjustable weights
  (default 40 / 30 / 30). Sliders let the user change them.

## Features

- Counterfactual what-if explanations (the smallest change that would flip the verdict)
- Signal-conflict banner when the three signals disagree
- Data-completeness indicator for each analysis
- Track record: the technical signal replayed on data the model never trained on
- Calibration check of the model's stated probabilities
- Historical stress test against past market shocks
- US and India (NSE / BSE) markets, with company-name search
- Accounts (JWT), search history, and a watchlist that tracks verdict changes
- Portfolio diversification advisor
- AI assistant (Gemini) that can discuss the current analysis

## Tech stack

Python, FastAPI, SQLAlchemy, SQLite, XGBoost, SHAP, scikit-learn,
Hugging Face Transformers (FinBERT), React (Vite), Recharts.
Data: yfinance (Yahoo Finance), Alpha Vantage, NewsAPI.

## Evaluation (honest summary)

The technical model is validated with walk-forward testing (never a random
split). Its accuracy is about 55%, which is close to the base rate: in the test
window prices rose roughly 56% of the time. Short-horizon price direction is
close to a random walk, so MarketMind does not claim to predict prices or beat
the market. Its value is in transparent reasoning and honest evaluation.

## Run locally

Backend:

    cd backend
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    python -m uvicorn app.main:app --reload

Create `backend/.env` with your own free API keys:

    ALPHA_VANTAGE_KEY=your_key
    NEWSAPI_KEY=your_key
    GEMINI_API_KEY=your_key

The first run downloads the FinBERT model (about 400 MB).

Frontend (in a second terminal):

    cd frontend
    npm install
    npm run dev

Open http://localhost:5173. The frontend expects the backend at http://127.0.0.1:8000.

## Known limitations

- Free data sources are rate-limited, delayed, and sometimes incomplete.
- The model is trained on large-cap US stocks and applied to Indian stocks without retraining.
- Fundamental benchmarks are US sector averages.
- The backtest covers only the technical signal and ignores costs and taxes.
- Training baskets are companies that are large today, so survivorship bias applies.

## Disclaimer

MarketMind is a decision-support and educational project. It is not financial
advice. Predictions are probabilistic, not guarantees.
