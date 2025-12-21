import requests
import json
import time
from datetime import datetime

# ================== CONFIGURATION ==================
BOT_TOKEN = '8590387011:AAGfpz-jQV9f4WFxapPi1lcvfcITbV_s0bY'
ADMIN_ID = 7923910698  # Your Admin ID
API_URL = 'https://x2-proxy.vercel.app/api?num='
SUBS_FILE = 'premium_users.json'
USERS_FILE = 'users.json'
STATS_FILE = 'stats.json'
FREE_COOLDOWN = 86400  # 24 hours for free users
PREMIUM_COOLDOWN = 10
PREMIUM_LIMIT_PERIOD = 600
PREMIUM_LIMIT_COUNT = 10
ADMIN_USERNAME = 'johnseniordesk'

# ===================================================

try:
    with open(SUBS_FILE, 'r') as f:
        subscribers = set(json.load(f))
except:
    subscribers = set()

try:
    with open(USERS_FILE, 'r') as f:
        unique_users = set(json.load(f))
except:
    unique_users = set()

try:
    with open(STATS_FILE, 'r') as f:
        stats = json.load(f)
except:
    stats = {'total_searches': 0}

def save_subs():
    with open(SUBS_FILE, 'w') as f:
        json.dump(list(subscribers), f)

def save_users():
    with open(USERS_FILE, 'w') as f:
        json.dump(list(unique_users), f)

def save_stats():
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f)

last_lookups = {}
premium_recent_searches = {}

def send_message(chat_id, text, reply_markup=None):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    try:
        requests.post(url, data=payload)
    except:
        pass

def main_keyboard():
    return {"keyboard": [[{"text": "🔍 Lookup Number"}], [{"text": "💎 Subscribe"}, {"text": "❓ Help"}]], "resize_keyboard": True}

def premium_keyboard():
    return {"inline_keyboard": [[{"text": "💎 Unlock Premium Features", "url": "t.me/johnseniordesk"}], [{"text": "🔄 New Search", "callback_data": "new_search"}]]}

