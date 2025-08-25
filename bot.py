from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import random
import os

# Bot credentials
API_ID = 24565632
API_HASH = "1482ed4f3990771a44ccb0769207fca2"
BOT_TOKEN = "8220102766:AAFvrTBP0fJ19F6yJFo3XgWtsb5dpx6Jak8"
ADMIN_ID = 8150269384  # Your Telegram ID

# Categories
CATEGORY_MAP = {
    "waifu": "waifu.json",
    "cosplay": "cosplay.json",
    "rule": "rule34.json",
    "loli": "loli.json"
}

# Quotes
SFW_QUOTES = [
    "💖 You're looking amazing today!",
    "✨ Here's a sweet waifu for your day!",
    "🌸 Keep smiling, beautiful!",
    "💫 Every waifu deserves a smile.",
    "🌼 Just a little happiness for you!"
]

NSFW_QUOTES = [
    "🔥 Naughty thoughts incoming... 😈",
    "💦 Careful, things are getting spicy!",
    "😏 Feeling naughty today, huh?",
    "💥 Ready for some steamy fun?",
    "🍑 Sweet and a little dangerous!"
]

# Create bot
app = Client("waifu_pro_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Load & save JSON data
def load_images(file_path):
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            json.dump([], f)
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except:
        return []

def save_images(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

# /start
@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_photo(
        photo="https://ar-hosting.pages.dev/1751454135930.jpg",
        caption="👋 Welcome! Use /help to see available commands and categories 💦"
    )

# /help
@app.on_message(filters.command("help"))
async def help_cmd(client, message):
    text = """🧠 **Waifu Bot Commands:**
/waifu – Send random waifu image
/cosplay – NSFW cosplay
/rule – Erotic anime waifu
/loli – Loli pic
/random – Any random image

**Admin Commands**
/addlink [cat] [url] – Add image to category
/deletelink [url] – Delete image from all
/show [url] – Check which category it's in
/list [cat] – Show first 30 links
/clear [cat] – Delete all in category
/refresh – Reload categories
/stats – Show number of images in each category"""
    await message.reply(text)

# /random
@app.on_message(filters.command("random"))
async def random_any(client, message):
    files = list(CATEGORY_MAP.values())
    random_file = random.choice(files)
    images = load_images(random_file)
    if images:
        await message.reply_photo(photo=random.choice(images))
    else:
        await message.reply("⚠️ No images found in any category.")

# /waifu /cosplay /rule /loli
@app.on_message(filters.command(list(CATEGORY_MAP.keys())))
async def handle_image_command(client, message):
    cmd = message.command[0].lstrip("/").lower()
    file = CATEGORY_MAP.get(cmd)
    images = load_images(file)

    if not images:
        return await message.reply(f"⚠️ No images found in `{cmd}`.")

    selected = random.choice(images)
    is_spoiler = cmd in ["cosplay", "rule", "loli"]
    quote = random.choice(NSFW_QUOTES if is_spoiler else SFW_QUOTES)

    await message.reply_photo(
        photo=selected,
        caption=quote,
        has_spoiler=is_spoiler,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄 Next", callback_data=f"next_{cmd}")
        ]])
    )

# Inline "Next" button
@app.on_callback_query(filters.regex("^next_"))
async def send_next_image(client, callback_query):
    cmd = callback_query.data.replace("next_", "")
    file = CATEGORY_MAP.get(cmd)
    images = load_images(file)
    if not images:
        return await callback_query.answer("⚠️ No more images!", show_alert=True)
    selected = random.choice(images)
    is_spoiler = cmd in ["cosplay", "rule", "loli"]
    quote = random.choice(NSFW_QUOTES if is_spoiler else SFW_QUOTES)
    await callback_query.message.reply_photo(
        photo=selected,
        caption=quote,
        has_spoiler=is_spoiler,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄 Next", callback_data=f"next_{cmd}")
        ]])
    )
    await callback_query.answer()

# /refresh
@app.on_message(filters.command("refresh") & filters.user(ADMIN_ID))
async def refresh_command(client, message):
    CATEGORY_MAP.clear()
    CATEGORY_MAP.update({
        "waifu": "waifu.json",
        "cosplay": "cosplay.json",
        "rule": "rule34.json",
        "loli": "loli.json"
    })
    await message.reply("🔄 Categories refreshed.")

# /addlink
@app.on_message(filters.command("addlink") & filters.user(ADMIN_ID))
async def add_link(client, message):
    try:
        _, category, url = message.text.split(maxsplit=2)
        if not url.startswith(("http://", "https://")):
            return await message.reply("⚠️ Invalid URL format.")
        file = CATEGORY_MAP.get(category)
        if not file:
            return await message.reply("❌ Unknown category.")
        images = load_images(file)
        if url in images:
            return await message.reply("⚠️ Link already exists.")
        images.append(url)
        save_images(file, images)
        await message.reply("✅ Link added.")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

# /deletelink
@app.on_message(filters.command("deletelink") & filters.user(ADMIN_ID))
async def delete_link(client, message):
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            return await message.reply("⚠️ Usage: /deletelink [url]")
        url = parts[1].strip()
        deleted_from = []
        for cat, file in CATEGORY_MAP.items():
            images = load_images(file)
            if url in images:
                images.remove(url)
                save_images(file, images)
                deleted_from.append(cat)
        if deleted_from:
            await message.reply_photo(photo=url, caption=f"🗑️ Deleted from: `{', '.join(deleted_from)}`")
        else:
            await message.reply("❌ Not found in any category.")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

# /show
@app.on_message(filters.command("show") & filters.user(ADMIN_ID))
async def show_link(client, message):
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            return await message.reply("⚠️ Usage: /show [url]")
        url = parts[1].strip()
        found_in = []
        for cat, file in CATEGORY_MAP.items():
            images = load_images(file)
            if url in images:
                found_in.append(cat)
        if found_in:
            await message.reply_photo(photo=url, caption=f"✅ Found in: `{', '.join(found_in)}`")
        else:
            await message.reply("❌ Not found in any category.")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

# /list
@app.on_message(filters.command("list") & filters.user(ADMIN_ID))
async def list_links(client, message):
    try:
        _, category = message.text.split(maxsplit=1)
        file = CATEGORY_MAP.get(category)
        if not file:
            return await message.reply("❌ Unknown category.")
        images = load_images(file)
        if not images:
            return await message.reply(f"📭 No images in `{category}`.")
        msg = f"📁 **{category}** has `{len(images)}` images:\n"
        msg += "\n".join(images[:30])
        await message.reply(msg)
    except:
        await message.reply("⚠️ Usage: `/list waifu`")

# /clear
@app.on_message(filters.command("clear") & filters.user(ADMIN_ID))
async def clear_links(client, message):
    try:
        _, category = message.text.split(maxsplit=1)
        file = CATEGORY_MAP.get(category)
        if not file:
            return await message.reply("❌ Unknown category.")
        save_images(file, [])
        await message.reply(f"🧹 Cleared all links in `{category}`.")
    except:
        await message.reply("⚠️ Usage: `/clear waifu`")

# /stats
@app.on_message(filters.command("stats") & filters.user(ADMIN_ID))
async def stats_command(client, message):
    text = "📊 **Bot Statistics:**\n"
    for cat, file in CATEGORY_MAP.items():
        images = load_images(file)
        text += f"• `{cat}`: {len(images)} images\n"
    await message.reply(text)

# Run bot
app.run()