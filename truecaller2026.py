import requests
import json
import time
from datetime import datetime
import random  # Random ke liye social links

# ================== CONFIGURATION ==================
BOT_TOKEN = '8590387011:AAGfpz-jQV9f4WFxapPi1lcvfcITbV_s0bY'
ADMIN_ID = 7923910698  # Your Admin ID
API_URL = 'https://x2-proxy.vercel.app/api?num='
SUBS_FILE = 'premium_users.json'
USERS_FILE = 'users.json'  # New: Unique users
STATS_FILE = 'stats.json'  # New: Total searches etc.
FREE_COOLDOWN = 1800  # 30 minutes for free users
PREMIUM_COOLDOWN = 10  # Short for premium

ADMIN_USERNAME = 'johnseniordesk'  # @johnseniordesk

# ===================================================

# Load premium users
try:
    with open(SUBS_FILE, 'r') as f:
        subscribers = set(json.load(f))
except:
    subscribers = set()

# Load unique users
try:
    with open(USERS_FILE, 'r') as f:
        unique_users = set(json.load(f))
except:
    unique_users = set()

# Load stats
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

def send_message(chat_id, text, reply_markup=None):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    try:
        requests.post(url, data=payload)
    except:
        pass

def main_keyboard():
    return {
        "keyboard": [
            [{"text": "🔍 Lookup Number"}],
            [{"text": "💎 Subscribe"}, {"text": "❓ Help"}]
        ],
        "resize_keyboard": True
    }

def premium_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "💎 Unlock Premium Features", "url": "t.me/johnseniordesk"}],
            [{"text": "🔄 New Search", "callback_data": "new_search"}]
        ]
    }

# Fetch data from API
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

def get_random_socials():
    socials = ['Instagram', 'Facebook', 'Snapchat']
    random.shuffle(socials)
    num_not_linked = random.randint(0, 2)
    result = {}
    for i, social in enumerate(socials):
        if i < num_not_linked:
            result[social] = "Not Linked"
        else:
            fake_id = f"@{social.lower()}_user{random.randint(100, 999)}"
            result[social] = fake_id
    return result

# Format search result
def format_result(info, is_premium):
    if not info:
        return "❌ No data found for this number."

    result = "🔍 *Lookup Results*\n\n"
    # Free: Name and Address
    result += f"👤 *Name:* {info.get('name', 'N/A')}\n"
    result += f"🏠 *Address:* {info.get('address', 'N/A')}\n\n"
    result += "🔒 *Premium Information (Subscription Required)*\n\n"
    if is_premium:
        result += f"📱 *Mobile:* {info.get('mobile', info.get('number', 'N/A'))}\n"
        result += f"🌍 *Circle:* {info.get('circle', 'N/A')}\n"
        result += f"📧 *Email:* {info.get('email', 'N/A')}\n"
        fathers_name = info.get("fathername", info.get("father_name", 'N/A'))
        result += f"👨‍👩‍👧 *Father's Name:* {fathers_name}\n"
        result += f"🆔 *Document Number:* {info.get('idnumber', info.get('id number', 'N/A'))}\n"
        result += f"📞 *Alternate Mobile:* {info.get('alternatemobile', info.get('alternate mobile', 'N/A'))}\n"
        result += f"📅 *Last Call Details:* Available in Premium+ (Coming Soon)\n\n"
       
        socials = get_random_socials()
        result += "🔗 *Linked Social Profiles:*\n"
        result += f"📸 *Instagram:* {socials['Instagram']}\n"
        result += f"📘 *Facebook:* {socials['Facebook']}\n"
        result += f"👻 *Snapchat:* {socials['Snapchat']}\n\n"
       
        result += "✅ You have full premium access."
    else:
        result += "📱 *Mobile:* 🔒 Premium Required\n"
        result += "🌍 *Circle:* 🔒 Premium Required\n"
        result += "📧 *Email:* 🔒 Premium Required\n"
        result += "👨‍👩‍👧 *Father's Name:* 🔒 Premium Required\n"
        result += "🆔 *Document Number:* 🔒 Premium Required\n"
        result += "📞 *Alternate Mobile:* 🔒 Premium Required\n"
        result += "📅 *Last Call Details:* 🔒 Premium Required (Date • Time • Duration)\n"
        result += "🔗 *Linked Social Profiles:* 🔒 Premium Required (Instagram • Facebook • Snapchat)\n\n"
        result += "💎 Upgrade to premium for complete details!"
    return result

