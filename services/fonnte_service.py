import requests
import config


def format_nomor_wa(nomor_hp):
    nomor = str(nomor_hp or "").strip()
    nomor = nomor.replace(" ", "").replace("-", "").replace("+", "")

    if nomor.startswith("0"):
        nomor = "62" + nomor[1:]

    return nomor


def kirim_whatsapp_fonnte(nomor_hp, pesan):
    if not nomor_hp:
        return {
            "success": False,
            "response": "Nomor HP kosong"
        }

    url = "https://api.fonnte.com/send"

    headers = {
        "Authorization": config.FONNTE_TOKEN
    }

    data = {
        "target": format_nomor_wa(nomor_hp),
        "message": pesan,
        "countryCode": "62"
    }

    try:
        response = requests.post(url, headers=headers, data=data, timeout=20)

        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "response": response.text
        }

    except Exception as e:
        return {
            "success": False,
            "response": str(e)
        }