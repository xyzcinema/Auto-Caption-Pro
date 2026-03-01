# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat
from aiogram import Router, types, F, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest
# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat
from database import (
    get_auto_caption_enabled, set_auto_caption_enabled,
    get_caption_style, set_caption_style,
    get_custom_caption, set_custom_caption,
    is_banned
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

class CaptionState(StatesGroup):
    waiting_for_custom_caption = State()

# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat

# Caption style options with their formats
CAPTION_STYLES = {
    "default": {
        "name": "Default",
        "format": "{filename}",
        "description": "Just the filename"
    },
    "uppercase": {
        "name": "UPPERCASE",
        "format": "{filename}",
        "description": "FILENAME in all caps"
    },
    "lowercase": {
        "name": "lowercase",
        "format": "{filename}",
        "description": "filename in lowercase"
    },
    "title_case": {
        "name": "Title Case",
        "format": "{filename}",
        "description": "File Name (Title Case)"
    },
    "with_emoji": {
        "name": "With Emoji",
        "format": "📹 {filename}",
        "description": "📹 Filename"
    },
    "boxed": {
        "name": "Boxed",
        "format": "「{filename}」",
        "description": "「Filename」in brackets"
    },
    "starred": {
        "name": "Starred",
        "format": "✦ {filename} ✦",
        "description": "✦ Filename ✦"
    },
    "dash_style": {
        "name": "Dash Style",
        "format": "— {filename} —",
        "description": "— Filename —"
    },
    "arrow_style": {
        "name": "Arrow Style",
        "format": "▶ {filename}",
        "description": "▶ Filename"
    },
    "custom": {
        "name": "Custom",
        "format": "{custom}",
        "description": "Your own custom caption"
    }
}
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
# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat

def format_filename(filename: str, style: str, custom_caption: str = "") -> str:
    """
    Format filename according to the selected style.
    Replaces underscores with spaces in the filename.
    """
    # Remove .mp4 extension for display
    display_name = filename
    if display_name.lower().endswith('.mp4'):
        display_name = display_name[:-4]
    
    # Replace underscores with spaces
    display_name = display_name.replace("_", " ")
    
    # Get style configuration
    style_config = CAPTION_STYLES.get(style, CAPTION_STYLES["default"])
    
    # Apply transformations based on style
    if style == "uppercase":
        formatted = display_name.upper()
    elif style == "lowercase":
        formatted = display_name.lower()
    elif style == "title_case":
        # Convert to title case
        formatted = display_name.title()
    elif style == "custom" and custom_caption:
        # Use custom caption, replace {filename} placeholder if present
        formatted = custom_caption.replace("{filename}", display_name)
    else:
        # Default and other styles
        formatted = display_name
    
    # Apply the format template
    if style == "custom" and custom_caption:
        # For custom, already replaced above
        return formatted
    else:
        return style_config["format"].format(filename=formatted)
# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat

async def generate_auto_caption(filename: str, user_id: int) -> str:
    """
    Generate auto caption for a video file.
    Returns formatted caption based on user's settings.
    """
    # Check if auto caption is enabled
    auto_caption_enabled = await get_auto_caption_enabled(user_id)
    
    if not auto_caption_enabled:
        return None
    
    # Get user's caption style
    style = await get_caption_style(user_id)
    
    # Get custom caption if style is custom
    custom_caption = ""
    if style == "custom":
        custom_caption = await get_custom_caption(user_id) or "{filename}"
    
    # Format and return the caption
    return format_filename(filename, style, custom_caption)
# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat

def get_caption_settings_keyboard(auto_caption_enabled: bool, current_style: str):
    """Generate keyboard for caption settings."""
    status = "✅" if auto_caption_enabled else "❌"
    
    keyboard = [
        [InlineKeyboardButton(text=f"{status} Auto Caption", callback_data="toggle_auto_caption")],
        [InlineKeyboardButton(text="🎨 Caption Style", callback_data="caption_style_menu")],
    ]
    
    # Add custom caption button if custom style is selected
    if current_style == "custom":
        keyboard.append([InlineKeyboardButton(text="✏️ Edit Custom Caption", callback_data="edit_custom_caption")])
    
    keyboard.extend([
        [InlineKeyboardButton(text="🔙 Back to Settings", callback_data="settings")],
        [InlineKeyboardButton(text="❌ Close", callback_data="close_caption")]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat

def get_style_selection_keyboard(current_style: str):
    """Generate keyboard for style selection."""
    keyboard = []
    
    # Create rows with 2 buttons each
    style_items = list(CAPTION_STYLES.items())
    for i in range(0, len(style_items), 2):
        row = []
        for j in range(i, min(i + 2, len(style_items))):
            style_key, style_info = style_items[j]
            prefix = "✅ " if style_key == current_style else ""
            row.append(InlineKeyboardButton(
                text=f"{prefix}{style_info['name']}",
                callback_data=f"set_style:{style_key}"
            ))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton(text="🔙 Back", callback_data="caption_settings")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat

@router.callback_query(F.data == "caption_settings")
async def show_caption_settings(callback: CallbackQuery, bot: Bot):
    """Show auto caption settings menu."""
    user_id = callback.from_user.id
    
    if await is_banned(user_id):
        await callback.answer(small_caps("You are banned!"), show_alert=True)
        return
    
    # Get user's current settings
    auto_caption_enabled = await get_auto_caption_enabled(user_id)
    current_style = await get_caption_style(user_id)
    
    style_name = CAPTION_STYLES.get(current_style, CAPTION_STYLES["default"])["name"]
    status_text = "Enabled" if auto_caption_enabled else "Disabled"
    
    text = (
        f"<b>📝 {small_caps('Auto Caption Settings')}</b>\n\n"
        f"<blockquote>"
        f"{small_caps('Status')}: {status_text}\n"
        f"{small_caps('Style')}: {style_name}"
        f"</blockquote>\n\n"
        f"<b>{small_caps('Preview:')}</b>\n"
        f"<blockquote>"
    )
    
    # Show preview with a sample filename (underscores removed)
    sample_filename = "My_Video_File_2024.mp4"
    custom_caption = await get_custom_caption(user_id) if current_style == "custom" else ""
    preview = format_filename(sample_filename, current_style, custom_caption)
    text += f"{preview}"
    text += f"</blockquote>\n\n"
    text += f"<i>{small_caps('Underscores are replaced with spaces')}</i>"
    
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass
    
    await bot.send_message(
        chat_id=callback.message.chat.id,
        text=text,
        parse_mode="HTML",
        reply_markup=get_caption_settings_keyboard(auto_caption_enabled, current_style)
    )
    await callback.answer()
# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat

@router.callback_query(F.data == "toggle_auto_caption")
async def toggle_auto_caption(callback: CallbackQuery, bot: Bot):
    """Toggle auto caption on/off."""
    user_id = callback.from_user.id
    
    current_status = await get_auto_caption_enabled(user_id)
    new_status = not current_status
    
    await set_auto_caption_enabled(user_id, new_status)
    
    await callback.answer(
        small_caps(f"Auto Caption {'Enabled' if new_status else 'Disabled'}"),
        show_alert=True
    )
    
    # Refresh the settings menu
    await show_caption_settings(callback, bot)
# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat

@router.callback_query(F.data == "caption_style_menu")
async def show_style_menu(callback: CallbackQuery, bot: Bot):
    """Show caption style selection menu."""
    user_id = callback.from_user.id
    current_style = await get_caption_style(user_id)
    
    text = (
        f"<b>🎨 {small_caps('Select Caption Style')}</b>\n\n"
        f"<blockquote>{small_caps('Choose how your caption will look:')}</blockquote>\n\n"
    )
    
    # List all styles with descriptions
    for style_key, style_info in CAPTION_STYLES.items():
        prefix = "✅ " if style_key == current_style else ""
        text += f"<b>{prefix}{style_info['name']}</b> - <i>{style_info['description']}</i>\n"
    
    text += f"\n<i>{small_caps('Underscores will be replaced with spaces')}</i>"
    
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass
    
    await bot.send_message(
        chat_id=callback.message.chat.id,
        text=text,
        parse_mode="HTML",
        reply_markup=get_style_selection_keyboard(current_style)
    )
    await callback.answer()
# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat

@router.callback_query(F.data.startswith("set_style:"))
async def set_caption_style_handler(callback: CallbackQuery, bot: Bot):
    """Handle style selection."""
    user_id = callback.from_user.id
    style = callback.data.split(":", 1)[1]
    
    if style in CAPTION_STYLES:
        await set_caption_style(user_id, style)
        style_name = CAPTION_STYLES[style]["name"]
        await callback.answer(small_caps(f"Style set to: {style_name}"), show_alert=True)
    
    # Go back to caption settings
    await show_caption_settings(callback, bot)
# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat

@router.callback_query(F.data == "edit_custom_caption")
async def edit_custom_caption_prompt(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Prompt user to enter custom caption."""
    user_id = callback.from_user.id
    current_custom = await get_custom_caption(user_id) or ""
    
    await state.set_state(CaptionState.waiting_for_custom_caption)
    
    text = (
        f"<b>✏️ {small_caps('Enter Custom Caption')}</b>\n\n"
        f"<blockquote>{small_caps('Send me your custom caption text.')}</blockquote>\n\n"
        f"<b>{small_caps('Available placeholders:')}</b>\n"
        f"<code>{{filename}}</code> - {small_caps('Will be replaced with the video filename')}\n\n"
    )
    
    if current_custom:
        text += f"<b>{small_caps('Current:')}</b> <code>{current_custom}</code>\n\n"
    
    text += f"<i>{small_caps('Example: Watch {filename} now!')}</i>"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Back", callback_data="caption_settings")]
    ])
    
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass
    
    await bot.send_message(
        chat_id=callback.message.chat.id,
        text=text,
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await callback.answer()
# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat

@router.message(CaptionState.waiting_for_custom_caption)
async def receive_custom_caption(message: types.Message, state: FSMContext, bot: Bot):
    """Save the custom caption."""
    user_id = message.from_user.id
    custom_caption = message.text.strip()
    
    await set_custom_caption(user_id, custom_caption)
    await state.clear()
    
    # Show preview (underscores replaced with spaces)
    sample_filename = "My_Video_File_2024.mp4"
    preview = custom_caption.replace("{filename}", "My Video File 2024")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ Caption Settings", callback_data="caption_settings")]
    ])
    
    await message.answer(
        f"<b>✅ {small_caps('Custom Caption Saved!')}</b>\n\n"
        f"<b>{small_caps('Preview:')}</b>\n"
        f"<blockquote>{preview}</blockquote>",
        parse_mode="HTML",
        reply_markup=keyboard
    )
# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat

@router.callback_query(F.data == "close_caption")
async def close_caption_settings(callback: CallbackQuery):
    """Close caption settings."""
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass
    await callback.answer(small_caps("Caption settings closed"))
# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat
