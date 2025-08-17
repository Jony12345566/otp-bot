import requests
import time
import re

# ==============================
# Telegram Bot Info
# ==============================
BOT_TOKEN = "8432191653:AAHUuOR485CXKkxg3TNL3ZIxRruxdIXK6Cs"
CHAT_ID = "@otprcvrakib"

# Panel API URL
cookies = {
    'PHPSESSID': '4eu731o94bhokeeg7mo8e97jv3',
}

headers = {
    'Host': '94.23.120.156',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'http://94.23.120.156/ints/agent/SMSCDRStats',
    'Accept-Language': 'en-US,en;q=0.9',
}

url = "http://94.23.120.156/ints/agent/res/data_smscdr.php?fdate1=2025-08-17%2000:00:00&fdate2=2025-08-17%2023:59:59&frange=&fclient=&fnum=&fcli=&fgdate=&fgmonth=&fgrange=&fgclient=&fgnumber=&fgcli=&fg=0&sEcho=1&iColumns=9&sColumns=%2C%2C%2C%2C%2C%2C%2C%2C&iDisplayStart=0&iDisplayLength=25&mDataProp_0=0&sSearch_0=&bRegex_0=false&bSearchable_0=true&bSortable_0=true&mDataProp_1=1&sSearch_1=&bRegex_1=false&bSearchable_1=true&bSortable_1=true&mDataProp_2=2&sSearch_2=&bRegex_2=false&bSearchable_2=true&bSortable_2=true&mDataProp_3=3&sSearch_3=&bRegex_3=false&bSearchable_3=true&bSortable_3=true&mDataProp_4=4&sSearch_4=&bRegex_4=false&bSearchable_4=true&bSortable_4=true&mDataProp_5=5&sSearch_5=&bRegex_5=false&bSearchable_5=true&bSortable_5=true&mDataProp_6=6&sSearch_6=&bRegex_6=false&bSearchable_6=true&bSortable_6=true&mDataProp_7=7&sSearch_7=&bRegex_7=false&bSearchable_7=true&bSortable_7=true&mDataProp_8=8&sSearch_8=&bRegex_8=false&bSearchable_8=true&bSortable_8=false&sSearch=&bRegex=false&iSortCol_0=0&sSortDir_0=desc&iSortingCols=1&_=1755445392279"

# ==============================
# Country Code Map
# ==============================
COUNTRY_CODES = {
    "1":   "USA 🇺🇸",
    "7":   "Russia 🇷🇺",
    "20":  "Egypt 🇪🇬",
    "212": "Morocco 🇲🇦",
    "213": "Algeria 🇩🇿",
    "216": "Tunisia 🇹🇳",
    "218": "Libya 🇱🇾",
    "880": "Bangladesh 🇧🇩",
    "91":  "India 🇮🇳",
    "92":  "Pakistan 🇵🇰",
    "963": "Syria 🇸🇾",
    "964": "Iraq 🇮🇶",
    "970": "Palestine 🇵🇸",
    "971": "UAE 🇦🇪",
    "972": "Israel 🇮🇱",
    "973": "Bahrain 🇧🇭",
    "974": "Qatar 🇶🇦",
    "966": "Saudi Arabia 🇸🇦",
}

def detect_country(number):
    for code, country in sorted(COUNTRY_CODES.items(), key=lambda x: -len(x[0])):  
        if str(number).startswith(code):
            return country
    return "Unknown 🌍"

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "reply_markup": {
            "inline_keyboard": [
                [
                    {"text": "Join Channel 1", "url": "https://t.me/your_channel_1"},
                    {"text": "Join Channel 2", "url": "https://t.me/your_channel_2"}
                ]
            ]
        }
    }
    requests.post(url, json=payload)

# ==============================
# Fetch OTPs
# ==============================
def fetch_otps():
    r = requests.get(url, cookies=cookies, headers=headers)
    data = r.json()

    otps = []
    if "aaData" in data:
        for row in reversed(data["aaData"]):
            time_str = row[0]
            number   = str(row[2])
            service  = row[3]
            full_msg = str(row[5])

            if full_msg.strip() == "0":
                continue

            patterns = [
                r'\b\d{4,6}\b',
                r'\d{3}\s?\d{3}',
                r'[A-Za-z0-9]{4,12}',
                r'[\w-]{4,12}'
            ]

            otp_code = "N/A"
            for pattern in patterns:
                match = re.search(pattern, full_msg)
                if match:
                    otp_code = match.group()
                    break

            country = detect_country(number)

            msg = (
                f"🔥 <b>{service} {country} RECEIVED!</b> ✨\n\n"
                f"<b>⏰ Time:</b> {time_str}\n"
                f"<b>🌍 Country:</b> {country}\n"
                f"<b>⚙️ Service:</b> {service}\n"
                f"<b>☎️ Number:</b> {number[:6]}***{number[-3:]}\n"
                f"<b>🔑 OTP:</b> <code>{otp_code}</code>\n"
                f"<b>📩 Full Message:</b>\n<pre>{full_msg}</pre>"
            )
            otps.append(msg)
    return otps

# ==============================
# Main Loop
# ==============================
last_seen = set()

while True:
    try:
        otps = fetch_otps()
        for otp in otps:
            if otp not in last_seen:
                send_to_telegram(otp)
                last_seen.add(otp)
    except Exception as e:
        print("Error:", e)

    time.sleep(15)