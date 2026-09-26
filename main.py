import requests
import json
import os

TELEGRAM_TOKEN = "7832870347:AAFW3lE-aI6s4O_J-A-eG2O_qQfS0iQ4kR0"
TELEGRAM_CHAT_ID = "612808027"
OPENROUTER_API_KEY = "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"

# Daftar Model AI Gratis yang Paling Stabil & Respon Cepat
FREE_MODELS = [
    "google/gemini-2.0-flash-lite-001:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "deepseek/deepseek-r1:free",
    "qwen/qwen-2.5-72b-instruct:free",
    "mistralai/mistral-7b-instruct:free"
]

def get_crypto_data():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "idr",
            "order": "market_cap_desc",
            "per_page": 10,
            "page": 1,
            "sparkline": "false",
            "price_change_percentage": "24h"
        }
        res = requests.get(url, params=params, timeout=10)
        return res.json()
    except Exception as e:
        print(f"Error Coingecko: {e}")
        return None

def analyze_with_ai(data_summary):
    prompt = f"""
    Kamu adalah analis crypto profesional untuk investor Indonesia.
    Analisa data top 10 koin berikut dalam bahasa Indonesia yang ringkas, jelas, dan tanpa simbol Markdown yang rumit:
    
    Data:
    {data_summary}
    
    Format Laporan:
    - Ringkasan Pasar Harian
    - Top Gainers / Losers
    - Sentimen Singkat
    """
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com",
        "X-Title": "CryptoBot"
    }

    for model in FREE_MODELS:
        print(f"Mencoba AI: {model}")
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        try:
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=20)
            if res.status_code == 200:
                result = res.json()
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Model {model} gagal, mencoba model berikutnya...")
            continue

    return "⚠️ Analisis AI sedang tidak tersedia, namun data pasar telah diperbarui."

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    }
    requests.post(url, json=payload, timeout=10)

def main():
    print("1. Mengambil data pasar...")
    coins = get_crypto_data()
    if not coins:
        print("Gagal mengambil data crypto.")
        return

    summary_list = []
    for c in coins:
        summary_list.append(f"{c['name']} ({c['symbol'].upper()}): Rp {c['current_price']:,} (24h: {c.get('price_change_percentage_24h', 0):.2f}%)")
    
    data_str = "\n".join(summary_list)
    
    print("2. Memproses analisis AI...")
    ai_analysis = analyze_with_ai(data_str)
    
    final_message = f"📊 LAPORAN PASAR CRYPTO HARIAN\n\n{ai_analysis}\n\n---\n*Bot Otomatis GitHub Actions*"
    
    print("3. Mengirim ke Telegram...")
    send_telegram(final_message)
    print("Selesai!")

if __name__ == "__main__":
    main()
