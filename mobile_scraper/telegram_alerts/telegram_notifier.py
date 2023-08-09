from mobile_scraper.telegram_alerts.credentials import token, users
from notifiers import get_notifier


def send_notification(msg):
    telegram = get_notifier('telegram')
    for user_id in users:
        telegram.notify(token=token, chat_id=user_id, message=msg)
