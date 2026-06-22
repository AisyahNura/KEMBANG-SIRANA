import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

print(f"GROQ_API_KEY: {GROQ_API_KEY[:10] if GROQ_API_KEY else 'Not Found'}...")

try:
    client = OpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1"
    )
    
    print("Mencoba model llama3-8b-8192...")
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "user", "content": "Halo, respon dengan kata 'BERHASIL' saja jika kamu menerima pesan ini."}
        ]
    )
    print("Respon llama3-8b-8192:", response.choices[0].message.content.strip())

except Exception as e:
    print("Error dengan llama3-8b-8192:", e)

try:
    client = OpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1"
    )
    
    print("Mencoba model llama-3.1-8b-instant...")
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": "Halo, respon dengan kata 'BERHASIL' saja jika kamu menerima pesan ini."}
        ]
    )
    print("Respon llama-3.1-8b-instant:", response.choices[0].message.content.strip())

except Exception as e:
    print("Error dengan llama-3.1-8b-instant:", e)
