import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def kirim_pesan_telegram(pesan):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": pesan
    }

    response = requests.post(url, data=data)
    return response.json()


def kirim_file_telegram(file_path, caption=""):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"

    with open(file_path, "rb") as file:

        files = {
            "document": file
        }

        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "caption": caption
        }

        response = requests.post(
            url,
            data=data,
            files=files
        )

    return response.json()