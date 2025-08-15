import os
import re
import time
import requests
import phonenumbers
from phonenumbers import geocoder
from dotenv import load_dotenv

load_dotenv()

# ================================
# TELEGRAM CONFIGURATION
# ================================
TELEGRAM_BOT_TOKEN = "8432191653:AAHUuOR485CXKkxg3TNL3ZIxRruxdIXK6Cs"
#  chat_id  username
GROUP_CHAT_ID = "@otprcvrakib"

HEADERS = {
    "Host": "94.23.120.156",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "http://94.23.120.156/ints/agent/SMSCDRStats",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9,ur-IN;q=0.8,ur;q=0.7",
}

cookies = {
    'PHPSESSID': '02lf16emo0m5u7hl9vnmli74rk',
}

URL = "http://94.23.120.156/ints/agent/res/data_smscdr.php?fdate1=2025-08-14%2000:00:00&fdate2=2025-08-14%2023:59:59&iDisplayStart=0&iDisplayLength=25"

# ================================
# Country name + flag generation
# ================================
def get_country_info(phone_number):
    try:
        if phone_number.startswith("216"):
            return "Tunisia "

        num = phonenumbers.parse(phone_number, None)
        country_name = geocoder.description_for_number(num, "en")
        country_code = phonenumbers.region_code_for_number(num)

        if country_code:
            flag = ''.join(chr(ord(c) + 127397) for c in country_code.upper())
        else:
            flag = ""
        return f"{country_name} {flag}"
    except Exception:
        return "Unknown"

# ================================
#      
# ================================
def bot_is_admin(chat_id):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getChatAdministrators?chat_id={chat_id}"
        res = requests.get(url).json()
        if res["ok"]:
            admins = res["result"]
            # Telegram Bot ID
            bot_info = requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe").json()
            bot_id = bot_info["result"]["id"]
            for admin in admins:
                if admin["user"]["id"] == bot_id:
                    return True
        return False
    except Exception as e:
        print("Error checking admin:", e)
        return False

# ================================
# Send message to Telegram with OTP
# ================================
def send_to_telegram(message, otp="No OTP found", country_info="Unknown"):
    if not bot_is_admin(GROUP_CHAT_ID):
        print("Bot is not admin in the group. Message not sent.")
        return

    tg_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    # MarkdownV2 escape function
    def escape_markdown(text):
        escape_chars = r"_*[]()~`>#+-=|{}.!"
        return ''.join(f"\\{c}" if c in escape_chars else c for c in text)

    message_lines = message.split('\n')
    formatted_lines = []

    for line in message_lines:
        if line.startswith(" Time:"):
            formatted_lines.append(f"*{escape_markdown(line)}*")
        elif line.startswith(" Number:"):
            formatted_lines.append(f"*{escape_markdown(line)}*")
            formatted_lines.append(f" *Main OTP:* `{escape_markdown(otp)}`")
            formatted_lines.append(f" *Country:* {escape_markdown(country_info)}")
        elif line.startswith(" Service:"):
            formatted_lines.append(f"*{escape_markdown(line)}*")
        elif line.startswith(" Full Message:"):
            formatted_lines.append(f"*{escape_markdown(line)}*")
        elif line.startswith(" Powered by:"):
            formatted_lines.append(f"*{escape_markdown(line)}*")
        else:
            formatted_lines.append(escape_markdown(line))

    final_message = '\n'.join(formatted_lines)

    payload = {
        "chat_id": GROUP_CHAT_ID,
        "text": final_message,
        "parse_mode": "MarkdownV2"
    }

    try:
        requests.post(tg_url, json=payload)
    except Exception as e:
        print("Error sending to Telegram:", e)

# ================================
# Fetch SMS data
# ================================
def fetch_data():
    try:
        r = requests.get(URL, cookies=cookies, headers=HEADERS, timeout=15)
        r.raise_for_status()
        return r.json()
    except ValueError:
        print("Invalid JSON response received:")
        print(r.text[:500])
        return {}
    except Exception as e:
        print("Error fetching data:", e)
        return {}

# ================================
# Main loop
# ================================
def main():
    last_ids = set()
    while True:
        try:
            data = fetch_data()
            if "aaData" in data:
                for row in data["aaData"]:
                    msg_id = row[0]
                    from_number = row[2]
                    cli = row[3]
                    sms_text = row[5]

                    # OTP extract
                    otp_match = re.search(r"Telegram\s*code[:\s-]*\s*(\d+)", sms_text, re.IGNORECASE)
                    main_otp = otp_match.group(1) if otp_match else "Otp Not Found"

                    # Country info
                    country_info = get_country_info(from_number)

                    # Send message to Telegram only once per msg_id
                    if msg_id not in last_ids:
                        message = f" Time: {msg_id}\n Number: {from_number}\n Service: {cli}\n Full Message:\n{sms_text}\n Powered by: Rakib"
                        send_to_telegram(message, otp=main_otp, country_info=country_info)
                        last_ids.add(msg_id)
        except Exception as e:
            print("Error in main loop:", e)
        time.sleep(2)  # 10 seconds delay

if __name__ == "__main__":
    main()