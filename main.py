# main.py
# Minimal Telegram + GPT-4o + Tradovate bot

import os, json, requests, uuid, openai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
TRADOVATE_ACCESS_TOKEN = os.getenv("TRADOVATE_ACCESS_TOKEN")
TRADOVATE_ACCOUNT_ID = os.getenv("TRADOVATE_ACCOUNT_ID")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Extract JSON with symbol, side, quantity, entry, stopLoss, takeProfit"},
            {"role": "user", "content": msg}
        ]
    )
    trade = json.loads(response.choices[0].message.content)
    order = {
        "accountId": int(TRADOVATE_ACCOUNT_ID),
        "action": "Sell" if trade["side"].upper() == "SELL" else "Buy",
        "symbol": trade["symbol"],
        "orderQty": trade.get("quantity", 1),
        "orderType": "Market",
        "isAutomated": True,
        "bracket": {
            "profitTarget": {"price": float(trade["takeProfit"])},
            "stopLoss": {"price": float(trade["stopLoss"])}
        }
    }
    r = requests.post("https://demo-api.tradovate.com/v1/order/placeorder",
                      headers={"Authorization": f"Bearer {TRADOVATE_ACCESS_TOKEN}"}, json=order)
    print("Tradovate Response:", r.status_code, r.text)

app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()