# Log every search to admin
def send_log_to_admin(user_id, username, first_name, num, is_premium):
    log = f"🔍 *New Lookup Alert*\n\n"
    log += f"👤 User ID: `{user_id}`\n"
    log += f"😎 Username: @{username if username else 'N/A'}\n"
    log += f"📛 Name: {first_name}\n"
    log += f"📱 Searched Number: `{num}`\n"
    log += f"🕐 Time: {datetime.now().strftime('%d %b %Y, %I:%M %p')}\n"
    log += f"💎 Premium: {'Yes ✅' if is_premium else 'No ❌'}"
    send_message(ADMIN_ID, log)

# Main polling loop
offset = None
print("Truecaller 2026 Bot is running... 🚀")

while True:
    try:
        updates = requests.get(
            f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates',
            params={'offset': offset, 'timeout': 30}
        ).json()

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
                        unique_users.add(user_id)  # Track unique user
                        save_users()
                        send_message(chat_id,
                            "🔥 *Truecaller 2026 - Advanced Lookup*\n\n"
                            "Get detailed mobile number information:\n"
                            "👤 Name • 🏠 Address (Free)\n"
                            "📧 Email • 🔗 Social Profiles • 🆔 Document Number (Premium)\n"
                            "📞 Alternate Number • 📅 Last Call Details\n\n"
                            "Basic info is free • Full details require premium subscription\n"
                            "Enter a number or use the buttons below 👇",
                            reply_markup=main_keyboard())

                    elif text in ['🔍 Lookup Number', '/lookup']:
                        send_message(chat_id, "Please send a 10-digit mobile number.\nExample: 9876543210")

                    elif text in ['💎 Subscribe', '/subscribe']:
                        send_message(chat_id,
                            "💎 *Premium Subscription*\n\n"
                            "Unlock all premium features including email, social profiles, document number, and more.\n\n"
                            "Contact admin: @johnseniordesk\n"
                            "Complete payment and get instant access!",
                            reply_markup=premium_keyboard())

                    elif text in ['❓ Help', '/help']:
                        send_message(chat_id,
                            "❓ *How to Use*\n\n"
                            "• Tap 'Lookup Number' or send a 10-digit number\n"
                            "• Use /lookup 9876543210 format\n"
                            "• Subscribe for full premium details\n\n"
                            "Premium includes: Email, Linked Socials (Insta/FB/Snap), Document Number, Alternate Mobile, Last Call Details")

                    elif text.isdigit() and len(text) == 10 or (text.startswith('/lookup') and len(text.split()) > 1):
                        num = text.split()[-1] if text.startswith('/lookup') else text

                        now = time.time()
                        cooldown = PREMIUM_COOLDOWN if is_premium else FREE_COOLDOWN

                        if user_id in last_lookups and now - last_lookups[user_id] < cooldown:
                            if is_premium:
                                send_message(chat_id, f"⏳ Please wait {cooldown} seconds before next lookup.")
                            else:
                                send_message(chat_id, "⏳ You can only search once every 30 minutes as a free user. Subscribe to get unlimited searches.", reply_markup=premium_keyboard())
                            continue

                        send_log_to_admin(user_id, username, first_name, num, is_premium)
                        info = fetch_info(num)
                        result = format_result(info, is_premium)

                        # Only apply cooldown if data was found
                        if info:
                            last_lookups[user_id] = now
                            stats['total_searches'] += 1  # Increment total searches
                            save_stats()

                        if is_premium:
                            send_message(chat_id, result, reply_markup=main_keyboard())
                        else:
                            send_message(chat_id, result, reply_markup=premium_keyboard())

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
                            subs_list = "\n".join([str(s) for s in subscribers]) if subscribers else "No premium users"
                            send_message(chat_id, f"💎 Premium Users:\n{subs_list}")

                        elif text == '/status':
                            total_users = len(unique_users)
                            total_premium = len(subscribers)
                            total_searches = stats.get('total_searches', 0)
                            status_msg = f"📊 *Bot Status*\n\n"
                            status_msg += f"Total Unique Users: {total_users}\n"
                            status_msg += f"Total Premium Users: {total_premium}\n"
                            status_msg += f"Total Searches: {total_searches}"
                            send_message(chat_id, status_msg)

                        elif text.startswith('/clearcooldown'):
                            try:
                                clear_id = int(text.split()[1])
                                if clear_id in last_lookups:
                                    del last_lookups[clear_id]
                                    send_message(chat_id, f"✅ Cooldown cleared for user {clear_id}.")
                                else:
                                    send_message(chat_id, "No cooldown found for this user.")
                            except:
                                send_message(chat_id, "Usage: /clearcooldown 123456789")

                elif 'callback_query' in update:
                    cb = update['callback_query']
                    cb_data = cb['data']
                    cb_chat_id = cb['message']['chat']['id']
                    if cb_data == 'new_search':
                        send_message(cb_chat_id, "🔍 Enter a new mobile number:", reply_markup=main_keyboard())

    except Exception as e:
        print("Error:", e)
        time.sleep(5)
