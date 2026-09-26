import requests
import json
import os

TELEGRAM_TOKEN = "8926246749:AAH7f9z5NzJn31ZM12o3ofd0ZRTXtdBhDzo"
TELEGRAM_CHAT_ID = "1741011462"
OPENROUTER_API_KEY = "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"

# Daftar Model AI Gratis Terbaru & Paling Stabil
FREE_MODELS = [
    "google/gemini-2.0-flash-lite-001:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "qwen/qwen-2.5-72b-instruct:free",
    "deepseek/deepseek-r1:free",
    "openrouter/free"
]

# KRITERIA RADAR ALERT
MIN_1H_CHANGE = 2.0      # Lonjakan minimum 2.0% dalam 1 jam
MIN_24H_CHANGE = 7.0     # Lonjakan minimum 7.0% dalam 24 jam
MIN_VOL_RATIO = 20.0     # Rasio Volume ke Market Cap >= 20%

def get_crypto_data():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "idr",
            "order": "market_cap_desc",
            "per_page": 50,
            "page": 1,
            "sparkline": "false",
            "price_change_percentage": "1h,24h"
        }
        res = requests.get(url, params=params, timeout=15)
        if res.status_code == 200:
            return res.json()
        return None
    except Exception as e:
        print(f"Error Coingecko: {e}")
        return None

def filter_surging_coins(coins):
    alert_coins = []
    for c in coins:
        change_1h = c.get("price_change_percentage_1h_in_currency") or 0.0
        change_24h = c.get("price_change_percentage_24h_in_currency") or c.get("price_change_percentage_24h") or 0.0
        volume = c.get("total_volume") or 0
        mcap = c.get("market_cap") or 1

        vol_mcap_ratio = (volume / mcap) * 100 if mcap > 0 else 0

        if change_1h >= MIN_1H_CHANGE or change_24h >= MIN_24H_CHANGE or vol_mcap_ratio >= MIN_VOL_RATIO:
            alert_coins.append({
                "name": c['name'],
                "symbol": c['symbol'].upper(),
                "price_idr": c['current_price'],
                "change_1h": change_1h,
                "change_24h": change_24h,
                "volume_idr": volume,
                "vol_mcap_ratio": vol_mcap_ratio
            })
    return alert_coins

def analyze_alerts_with_ai(alert_coins):
    summary_text = ""
    for c in alert_coins:
        summary_text += f"- {c['name']} ({c['symbol']}): Rp {c['price_idr']:,} | 1h: +{c['change_1h']:.2f}% | 24h: +{c['change_24h']:.2f}% | Vol/MC Ratio: {c['vol_mcap_ratio']:.1f}%\n"

    prompt = f"""
    Kamu adalah AI Radar Scanner Crypto profesional untuk investor Indonesia.
    Berikut koin yang mendadak mengalami lonjakan volume/harga saat ini:

    {summary_text}

    Berikan analisis kilat & panduan tindakan singkat (maksimal 3-4 poin ringkas) untuk koin di atas:
    - Indikasi penyebab lonjakan / potensi akumulasi.
    - Area perhatian (Breakout / Volatilitas Tinggi).
    - Panduan tindakan simpel untuk investor (misal: Entry Bertahap, Wait & See, atau Watchlist).
    Gunakan bahasa Indonesia yang jelas, profesional, tanpa simbol Markdown rumit.
    """

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com",
        "X-Title": "CryptoScannerBot"
    }

    for model in FREE_MODELS:
        print(f"Mencoba AI Model: {model}")
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        try:
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=25)
            print(f"Respon Status ({model}): {res.status_code}")
            if res.status_code == 200:
                result = res.json()
                if "choices" in result and len(result["choices"]) > 0:
                    text_content = result["choices"][0]["message"]["content"]
                    if text_content and len(text_content.strip()) > 0:
                        return text_content
        except Exception as e:
            print(f"Model {model} error: {e}")
            continue

    return "⚠️ Lonjakan terdeteksi, namun analisis mendalam AI sedang tidak tersedia."

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    }
    res = requests.post(url, json=payload, timeout=10)
    print(f"Status Respon Telegram: {res.status_code}")

def main():
    print("1. Scanning top 50 pasar crypto...")
    coins = get_crypto_data()
    if not coins:
        print("Gagal mengambil data dari CoinGecko.")
        return

    print("2. Menganalisis kriteria lonjakan volume/harga...")
    surging_coins = filter_surging_coins(coins)

    if not surging_coins:
        print("Status: Pasar stabil. Tidak ada koin yang memenuhi kriteria lonjakan saat ini. Bot diam.")
        return

    print(f"Ditemukan {len(surging_coins)} koin mengalami lonjakan!")

    print("3. Meminta analisis kilat AI...")
    ai_analysis = analyze_alerts_with_ai(surging_coins)

    final_message = f"🚨 RADAR SCANNER: SINYAL LONJAKAN DETECTED!\n\n{ai_analysis}\n\n---\n*Bot Radar Scanner Real-Time*"

    print("4. Mengirim sinyal ALERT ke Telegram...")
    send_telegram(final_message)
    print("Sinyal berhasil dikirim!")

if __name__ == "__main__":
    main()
