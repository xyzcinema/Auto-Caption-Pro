# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat
from aiogram import Router, types, F, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat
from config import LOG_CHANNEL
from database import get_thumbnail, increment_usage, is_banned, add_user
from plugins.caption import generate_auto_caption
# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat
router = Router()
# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat

class VideoRenameState(StatesGroup):
    waiting_for_filename = State()

# Store video info temporarily (chat_id, message_id -> video data)
video_storage = {}

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
# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat

def get_original_filename(video: types.Video) -> str:
    """Get the original filename from video, preserving full name with underscores."""
    if video.file_name:
        # Return full filename without any truncation
        return video.file_name
    # Fallback if no filename
    return f"video_{video.file_unique_id}.mp4"
# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat

@router.message(F.video)
async def handle_video(message: types.Message, state: FSMContext, bot: Bot):
    """Handle incoming video - ask if user wants to rename."""
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

    # Store video data for later use
    storage_key = f"{user_id}_{message.message_id}"
    video_storage[storage_key] = {
        "video_file_id": video.file_id,
        "caption": caption,
        "thumb_file_id": thumb_file_id,
        "user_id": user_id,
        "username": username,
        "first_name": first_name,
        "original_filename": original_filename
    }

    # Show rename prompt
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Rename File", callback_data=f"rename:{storage_key}")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data=f"cancel_rename:{storage_key}")]
    ])

    await message.answer(
        f"<b>📹 {small_caps('Video Received')}</b>\n\n"
        f"<b>{small_caps('Original Name:')}</b>\n"
        f"<code>{original_filename}</code>\n\n"
        f"<blockquote>{small_caps('Do you want to rename this file?')}</blockquote>",
        parse_mode="HTML",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("rename:"))
async def prompt_rename(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Ask user for new filename."""
    storage_key = callback.data.split(":", 1)[1]

    if storage_key not in video_storage:
        await callback.answer(small_caps("Session expired! Please send the video again."), show_alert=True)
        return

    # Store the storage key in FSM state
    await state.set_state(VideoRenameState.waiting_for_filename)
    await state.update_data(storage_key=storage_key)

    # Delete the rename prompt message
    try:
        await callback.message.delete()
    except Exception:
        pass

    # Ask for new filename
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Cancel", callback_data=f"cancel_input:{storage_key}")]
    ])

    await bot.send_message(
        chat_id=callback.message.chat.id,
        text=f"<b>✏️ {small_caps('Enter New Filename')}</b>\n\n"
             f"<blockquote>{small_caps('Send me the new filename for your video.')}</blockquote>\n"
             f"<i>{small_caps('Example: My_Video, Episode_01, Movie_2024')}</i>\n\n"
             f"<i>{small_caps('.mp4 will be added automatically')}</i>",
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(F.data.startswith("cancel_rename:"))
async def cancel_rename_send_video(callback: types.CallbackQuery, bot: Bot):
    """Send video with original filename."""
    storage_key = callback.data.split(":", 1)[1]

    if storage_key not in video_storage:
        await callback.answer(small_caps("Session expired!"), show_alert=True)
        return

    data = video_storage.pop(storage_key)

    # Delete the prompt message
    try:
        await callback.message.delete()
    except Exception:
        pass

    # Increment usage count
    await increment_usage(data["user_id"])

    # Get original filename for auto caption
    original_filename = data.get("original_filename", "video.mp4")
    
    # Generate auto caption if enabled
    auto_caption = await generate_auto_caption(original_filename, data["user_id"])
    
    # Combine with user's caption if exists
    final_caption = data["caption"]
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
        chat_id=callback.message.chat.id,
        video=data["video_file_id"],
        caption=final_caption,
        cover=data["thumb_file_id"],
        filename=original_filename,
        reply_markup=keyboard
    )

    # Log to channel
    if LOG_CHANNEL:
        try:
            await bot.send_message(
                chat_id=LOG_CHANNEL,
                text=f"📹 <b>ᴠɪᴅᴇᴏ ᴘʀᴏᴄᴇssᴇᴅ</b>\n\n"
                     f"🆔 <code>{data['user_id']}</code>\n"
                     f"👤 {data['first_name']} (@{data['username'] or 'N/A'})\n"
                     f"📄 <code>{original_filename}</code>\n"
                     f"📝 {data['caption'][:50] + '...' if len(data['caption']) > 50 else data['caption'] or 'No caption'}",
                parse_mode="HTML"
            )
        except Exception:
            pass

    await callback.answer(small_caps("Video sent!"))

@router.callback_query(F.data.startswith("cancel_input:"))
async def cancel_filename_input(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Cancel filename input and send video with original name."""
    storage_key = callback.data.split(":", 1)[1]

    await state.clear()

    if storage_key not in video_storage:
        await callback.answer(small_caps("Session expired!"), show_alert=True)
        return

    data = video_storage.pop(storage_key)

    # Delete the input prompt message
    try:
        await callback.message.delete()
    except Exception:
        pass

    # Increment usage count
    await increment_usage(data["user_id"])

    # Get original filename for auto caption
    original_filename = data.get("original_filename", "video.mp4")
    
    # Generate auto caption if enabled
    auto_caption = await generate_auto_caption(original_filename, data["user_id"])
    
    # Combine with user's caption if exists
    final_caption = data["caption"]
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
        chat_id=callback.message.chat.id,
        video=data["video_file_id"],
        caption=final_caption,
        cover=data["thumb_file_id"],
        filename=original_filename,
        reply_markup=keyboard
    )

    # Log to channel
    if LOG_CHANNEL:
        try:
            await bot.send_message(
                chat_id=LOG_CHANNEL,
                text=f"📹 <b>ᴠɪᴅᴇᴏ ᴘʀᴏᴄᴇssᴇᴅ</b>\n\n"
                     f"🆔 <code>{data['user_id']}</code>\n"
                     f"👤 {data['first_name']} (@{data['username'] or 'N/A'})\n"
                     f"📄 <code>{original_filename}</code>\n"
                     f"📝 {data['caption'][:50] + '...' if len(data['caption']) > 50 else data['caption'] or 'No caption'}",
                parse_mode="HTML"
            )
        except Exception:
            pass

    await callback.answer(small_caps("Video sent with original name!"))

@router.message(VideoRenameState.waiting_for_filename)
async def receive_filename_and_send(message: types.Message, state: FSMContext, bot: Bot):
    """Receive filename and send video with new name."""
    user_data = await state.get_data()
    storage_key = user_data.get("storage_key")

    if not storage_key or storage_key not in video_storage:
        await state.clear()
        await message.answer(small_caps("Session expired! Please send the video again."))
        return

    data = video_storage.pop(storage_key)
    await state.clear()

    # Get and validate filename
    filename = message.text.strip()
    import re
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)

    if not filename:
        await message.answer(
            f"<b>❌ {small_caps('Invalid filename!')}</b>\n\n"
            f"<blockquote>{small_caps('Please send a valid filename without special characters.')}</blockquote>",
            parse_mode="HTML"
        )
        # Put data back since user needs to retry
        video_storage[storage_key] = data
        await state.set_state(VideoRenameState.waiting_for_filename)
        await state.update_data(storage_key=storage_key)
        return

    # Limit filename length (Telegram limit)
    if len(filename) > 100:
        filename = filename[:100]

    # Increment usage count
    await increment_usage(data["user_id"])

    # Generate auto caption with the NEW filename
    new_filename = f"{filename}.mp4"
    auto_caption = await generate_auto_caption(new_filename, data["user_id"])
    
    # Combine with user's caption if exists
    final_caption = data["caption"]
    if auto_caption:
        if final_caption:
            final_caption = f"{auto_caption}\n\n{final_caption}"
        else:
            final_caption = auto_caption

    # Send video with new filename (instant rename - no download/upload)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ Settings", callback_data="settings")]
    ])

    await bot.send_video(
        chat_id=message.chat.id,
        video=data["video_file_id"],
        caption=final_caption,
        cover=data["thumb_file_id"],
        filename=new_filename,
        reply_markup=keyboard
    )

    await message.answer(
        f"<b>✅ {small_caps('Video sent!')}</b>\n\n"
        f"<b>{small_caps('Filename:')}</b> <code>{new_filename}</code>",
        parse_mode="HTML"
    )

    # Log to channel
    if LOG_CHANNEL:
        try:
            await bot.send_message(
                chat_id=LOG_CHANNEL,
                text=f"📹 <b>ᴠɪᴅᴇᴏ ʀᴇɴᴀᴍᴇᴅ & ᴘʀᴏᴄᴇssᴇᴅ</b>\n\n"
                     f"🆔 <code>{data['user_id']}</code>\n"
                     f"👤 {data['first_name']} (@{data['username'] or 'N/A'})\n"
                     f"📄 <code>{new_filename}</code>\n"
                     f"📝 {data['caption'][:50] + '...' if len(data['caption']) > 50 else data['caption'] or 'No caption'}",
                parse_mode="HTML"
            )
        except Exception:
            pass

# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat
