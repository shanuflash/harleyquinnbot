from io import BytesIO
from time import sleep
import time
from typing import Optional, List
from telegram import TelegramError, Chat, Message
from telegram import Update, Bot
from telegram.error import BadRequest
from telegram import ParseMode
from telegram.ext import MessageHandler, Filters, CommandHandler
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import escape_markdown
from tg_bot.modules.helper_funcs.chat_status import is_user_ban_protected, bot_admin

import tg_bot.modules.sql.users_sql as sql
from tg_bot import dispatcher, OWNER_ID, LOGGER, SUDO_USERS, SUPPORT_USERS
from tg_bot.modules.helper_funcs.filters import CustomFilters
from tg_bot.modules.disable import DisableAbleCommandHandler


@run_async
def snipe(bot: Bot, update: Update, args: List[str]):
    try:
        chat_id = str(args[0])
        del args[0]
    except TypeError as excp:
        update.effective_message.reply_text("Please give me a chat to echo to!")
    to_send = " ".join(args)
    if len(to_send) >= 2:
        try:
            bot.sendMessage(int(chat_id), str(to_send))
        except TelegramError:
            LOGGER.warning("Couldn't send to group %s", str(chat_id))
            update.effective_message.reply_text("Couldn't send the message. Perhaps I'm not part of that group?")


@run_async
@bot_admin
def getlink(bot: Bot, update: Update, args: List[int]):
    if args:
        chat_id = int(args[0])
    else:
        update.effective_message.reply_text("You don't seem to be referring to a chat")
    chat = bot.get_chat(chat_id)
    bot_member = chat.get_member(bot.id)
    if bot_member.can_invite_users:
        invitelink = bot.exportChatInviteLink(chat_id)
        update.effective_message.reply_text(invitelink)
    else:
        update.effective_message.reply_text("I don't have access to the invite link!")

@run_async
def slist(bot: Bot, update: Update):
    text1 = "My sudo users are:"
    for user_id in SUDO_USERS:
        user = bot.get_chat(user_id)
        name = "[{}](tg://user?id={})".format(user.first_name + (user.last_name or ""), user.id)
        if user.username:
            name = escape_markdown("@" + user.username)
        text1 += "\n - {}".format(name)
    text2 = "My support users are:"
    for user_id in SUPPORT_USERS:
        user = bot.get_chat(user_id)
        name = "[{}](tg://user?id={})".format(user.first_name + (user.last_name or ""), user.id)
        if user.username:
            name = escape_markdown("@" + user.username)
        text2 += "\n - {}".format(name)

    update.effective_message.reply_text(text1 + "\n" + text2, parse_mode=ParseMode.MARKDOWN)

@run_async
def ping(bot: Bot, update: Update):
    start_time = time.time()
    bot.send_message(update.effective_chat.id, "Pong!")
    end_time = time.time()
    ping_time = float(end_time - start_time)*1000
    update.effective_message.reply_text(" Ping speed was : {}ms".format(ping_time))

@bot_admin
def leavechat(bot: Bot, update: Update, args: List[int]):
    if args:
        chat_id = int(args[0])
    else:
        update.effective_message.reply_text("You do not seem to be referring to a chat!")
    try:
        chat = bot.getChat(chat_id)
        titlechat = bot.get_chat(chat_id).title
        bot.sendMessage(chat_id, "Goodbye all 😁")
        bot.leaveChat(chat_id)
        update.effective_message.reply_text("I left group {}".format(titlechat))

    except BadRequest as excp:
        if excp.message == "Chat not found":
            update.effective_message.reply_text("It looks like I've been kicked out of the group :p")
        else:
            return

__mod_name__ = "Special"

SNIPE_HANDLER = CommandHandler("snipe", snipe, pass_args=True, filters=CustomFilters.sudo_filter)
GETLINK_HANDLER = CommandHandler("getlink", getlink, pass_args=True, filters=Filters.user(OWNER_ID))
SLIST_HANDLER = CommandHandler("slist", slist, filters=CustomFilters.sudo_filter)
PING_HANDLER = DisableAbleCommandHandler("ping", ping)
LEAVECHAT_HANDLER = CommandHandler("leavechat", leavechat, pass_args=True, filters=Filters.user(OWNER_ID))

dispatcher.add_handler(SNIPE_HANDLER)
dispatcher.add_handler(GETLINK_HANDLER)
dispatcher.add_handler(SLIST_HANDLER)
dispatcher.add_handler(PING_HANDLER)
dispatcher.add_handler(LEAVECHAT_HANDLER)
