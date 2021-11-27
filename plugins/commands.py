import os
import logging
import random
import asyncio
from Script import script
from pyrogram import Client, filters
from pyrogram.errors.exceptions.bad_request_400 import ChatAdminRequired
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id
from database.users_chats_db import db
from info import CHANNELS, ADMINS, AUTH_CHANNEL, CUSTOM_FILE_CAPTION, LOG_CHANNEL, PICS
from utils import get_size, is_subscribed, temp
import re
logger = logging.getLogger(__name__)


PICS = (
         "https://telegra.ph/file/99895680d684d0711c017.jpg",
         "https://telegra.ph/file/5ab2662271c89cbf0a1e3.jpg",
         "https://telegra.ph/file/e6d9a367fe3d4e64b0195.jpg",
         "https://telegra.ph/file/af58155475465e05d3311.jpg",
         "https://telegra.ph/file/f0cb6b3b14e07514fcd16.jpg",
)


@Client.on_message(filters.command("start"))
async def start(client, message):
    if message.chat.type in ['group', 'supergroup']:
        buttons = [
            [
                InlineKeyboardButton('🤖 Updates', url='https://t.me/TeamEvamaria')
            ]
            ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply(script.START_TXT.format(message.from_user.mention if message.from_user else message.chat.title, temp.U_NAME, temp.B_NAME), reply_markup=reply_markup)
        await asyncio.sleep(2) # 😢 https://github.com/EvamariaTG/EvaMaria/blob/master/plugins/p_ttishow.py#L17 😬 wait a bit, before checking.
        if not await db.get_chat(message.chat.id):
            total=await client.get_chat_members_count(message.chat.id)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, "Unknown"))       
            await db.add_chat(message.chat.id, message.chat.title)
        return 
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))
    if len(message.command) != 2:
        buttons = [[
            InlineKeyboardButton('🏷️ 𝖮𝗎𝗋 𝖦𝗋𝗈𝗎𝗉', url=f'http://t.me/InfameSeries')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode='html'
        )
        return
    if AUTH_CHANNEL and not await is_subscribed(client, message):
        try:
            invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL))
        except ChatAdminRequired:
            logger.error("Make sure Bot is admin in Forcesub channel")
            return
        btn = [
            [
                InlineKeyboardButton(
                    "🤖 Join Updates Channel", url=invite_link.invite_link
                )
            ]
        ]

        if message.command[1] != "subscribe":
            btn.append([InlineKeyboardButton(" 🔄 Try Again", callback_data=f"checksub#{message.command[1]}")])
        await client.send_message(
            chat_id=message.from_user.id,
            text="**Please Join My Updates Channel to use this Bot!**",
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode="markdown"
            )
        return
    if len(message.command) ==2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
        buttons = [[
            InlineKeyboardButton('🏷️ 𝖮𝗎𝗋 𝖦𝗋𝗈𝗎𝗉', url=f'http://t.me/InfameSeries')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode='html'
        )
        return
    

@Client.on_message(filters.command('help') & filters.private)
async def help(client, message):
    await message.reply_photo(
        photo=random.choice(PICS),
        caption=script.HELP_TXT.format(message.from_user.mention),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🏷️ 𝖮𝗎𝗋 𝖦𝗋𝗈𝗎𝗉", url="https://t.me/InfameSeries"),
                    InlineKeyboardButton("♻️ 𝖠𝖻𝗈𝗎𝗍", callback_data="about")
                ],
                [
                    InlineKeyboardButton ("👩‍💻 𝖬𝗒 𝖣𝖾𝗏", url="https://t.me/pubgplayer1"),
                    InlineKeyboardButton("𝖢𝗅𝗈𝗌𝖾 🔐", callback_data="close_data")
                ]
            ]
        ),
        reply_to_message_id=message.message_id
    )

@Client.on_message(filters.command('status') & filters.private)
asyn def status(client, message):
    await message.reply_text(script.STATUS_TXT.format(message.from_user.mention)

@Client.on_message(filters.command('about') & filters.private)
async def about(client, message):
    await message.reply_photo(
        photo=random.choice(PICS),
        caption=script.ABOUT_TXT.format(message.from_user.mention),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("⚙️ 𝖧𝖾𝗅𝗉", callback_data="help"),
                    InlineKeyboardButton("🏠 𝖧𝗈𝗆𝖾", callback_data="start"),
                ],
                [
                    InlineKeyboardButton("𝖢𝗅𝗈𝗌𝖾 🔐", callback_data="close_data") 
                ]               
            ]
        ),
        reply_to_message_id=message.message_id
    )


@Client.on_callback_query(filters.regex(r'^autofilter_delete'))
async def delete_all_index_confirm(bot, message):
    await Media.collection.drop()
    await message.answer()
    await message.message.edit('Succesfully Deleted All The Indexed Files.')

