# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat
from aiogram import Router, types, F, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat
from config import LOG_CHANNEL
from database import (
    get_thumbnail, increment_usage, is_banned, add_user,
    get_auto_caption, get_caption_format,
    get_replace_underscores, get_show_extension
)
# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat
router = Router()
# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat

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

def format_filename(filename: str, replace_underscores: bool, show_extension: bool) -> str:
    """Format filename according to settings."""
    if not filename:
        return "Unknown File"
    
    # Replace underscores with spaces
    if replace_underscores:
        filename = filename.replace("_", " ")
    
    # Hide extension if needed
    if not show_extension:
        if "." in filename:
            filename = filename.rsplit(".", 1)[0]
    
    return filename

def generate_caption(caption_format: str, filename: str, 
                     replace_underscores: bool, show_extension: bool) -> str:
    """Generate the final caption based on format and settings."""
    # Format the filename
    formatted_filename = format_filename(filename, replace_underscores, show_extension)
    
    # Replace {filename} with the formatted filename
    caption = caption_format.replace("{filename}", formatted_filename)
    
    return caption

# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat

@router.message(F.video)
async def handle_video(message: types.Message, bot: Bot):
    """Handle incoming video and send it back with user's thumbnail as cover."""
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
    
    # Get video filename - use file_name if available, otherwise use a default
    video_filename = video.file_name if video.file_name else f"video_{video.file_unique_id}.mp4"
    
    # Get original caption
    original_caption = message.caption or ""
    
    # Check if auto caption is enabled
    auto_caption_enabled = await get_auto_caption(user_id)
    
    if auto_caption_enabled:
        # Get caption settings
        caption_format = await get_caption_format(user_id)
        replace_underscores = await get_replace_underscores(user_id)
        show_extension = await get_show_extension(user_id)
        
        # Generate new caption
        final_caption = generate_caption(
            caption_format, video_filename,
            replace_underscores, show_extension
        )
    else:
        # Keep original caption if auto caption is disabled
        final_caption = original_caption
    
    # Get user's thumbnail
    thumb_file_id = await get_thumbnail(user_id)
    
    if thumb_file_id:
        # Increment usage count
        await increment_usage(user_id)
        
        # Send video with custom cover (no settings button)
        await bot.send_video(
            chat_id=message.chat.id,
            video=video.file_id,
            caption=final_caption,
            parse_mode="HTML",
            cover=thumb_file_id
        )
        
        # Log video to log channel
        if LOG_CHANNEL:
            try:
                log_caption = final_caption[:50] + '...' if len(final_caption) > 50 else final_caption or 'No caption'
                await bot.send_message(
                    chat_id=LOG_CHANNEL,
                    text=f"📹 <b>ᴠɪᴅᴇᴏ ᴘʀᴏᴄᴇssᴇᴅ</b>\n\n"
                         f"🆔 <code>{user_id}</code>\n"
                         f"👤 {first_name} (@{username or 'N/A'})\n"
                         f"📄 <code>{video_filename}</code>\n"
                         f"📝 {log_caption}",
                    parse_mode="HTML"
                )
            except Exception:
                pass
    else:
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
# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat
