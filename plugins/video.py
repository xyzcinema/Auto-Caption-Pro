from aiogram import Router, types, F, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import LOG_CHANNEL
from database import get_thumbnail, increment_usage, is_banned, add_user
from plugins.caption import generate_auto_caption

router = Router()

def small_caps(text: str) -> str:
    """Convert text to small caps unicode."""
    normal = "abcdefghijklmnopqrstuvwxyz"
    small = "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
    result = ""
    for char in text:
        if char.lower() in normal:
            idx = normal.index(char.lower())
            result += small[idx]
        else:
            result += char
    return result

def get_original_filename(video: types.Video) -> str:
    """Get the original filename from video, preserving full name with underscores."""
    if video.file_name:
        # Return full filename without any truncation
        return video.file_name
    # Fallback if no filename
    return f"video_{video.file_unique_id}.mp4"

@router.message(F.video)
async def handle_video(message: types.Message, bot: Bot):
    """Handle incoming video - process immediately with original filename."""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name

    # Check if banned
    if await is_banned(user_id):
        await message.answer(small_caps("You are banned from using this bot."))
        return

    # Add/update user
    await add_user(user_id, username, first_name)

    video = message.video
    caption = message.caption or ""
    original_filename = get_original_filename(video)

    # Get user's thumbnail
    thumb_file_id = await get_thumbnail(user_id)

    if not thumb_file_id:
        # No thumbnail set - send warning
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⚙️ Settings", callback_data="settings")]
        ])
        await message.answer(
            f"<b>⚠️ {small_caps('No thumbnail set!')}</b>\n\n"
            f"<blockquote>{small_caps('Please set a thumbnail first using Settings.')}</blockquote>",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        return

    # Increment usage count
    await increment_usage(user_id)

    # Generate auto caption if enabled
    auto_caption = await generate_auto_caption(original_filename, user_id)

    # Combine with user's caption if exists
    final_caption = caption
    if auto_caption:
        if final_caption:
            final_caption = f"{auto_caption}\n\n{final_caption}"
        else:
            final_caption = auto_caption

    # Send video with original filename
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ Settings", callback_data="settings")]
    ])

    await bot.send_video(
        chat_id=message.chat.id,
        video=video.file_id,
        caption=final_caption,
        cover=thumb_file_id,
        filename=original_filename,
        reply_markup=keyboard
    )

    # Log to channel
    if LOG_CHANNEL:
        try:
            await bot.send_message(
                chat_id=LOG_CHANNEL,
                text=f"📹 <b>ᴠɪᴅᴇᴏ ᴘʀᴏᴄᴇssᴇᴅ</b>\n\n"
                     f"🆔 <code>{user_id}</code>\n"
                     f"👤 {first_name} (@{username or 'N/A'})\n"
                     f"📄 <code>{original_filename}</code>\n"
                     f"📝 {caption[:50] + '...' if len(caption) > 50 else caption or 'No caption'}",
                parse_mode="HTML"
            )
        except Exception:
            pass
