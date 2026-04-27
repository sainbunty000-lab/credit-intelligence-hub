def send_telegram_alert(message):
    # Use the specific B2B token secret we just created
    token = os.getenv("B2B_BOT_TOKEN") 
    chat_id = os.getenv("TELEGRAM_CHAT_ID") # You can use the same Chat ID
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        params = {"chat_id": chat_id, "text": message}
        try:
            requests.get(url, params=params)
        except Exception as e:
            print(f"Telegram Error: {e}")
