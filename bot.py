import telebot
import instaloader
import os
import re
import uuid

BOT_TOKEN = "TELEGRAM-BOT-API"
bot = telebot.TeleBot(BOT_TOKEN)
ig = instaloader.Instaloader()

INSTAGRAM_URL_PATTERN = r"(https?://(?:www\.)?instagram\.com/(?:p|reel|tv)/[a-zA-Z0-9_-]+)"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🚀 I’m here to help you download Instagram profile pictures, images, and reels effortlessly!")

@bot.message_handler(commands=['profile'])
def ask_for_nickname(message):
    bot.reply_to(message,
        "📸 Profile Picture Fetcher Activated!\nPlease enter the Instagram username to retrieve the profile picture.\n💡 Example: _abcd3\n📌 No need to include '@'—just type the username!")

@bot.message_handler(func=lambda message: True)
def handle_input(message):
    text = message.text.strip()

    # Handle Instagram media URL
    match = re.search(INSTAGRAM_URL_PATTERN, text)
    if match:
        url = match.group(1)
        bot.reply_to(message, f"📥 Downloading media from:\n{url}")
        return download_instagram_post(bot, message, url)

    # Handle Instagram profile picture
    if ' ' in text or text.startswith('/'):
        return

    bot.reply_to(message, f"🔍 Downloading profile picture of @{text}...")

    try:
        ig.download_profile(text, profile_pic_only=True)
        folder_name = text
        files = os.listdir(folder_name)
        image_path = next((os.path.join(folder_name, f) for f in files if f.endswith('.jpg')), None)

        if image_path and os.path.exists(image_path):
            with open(image_path, 'rb') as photo:
                bot.send_photo(message.chat.id, photo, caption=f"📸 Profile picture of @{text}")
                bot.send_message(message.chat.id, "🎯 Mission Accomplished! Your media is now available! 🚀\n🔗 Click to view/download it now. 🔄 Want another one? Send me the next link!")
        else:
            bot.send_message(message.chat.id, "❌ The nickname is not found!")

        # Cleanup
        for f in files:
            os.remove(os.path.join(folder_name, f))
        os.rmdir(folder_name)

    except instaloader.exceptions.ProfileNotExistsException:
        bot.send_message(message.chat.id, "❌ The nickname is not found!")
    except Exception as e:
        bot.send_message(message.chat.id, "⚠️ Oops! Something went wrong. Please try again later. If the issue persists, check your connection or try a different link.")

def download_instagram_post(bot, message, url):
    try:
        shortcode = url.strip('/').split('/')[-1]
        temp_dir = str(uuid.uuid4())
        os.makedirs(temp_dir)

        post = instaloader.Post.from_shortcode(ig.context, shortcode)
        ig.download_post(post, target=temp_dir)

        sent = False
        for file in os.listdir(temp_dir):
            path = os.path.join(temp_dir, file)
            if file.endswith('.jpg') or file.endswith('.png'):
                with open(path, 'rb') as img:
                    bot.send_photo(message.chat.id, img)
                    sent = True
            elif file.endswith('.mp4'):
                with open(path, 'rb') as vid:
                    bot.send_video(message.chat.id, vid)
                    sent = True

        if sent:
            bot.send_message(message.chat.id, "🎯 Mission Accomplished! Your media is now available! 🚀\n🔗 Click to view/download it now. 🔄 Want another one? Send me the next link!")
        else:
            bot.send_message(message.chat.id, "⚠️ Oops! Something went wrong. Please try again later. If the issue persists, check your connection or try a different link.")

        # Cleanup
        for f in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, f))
        os.rmdir(temp_dir)

    except Exception as e:
        bot.send_message(message.chat.id, "⚠️ Oops! Something went wrong. Please try again later. If the issue persists, check your connection or try a different link.")

# Start the bot
print("🤖 Bot is running...")
bot.infinity_polling()
