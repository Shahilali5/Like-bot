from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler, Bot
import requests
import os
from datetime import datetime, timedelta

app = Flask(__name__)

BOT_TOKEN = '7396431893:AAEMiOriq9BWY9fo4J9PnKbiuwv0DjUSevU'
CHANNELS = ["ShahilWebs", "FreeFireAPI_CHAT", "Shahilwebschat"]
WEBHOOK_URL = 'https://like-bot-4g9g.onrender.com/'
bot = Bot(BOT_TOKEN)
application = Application.builder().token(BOT_TOKEN).build()  # Use Application.builder() instead of Dispatcher

user_verification_data = {}

def check_user_membership(telegram_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember"
    for channel in CHANNELS:
        response = requests.get(url, params={'chat_id': '@' + channel, 'user_id': telegram_id})
        data = response.json()
        if not data['ok'] or data['result']['status'] not in ['member', 'administrator', 'creator']:
            return False
    return True

def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    telegram_id = user.id
    if not check_user_membership(telegram_id):
        photo = "https://t.me/Codewithshahilfiles/7"
        caption = f"<b> 🙋‍♂ Wᴇʟᴄᴏᴍᴇ <a href='tg://user?id={telegram_id}'>{user.first_name}</a></b>\n➖➖➖➖➖➖➖➖➖➖➖➖\n\n⌛ Jᴏɪɴ Aʟʟ Cʜᴀɴɴᴇʟs Aɴᴅ Cʟɪᴄᴋ Oɴ Jᴏɪɴᴇᴅ Tᴏ Sᴛᴀʀᴛ Oᴜʀ Bᴏᴛ"
        keyboard = [
            [InlineKeyboardButton(f"Join {CHANNELS[0]}", url=f"https://t.me/{CHANNELS[0]}"),
             InlineKeyboardButton(f"Join {CHANNELS[1]}", url=f"https://t.me/{CHANNELS[1]}")],
            [InlineKeyboardButton(f"Join {CHANNELS[2]}", url=f"https://t.me/{CHANNELS[2]}")]
        ]
        update.message.reply_photo(photo=photo, caption=caption, parse_mode=ParseMode.HTML,
                                  reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        keyboard = [
            [InlineKeyboardButton("Verify", callback_data='verify')]
        ]
        update.message.reply_text(
            "You have joined all channels, click the button below to verify and start using the bot.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

def verify(update: Update, context: CallbackContext):
    user = update.callback_query.from_user
    telegram_id = user.id

    long_url = "https://t.me/freeFire_max_likesbot"
    api_token = '30618b9817f395a45089a988ad998cf254eafb4c'
    api_url = f"https://api.modijiurl.com/api?api={api_token}&url={long_url}&alias=CustomAlias"

    try:
        response = requests.get(api_url)
        data = response.json()
        
        if data.get("status") == "success":
            short_url = data["shortenedUrl"]
            access_expiry = datetime.now() + timedelta(hours=1)
            user_verification_data[telegram_id] = {
                'verified': True,
                'access_expiry': access_expiry
            }
            update.callback_query.answer(text="✅ Verified! You have access for 1 hour.")
            update.callback_query.message.reply_text(f"Your verification is successful! Access granted for 1 hour.\nShortened URL: {short_url}")
        else:
            update.callback_query.answer(text="❌ Verification failed. Please try again.")
    
    except Exception as e:
        update.callback_query.answer(text="❌ An error occurred while verifying. Please try again later.")
        print(e)

def like(update: Update, context: CallbackContext):
    telegram_id = update.message.from_user.id

    if telegram_id in user_verification_data:
        access_expiry = user_verification_data[telegram_id].get('access_expiry')
        if access_expiry and datetime.now() > access_expiry:
            del user_verification_data[telegram_id]
            update.message.reply_text("Your access has expired. Please verify again to continue using the bot.")
            return

    if telegram_id not in user_verification_data or not user_verification_data[telegram_id].get('verified'):
        update.message.reply_text("You need to verify first to use the bot. Please click 'Verify' to continue.")
        return

    if len(context.args) < 2:
        update.message.reply_text("Usage: /like <region> <uid>")
        return

    region = context.args[0]
    uid = context.args[1]
    api_url = f"https://ff-like-shahil.vercel.app/like?uid={uid}&region={region}"

    try:
        response = requests.get(api_url)
        data = response.json()

        if data["status"] == 1:
            update.message.reply_text(
                f"🚀 *UID Validated - API connected*\n\n🆔 *UID:* `{uid}`\n👤 *Name:* `{data['PlayerNickname']}`\n\n"
                f"👍 *Likes Before Cmd:* `{data['LikesbeforeCommand']}`\n💚 *Likes After Cmd:* `{data['LikesafterCommand']}`\n"
                f"🐉 *Likes Given By Bot:* `{data['LikesGivenByAPI']}`\n\n"
                "📨 *Sent By:* @Shahil440\n\n🖼️ [LIKES SENT](https://iili.io/33PVMKl.md.jpg)",
                parse_mode=ParseMode.MARKDOWN
            )
        elif data["status"] == 2:
            update.message.reply_text("❌ You have already claimed your likes.")
        else:
            update.message.reply_text("❌ Failed to process your request. Please try again later.")
    except Exception as e:
        update.message.reply_text("❌ Failed to get data from API. Please try again later.")
        print(e)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        json_str = request.get_json(force=True)
        update = Update.de_json(json_str, bot)
        application.process_update(update)  # Use application.process_update() instead of dispatcher.process_update()
        return "ok", 200

def set_webhook():
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={WEBHOOK_URL}webhook'
    response = requests.get(url)
    return response.json()

if __name__ == "__main__":
    set_webhook()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("like", like))
    application.add_handler(CallbackQueryHandler(verify, pattern='^verify$'))

    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
