def run_scraper():
    print("Testing connection...")
    alert_msg = "Hello! Your Credit Intelligence Hub is successfully connected."
    
    # Try sending the message
    send_telegram_alert(alert_msg)
    print("Test message sent.")

if __name__ == "__main__":
    run_scraper()
