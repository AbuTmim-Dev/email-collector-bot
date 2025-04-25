import datetime
print(f"🚀 Bot started at: {datetime.datetime.now()}")
print("✅ Email Bot launched.")

import re
import asyncio
import nest_asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ChatMemberHandler,
    filters,
)

TOKEN = "7842485646:AAEb7dglPU9CZtHTHEHXXGAhjNvMLbvszr8"
EMAIL_REGEX = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'

def load_emails(chat_id):
    try:
        with open(f"emails_{chat_id}.txt", "r") as f:
            return set(f.read().split(", "))
    except FileNotFoundError:
        return set()

def save_emails(chat_id, emails):
    with open(f"emails_{chat_id}.txt", "w") as f:
        f.write(", ".join(sorted(emails)))

# ✅ message handler: detects emails
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        chat_id = update.message.chat_id
        text = update.message.text
        found = re.findall(EMAIL_REGEX, text)
        if found:
            emails = load_emails(chat_id)
            emails.update(found)
            save_emails(chat_id, emails)

# ✅ /get_emails command
async def get_all_emails(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    emails = load_emails(chat_id)
    if emails:
        email_list = ", ".join(sorted(emails))
        keyboard = [[InlineKeyboardButton("Copy Emails", callback_data="copy_emails")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(email_list, reply_markup=reply_markup)
    else:
        await update.message.reply_text("No emails found yet.")

# ✅ inline button handler
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    emails = load_emails(chat_id)
    if emails:
        email_list = ", ".join(sorted(emails))
        await query.from_user.send_message(f"Here are the emails:\n{email_list}")
    else:
        await query.from_user.send_message("No emails found yet.")

# ✅ welcome new member handler
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_change = update.chat_member.difference().get("status")
    if status_change == "member":
        name = update.chat_member.new_chat_member.user.full_name
        await context.bot.send_message(
            chat_id=update.chat_member.chat.id,
            text=(
                f"Welcome {name}!\n\n"
                "Please share your email address in this group.\n"
                "To get the full list of collected emails, send:\n"
                "`/get_emails`"
            ),
            parse_mode="Markdown"
        )

# ✅ /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome!\n\n"
        "This bot collects all email addresses shared in the group.\n"
        "To view the list of emails collected so far, use the command:\n"
        "`/get_emails`\n\n"
        "You'll also see a 'Copy Emails' button when you do!",
        parse_mode="Markdown"
    )

# ✅ set bot command menu for Telegram interface
async def set_bot_commands(application):
    await application.bot.set_my_commands([
        BotCommand("start", "Start using the bot"),
        BotCommand("get_emails", "Show collected emails")
    ])

# ✅ initialize and run the bot
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start_command))
app.add_handler(CommandHandler("get_emails", get_all_emails))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
app.add_handler(CallbackQueryHandler(handle_buttons))
app.add_handler(ChatMemberHandler(welcome_new_member, ChatMemberHandler.CHAT_MEMBER))

async def main():
    await set_bot_commands(app)
    await app.run_polling()

# ✅ final setup for Render/asyncio compatibility
if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(main())