def fetch_info(num):
    try:
        r = requests.get(API_URL + str(num), timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get('success') and 'result' in data and len(data['result']) > 0:
                info = {k.lower(): v for k, v in data['result'][0].items()}
                return info
    except:
        pass
    return None

def format_result(info, is_premium):
    if not info:
        return "❌ No data found for this number."
    result = "🔍 *Lookup Results*\n\n"
    result += f"👤 *Name:* {info.get('name', 'N/A')}\n"
    result += f"🏠 *Address:* {info.get('address', 'N/A')}\n\n"
    if not is_premium:
        result += "🔒 *Premium Information (Subscription Required)*\n\n"
        result += "📱 *Mobile:* 🔒 Premium Required\n"
        result += "🌍 *Circle:* 🔒 Premium Required\n"
        result += "📧 *Email:* 🔒 Premium Required\n"
        result += "👨‍👩‍👧 *Father's Name:* 🔒 Premium Required\n"
        result += "🆔 *Document Number:* 🔒 Premium Required\n"
        result += "📞 *Alternate Mobile:* 🔒 Premium Required\n"
        result += "📅 *Last Call Details:* 🔒 Premium Required\n"
        result += "🔗 *Linked Social Profiles:* 🔒 Premium Required\n\n"
        result += "💎 Upgrade to premium for complete details!"
        return result
    result += "✅ *Full Premium Details Unlocked*\n\n"
    result += f"📱 *Mobile:* {info.get('mobile', info.get('number', 'N/A'))}\n"
    result += f"🌍 *Circle:* {info.get('circle', 'N/A')}\n"
    result += f"📧 *Email:* {info.get('email', 'N/A')}\n"
    fathers_name = info.get('fathername', info.get('father_name', 'N/A'))
    result += f"👨‍👩‍👧 *Father's Name:* {fathers_name}\n"
    doc_num = info.get('idnumber', info.get('id number', 'N/A'))
    result += f"🆔 *Document Number:* {doc_num}\n"
    alt_mobile = info.get('alternatemobile', info.get('alternate mobile', None))
    if alt_mobile and alt_mobile.strip() and alt_mobile.lower() not in ['n/a', 'none', '', 'not available']:
        result += f"📞 *Alternate Mobile:* {alt_mobile}\n"
    else:
        result += f"📞 *Alternate Mobile:* Not Available\n"
    result += "\n✅ You have full premium access."
    return result

def send_log_to_admin(user_id, username, first_name, num, is_premium):
    log = f"🔍 *New Lookup Alert*\n\n"
    log += f"👤 User ID: `{user_id}`\n"
    log += f"😎 Username: @{username if username else 'N/A'}\n"
    log += f"📛 Name: {first_name}\n"
    log += f"📱 Searched Number: `{num}`\n"
    log += f"🕐 Time: {datetime.now().strftime('%d %b %Y, %I:%M %p')}\n"
    log += f"💎 Premium: {'Yes ✅' if is_premium else 'No ❌'}"
    send_message(ADMIN_ID, log)

offset = None
print("Truecaller 2026 Bot is running... 🚀")

while True:
    try:
        updates = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates', params={'offset': offset, 'timeout': 30}).json()
        if 'result' in updates:
            for update in updates['result']:
                offset = update['update_id'] + 1
                if 'message' in update:
                    msg = update['message']
                    chat_id = msg['chat']['id']
                    user_id = msg['from']['id']
                    text = msg.get('text', '').strip()
                    username = msg['from'].get('username', '')
                    first_name = msg['from'].get('first_name', 'Unknown')
                    is_premium = user_id in subscribers

                    if text == '/start':
                        unique_users.add(user_id)
                        save_users()
                        send_message(chat_id, "🔥 *Truecaller 2026 - Advanced Lookup*\n\nGet detailed mobile number information:\n👤 Name • 🏠 Address (Free)\n📧 Email • 🆔 Document Number • 📞 Alternate Number (Premium)\n\nBasic info is free • Full details require premium subscription\nEnter a number or use the buttons below 👇", reply_markup=main_keyboard())

                    elif text in ['🔍 Lookup Number', '/lookup']:
                        send_message(chat_id, "Please send a 10-digit mobile number.\nExample: 9876543210")

                    elif text in ['💎 Subscribe', '/subscribe']:
                        send_message(chat_id, "💎 *Premium Subscription*\n\nUnlock all premium features including email, document number, alternate mobile, etc.\n\nContact admin: @johnseniordesk\nComplete payment and get instant access!", reply_markup=premium_keyboard())

                    elif text in ['❓ Help', '/help']:
                        send_message(chat_id, "❓ *How to Use*\n\n• Tap 'Lookup Number' or send a 10-digit number\n• Use /lookup 9876543210\n• Subscribe for full premium details\n\nPremium includes: Email, Document Number, Alternate Mobile, etc.")

                    elif text.isdigit() and len(text) == 10 or (text.startswith('/lookup') and len(text.split()) > 1):
                        num = text.split()[-1] if text.startswith('/lookup') else text
                        now = time.time()

                        if user_id in last_lookups and now - last_lookups[user_id] < (PREMIUM_COOLDOWN if is_premium else FREE_COOLDOWN):
                            remaining = int((PREMIUM_COOLDOWN if is_premium else FREE_COOLDOWN) - (now - last_lookups[user_id]))
                            hours_left = remaining // 3600
                            if is_premium:
                                send_message(chat_id, f"⏳ Please wait {PREMIUM_COOLDOWN} seconds before next lookup.")
                            else:
                                send_message(chat_id, f"⏳ Please wait {hours_left} hours before next search.\nSubscribe for unlimited access!", reply_markup=premium_keyboard())
                            continue

                        if is_premium:
                            if user_id not in premium_recent_searches:
                                premium_recent_searches[user_id] = []
                            premium_recent_searches[user_id] = [t for t in premium_recent_searches[user_id] if now - t < PREMIUM_LIMIT_PERIOD]
                            if len(premium_recent_searches[user_id]) >= PREMIUM_LIMIT_COUNT:
                                send_message(chat_id, "Bot is in heavy load, wait few minutes and try again.")
                                continue

                        send_log_to_admin(user_id, username, first_name, num, is_premium)
                        info = fetch_info(num)
                        result = format_result(info, is_premium)

                        if info:
                            last_lookups[user_id] = now
                            stats['total_searches'] += 1
                            save_stats()
                            if is_premium:
                                premium_recent_searches[user_id].append(now)

                        keyboard = main_keyboard() if is_premium else premium_keyboard()
                        send_message(chat_id, result, reply_markup=keyboard)

                    elif user_id == ADMIN_ID:
                        if text.startswith('/addsub'):
                            try:
                                sub_id = int(text.split()[1])
                                subscribers.add(sub_id)
                                save_subs()
                                send_message(chat_id, f"✅ User {sub_id} added to premium.")
                            except:
                                send_message(chat_id, "Usage: /addsub 123456789")
                        elif text.startswith('/removesub'):
                            try:
                                sub_id = int(text.split()[1])
                                subscribers.discard(sub_id)
                                save_subs()
                                send_message(chat_id, f"✅ User {sub_id} removed from premium.")
                            except:
                                send_message(chat_id, "Usage: /removesub 123456789")
                        elif text.startswith('/broadcast'):
                            message = text.split(maxsplit=1)[1] if len(text.split()) > 1 else "No message"
                            for sub in subscribers:
                                send_message(sub, message)
                            send_message(chat_id, f"✅ Broadcast sent to {len(subscribers)} premium users.")
                        elif text == '/listsubs':
                            subs_list = "\n".join(map(str, subscribers)) if subscribers else "None"
                            send_message(chat_id, f"💎 Premium Users:\n{subs_list}")
                        elif text == '/status':
                            send_message(chat_id, f"📊 *Bot Status*\n\nUnique Users: {len(unique_users)}\nPremium Users: {len(subscribers)}\nTotal Searches: {stats.get('total_searches', 0)}")
                        elif text.startswith('/clearcooldown'):
                            try:
                                cid = int(text.split()[1])
                                last_lookups.pop(cid, None)
                                send_message(chat_id, f"✅ Cooldown cleared for {cid}")
                            except:
                                send_message(chat_id, "Usage: /clearcooldown 123456789")

                elif 'callback_query' in update:
                    cb = update['callback_query']
                    if cb['data'] == 'new_search':
                        send_message(cb['message']['chat']['id'], "🔍 Enter a new mobile number:", reply_markup=main_keyboard())

    except Exception as e:
        print("Error:", e)
        time.sleep(5)
