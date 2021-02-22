import config, smtplib, ssl
from datetime import date
import time

current_date = date.today()

# Create a secure SSL context
context = ssl.create_default_context()

# sends a trade notification to gkcap gmail account
#  and a text message to both of our phones
def send_trade_notification(messages,short_messages,strategy_name):
    if not messages:
        return print("The list of messages is empty.")
    else:
        with smtplib.SMTP_SSL(config.EMAIL_HOST, config.EMAIL_PORT, context=context) as server:

            email_message = "\r\n".join([
                f"From: {config.EMAIL_ADDRESS}",
                f"To: {config.EMAIL_ADDRESS}",
                f"Subject: {config.PAPER_API_PLATFORM} Trades | {strategy_name} | {current_date}\n\n"            
            ])
            email_message += "\n\n".join(messages)
            
            server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
            server.sendmail(config.EMAIL_ADDRESS, config.EMAIL_ADDRESS, email_message)

            for sm in short_messages:
                time.sleep(5)
                text_message = "\n".join([
                    f"From: {config.EMAIL_ADDRESS}",
                    f"To: {config.EMAIL_SMS}",
                    f"Subject: {sm}"            
                ])

                server.sendmail(config.EMAIL_ADDRESS, config.EMAIL_SMS, text_message)
                server.sendmail(config.EMAIL_ADDRESS, config.ROHN_EMAIL_SMS, text_message)
                
            return print("You've got a notification.")