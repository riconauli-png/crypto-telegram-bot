import requests

# Credentials OpenRouter & Telegram
OPENROUTER_API_KEY = (
    "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"
)
TELEGRAM_BOT_TOKEN = "8926246749:AAFNGw1wl9mo16A8cfzIkAXzzMaomoiCH_Y"
TELEGRAM_CHAT_ID = "1741011462"


def ambil_data_coingecko():
    """Mengambil Top 20 koin global berdasarkan volume transaksi dari CoinGecko"""
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "volume_desc",
            "per_page": 20,
            "page": 1,
            "sparkline": "false",
        }
        res = requests.get(url, params=params, timeout=10)

        if res.status_code == 200:
            coins = res.json()
            teks_data = "📊 DATA VOLUME GLOBAL COINGECKO (TOP 20):\n"
            for c in coins:
                symbol = c.get("symbol").upper()
                name = c.get("name")
                price = c.get("current_price")
                change = c.get("price_change_percentage_24h", 0)
                vol = c.get("total_volume")
                vol_juta = vol / 1_000_000
                teks_data += f"- {name} ({symbol}): ${price} | 24h: {change:.2f}% | Vol: ${vol_juta:,.1f}M\n"
            return teks_data
    except Exception as e:
        print(f"⚠️ Gagal mengambil data CoinGecko: {e}")
    return "Data CoinGecko tidak tersedia."


def ambil_model_gratis_aktif():
    url = "https://openrouter.ai/api/v1/models"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json().get("data", [])
            model_gratis = []
            for m in data:
                m_id = m.get("id", "")
                pricing = m.get("pricing", {})
                p_prompt = float(pricing.get("prompt", 1))
                p_comp = float(pricing.get("completion", 1))

                if m_id.endswith(":free") or (p_prompt == 0 and p_comp == 0):
                    model_gratis.append(m_id)
            return model_gratis
    except Exception as e:
        print(f"⚠️ Gagal mengambil model OpenRouter: {e}")
    return []


def main():
    print("📈 1. Mengambil data volume global dari CoinGecko...")
    data_market = ambil_data_coingecko()

    print("🔍 2. Mendeteksi model AI gratis di OpenRouter...")
    daftar_model = ambil_model_gratis_aktif()

    if not daftar_model:
        print("❌ Tidak ada model gratis aktif.")
        return

    openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://telegram.bot",
        "X-Title": "Crypto AI Bot",
        "Content-Type": "application/json",
    }

    prompt = (
        f"Berikut data pasar crypto terkini dari CoinGecko:\n\n{data_market}\n\n"
        "Tugas Anda: Buat ringkasan informasi yang SANGAT SIMPEL, MUDAH DIPAHAMI, dan LANGSUNG PADA POIN.\n"
        "Fokus HANYA pada koin yang terdaftar dan populer di INDODAX (seperti BTC, ETH, SOL, XRP, DOGE, ADA, BNB, TRX, PEPE, SHIB, LINK, NEAR, AVAX, dll).\n\n"
        "Gunakan format polos tanpa menggunakan tanda bintang (*) atau garis bawah (_) sama sekali agar tidak error di Telegram:\n\n"
        "🏛️ 1. RINGKASAN MAKRO & THE FED\n"
        "(Tulis 2 kalimat simpel dampak suku bunga/inflasi ke crypto hari ini)\n\n"
        "🔥 2. KOIN POTENSIAL & LONJAKAN VOLUME (ADA DI INDODAX)\n"
        "(Sebutkan 3-5 koin populer Indodax dengan lonjakan volume terbaik beserta alasan singkatnya)\n\n"
        "🎯 3. ANJURAN TINDAKAN SIMPEL\n"
        "( Berikan 3 poin arahan strategi sederhana)"
    )

    hasil_ai = None

    for model in daftar_model[:5]:
        print(f"🤖 Mengirim data ke model: [{model}]...")
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        }

        try:
            res = requests.post(
                openrouter_url, headers=headers, json=payload, timeout=25
            )
            if res.status_code == 200:
                data = res.json()
                hasil_ai = data["choices"][0]["message"]["content"]
                print(f"✅ Analisa berhasil dibuat oleh [{model}]!")
                break
        except Exception as e:
            print(f"⚠️ Error pada [{model}]: {e}")

    if not hasil_ai:
        print("\n❌ Gagal memproses analisa AI.")
        return

    # Kirim ke Telegram (Tanpa parse_mode agar 100% bebas dari error karakter)
    print("\n📱 3. Mengirim laporan ke Telegram iPhone 7 Plus...")
    telegram_url = (
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    )
    payload_telegram = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"🚀 RINGKASAN CRYPTO & MAKRO HARIAN\n\n{hasil_ai}",
    }

    try:
        res_telegram = requests.post(telegram_url, json=payload_telegram)
        if res_telegram.status_code == 200:
            print(
                "\n🎉 SUKSES 100%! Pesan ringkas berhasil masuk ke Telegram iPhone 7 Plus Anda!"
            )
        else:
            print(f"\n❌ Gagal mengirim ke Telegram: {res_telegram.text}")
    except Exception as e:
        print(f"\n❌ Eror koneksi Telegram: {e}")


if __name__ == "__main__":
    main()