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
    get_auto_caption, get_caption_template, get_caption_style,
    get_replace_underscores, get_show_extension, get_caption_position
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

def apply_style(text: str, style: str) -> str:
    """Apply text style formatting."""
    if style == "bold":
        return f"<b>{text}</b>"
    elif style == "mono":
        return f"<code>{text}</code>"
    elif style == "bold_mono":
        return f"<b><code>{text}</code></b>"
    return text

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

def generate_caption(template: str, filename: str, original_caption: str, 
                     replace_underscores: bool, show_extension: bool, 
                     style: str, position: str) -> str:
    """Generate the final caption based on template and settings."""
    # Format the filename
    formatted_filename = format_filename(filename, replace_underscores, show_extension)
    
    # Apply style to filename
    styled_filename = apply_style(formatted_filename, style)
    
    # Replace template variables
    caption = template.replace("{filename}", styled_filename)
    caption = caption.replace("{original}", original_caption or "")
    
    # Handle position
    if position == "replace":
        return caption
    elif position == "before":
        if original_caption:
            return f"{caption}\n\n{original_caption}"
        return caption
    elif position == "after":
        if original_caption:
            return f"{original_caption}\n\n{caption}"
        return caption
    
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
        template = await get_caption_template(user_id)
        style = await get_caption_style(user_id)
        replace_underscores = await get_replace_underscores(user_id)
        show_extension = await get_show_extension(user_id)
        position = await get_caption_position(user_id)
        
        # Generate new caption
        final_caption = generate_caption(
            template, video_filename, original_caption,
            replace_underscores, show_extension, style, position
        )
    else:
        # Keep original caption if auto caption is disabled
        final_caption = original_caption
    
    # Get user's thumbnail
    thumb_file_id = await get_thumbnail(user_id)
    
    # Build keyboard
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ Settings", callback_data="settings")]
    ])
    
    if thumb_file_id:
        # Increment usage count
        await increment_usage(user_id)
        
        # Send video with custom cover
        await bot.send_video(
            chat_id=message.chat.id,
            video=video.file_id,
            caption=final_caption,
            cover=thumb_file_id,
            reply_markup=keyboard
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
