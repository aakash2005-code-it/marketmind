import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """You are MarketMind's AI assistant, embedded in a stock analysis web app.
You help users understand:
1. How MarketMind works (it combines Technical analysis via XGBoost+SHAP, Fundamental analysis via expert rules, and Sentiment analysis via FinBERT into a Buy/Hold/Avoid verdict)
2. The specific stock analysis currently shown to the user, if provided
3. General finance and investing questions — including both US and Indian stock markets (NSE/BSE)

Rules:
- Keep answers concise and conversational (2-4 sentences unless the user asks for detail)
- Never give direct financial advice like "you should buy this" - always frame things educationally
- If asked about the current stock analysis, use the provided context to give a specific, grounded answer
- Always remind users that MarketMind is a decision-support tool, not financial advice, if they ask something like "should I invest"
- For Indian stocks, you may reference SEBI regulations, NSE/BSE listing norms, and Indian market conditions
- Prices for Indian stocks are in INR (₹), not USD
"""

model = genai.GenerativeModel(
    model_name="gemini-3.6-flash",
    system_instruction=SYSTEM_PROMPT,
)


def get_chat_response(message: str, stock_context: dict | None = None) -> str:
    prompt = message
    if stock_context:
        is_indian = stock_context.get("is_indian", False)
        currency = "₹" if is_indian else "$"
        market_label = "NSE/BSE (India)" if is_indian else "US Markets"
        context_str = (
            f"\n\n[Current stock being viewed by the user: {stock_context.get('ticker')}]\n"
            f"Market: {market_label}\n"
            f"Currency: {currency}\n"
            f"Verdict: {stock_context.get('verdict')}\n"
            f"Investment Score: {stock_context.get('investment_score')}\n"
            f"Confidence: {stock_context.get('confidence_score')}\n"
            f"Risk Level: {stock_context.get('risk_level')}\n"
            f"Explanation: {'; '.join(stock_context.get('explanation', []))}\n"
        )
        prompt = message + context_str

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Sorry, I couldn't process that right now. ({str(e)})"