import requests

from config import FONNTE_TOKEN

TOKEN = FONNTE_TOKEN

if not TOKEN:
    raise RuntimeError("FONNTE_TOKEN belum diisi di environment atau file .env")

headers = {
    "Authorization": TOKEN
}

data = {
    "target": "087832722708",
    "message": "Halo dari Sirana Kembang 🌸"
}
files = {
    "document": open("outputs/undangan/undangan_27_Fajar.pdf", "rb")
}

response = requests.post(
    "https://api.fonnte.com/send",
    headers=headers,
    data=data,
    files=files
)

print(response.text)