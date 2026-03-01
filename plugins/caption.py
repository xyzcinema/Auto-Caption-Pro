# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat
from aiogram import Router, types, F, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat
from database import (
    is_banned, set_auto_caption, get_auto_caption,
    set_caption_format, get_caption_format,
    set_replace_underscores, get_replace_underscores,
    set_show_extension, get_show_extension
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
    waiting_for_caption_format = State()

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

def get_caption_menu_keyboard(auto_caption: bool) -> InlineKeyboardMarkup:
    """Return the caption menu keyboard."""
    status = "✅ ON" if auto_caption else "❌ OFF"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🤖 Auto Caption: {status}", callback_data="toggle_auto_caption")],
        [InlineKeyboardButton(text="📝 Set Caption Format", callback_data="set_caption_format_menu")],
        [InlineKeyboardButton(text="🔤 Replace _ to Space", callback_data="caption_underscore")],
        [InlineKeyboardButton(text="📎 Show Extension", callback_data="caption_extension")],
        [InlineKeyboardButton(text="🔙 Back to Settings", callback_data="settings")],
    ])

def get_underscore_keyboard(enabled: bool) -> InlineKeyboardMarkup:
    """Return underscore settings keyboard."""
    status = "✅ ON" if enabled else "❌ OFF"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🔄 Toggle: {status}", callback_data="toggle_underscore")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="caption_settings")],
    ])

def get_extension_keyboard(enabled: bool) -> InlineKeyboardMarkup:
    """Return extension settings keyboard."""
    status = "✅ ON" if enabled else "❌ OFF"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🔄 Toggle: {status}", callback_data="toggle_extension")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="caption_settings")],
    ])

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

@router.callback_query(F.data == "caption_settings")
async def show_caption_settings(callback: CallbackQuery, bot: Bot):
    """Show caption settings menu."""
    user_id = callback.from_user.id
    
    if await is_banned(user_id):
        await callback.answer(small_caps("You are banned!"), show_alert=True)
        return
    
    auto_caption = await get_auto_caption(user_id)
    caption_format = await get_caption_format(user_id)
    
    text = (
        f"<b>📝 {small_caps('Auto Caption Settings')}</b>\n\n"
        f"<blockquote>"
        f"🤖 {small_caps('Auto Caption')}: {'✅ ON' if auto_caption else '❌ OFF'}\n"
        f"📝 {small_caps('Format')}: <code>{caption_format}</code>\n\n"
        f"💡 {small_caps('Use')} <code>/setcaption</code> {small_caps('to set format')}\n"
        f"💡 {small_caps('Example:')} <code>/setcaption &lt;b&gt;{{filename}}&lt;/b&gt;</code>"
        f"</blockquote>"
    )
    
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass
    
    await bot.send_message(
        chat_id=callback.message.chat.id,
        text=text,
        parse_mode="HTML",
        reply_markup=get_caption_menu_keyboard(auto_caption)
    )
    await callback.answer()

@router.callback_query(F.data == "toggle_auto_caption")
async def toggle_auto_caption_handler(callback: CallbackQuery, bot: Bot):
    """Toggle auto caption on/off."""
    user_id = callback.from_user.id
    
    current = await get_auto_caption(user_id)
    new_state = not current
    await set_auto_caption(user_id, new_state)
    
    await show_caption_settings(callback, bot)
    await callback.answer(f"Auto Caption {'enabled' if new_state else 'disabled'}!")

@router.callback_query(F.data == "set_caption_format_menu")
async def show_set_caption_format(callback: CallbackQuery, bot: Bot):
    """Show how to set caption format."""
    user_id = callback.from_user.id
    current_format = await get_caption_format(user_id)
    
    text = (
        f"<b>📝 {small_caps('Set Caption Format')}</b>\n\n"
        f"<b>{small_caps('Current Format:')}</b>\n"
        f"<blockquote><code>{current_format}</code></blockquote>\n\n"
        f"<b>📌 {small_caps('Available Variable:')}</b>\n"
        f"<blockquote><code>{{filename}}</code> - {small_caps('Video filename')}</blockquote>\n\n"
        f"<b>🎨 {small_caps('HTML Tags Supported:')}</b>\n"
        f"<blockquote>"
        f"<code>&lt;b&gt;text&lt;/b&gt;</code> - <b>Bold</b>\n"
        f"<code>&lt;i&gt;text&lt;/i&gt;</code> - <i>Italic</i>\n"
        f"<code>&lt;code&gt;text&lt;/code&gt;</code> - <code>Mono</code>\n"
        f"<code>&lt;u&gt;text&lt;/u&gt;</code> - <u>Underline</u>\n"
        f"<code>&lt;s&gt;text&lt;/s&gt;</code> - <s>Strikethrough</s>\n"
        f"<code>&lt;a href='url'&gt;text&lt;/a&gt;</code> - {small_caps('Link')}\n"
        f"<code>&lt;spoiler&gt;text&lt;/spoiler&gt;</code> - {small_caps('Spoiler')}\n"
        f"</blockquote>\n\n"
        f"<b>💡 {small_caps('Examples:')}</b>\n"
        f"<blockquote>"
        f"<code>/setcaption &lt;b&gt;{{filename}}&lt;/b&gt;</code>\n"
        f"<code>/setcaption 📁 &lt;code&gt;{{filename}}&lt;/code&gt;</code>\n"
        f"<code>/setcaption &lt;b&gt;🎬 {{filename}}&lt;/b&gt; | &lt;a href='https://t.me/yourchannel'&gt;Join&lt;/a&gt;</code>\n"
        f"<code>/setcaption &lt;i&gt;{{filename}}&lt;/i&gt; | Size: 1080p</code>"
        f"</blockquote>\n\n"
        f"{small_caps('Send')} <code>/setcaption &lt;your format&gt;</code> {small_caps('to set')}."
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Back", callback_data="caption_settings")],
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

@router.message(Command("setcaption"))
async def setcaption_cmd(message: types.Message):
    """Set caption format via command."""
    user_id = message.from_user.id
    
    if await is_banned(user_id):
        await message.answer(small_caps("You are banned from using this bot."))
        return
    
    # Get the caption format from command
    args = message.text.split(" ", 1)
    
    if len(args) < 2:
        # Show current format and help
        current_format = await get_caption_format(user_id)
        
        help_text = (
            f"<b>📝 {small_caps('Set Caption Format')}</b>\n\n"
            f"<b>{small_caps('Current Format:')}</b>\n"
            f"<blockquote><code>{current_format}</code></blockquote>\n\n"
            f"<b>📌 {small_caps('Usage:')}</b>\n"
            f"<code>/setcaption &lt;format&gt;</code>\n\n"
            f"<b>💡 {small_caps('Examples:')}</b>\n"
            f"<blockquote>"
            f"<code>/setcaption {{filename}}</code> - {small_caps('Just filename')}\n"
            f"<code>/setcaption &lt;b&gt;{{filename}}&lt;/b&gt;</code> - {small_caps('Bold filename')}\n"
            f"<code>/setcaption &lt;code&gt;{{filename}}&lt;/code&gt;</code> - {small_caps('Mono filename')}\n"
            f"<code>/setcaption 📁 &lt;b&gt;{{filename}}&lt;/b&gt;</code> - {small_caps('With emoji')}\n"
            f"<code>/setcaption &lt;b&gt;{{filename}}&lt;/b&gt; | &lt;a href='https://t.me/yourchannel'&gt;Join&lt;/a&gt;</code>"
            f"</blockquote>\n\n"
            f"<b>🎨 {small_caps('HTML Tags:')}</b> <code>&lt;b&gt;, &lt;i&gt;, &lt;code&gt;, &lt;u&gt;, &lt;s&gt;, &lt;a&gt;, &lt;spoiler&gt;</code>"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⚙️ Caption Settings", callback_data="caption_settings")],
        ])
        
        await message.answer(help_text, parse_mode="HTML", reply_markup=keyboard)
        return
    
    caption_format = args[1].strip()
    
    # Validate that {filename} is present
    if "{filename}" not in caption_format:
        await message.answer(
            f"<b>❌ {small_caps('Error!')}</b>\n\n"
            f"{small_caps('Your caption format must contain')} <code>{{filename}}</code> {small_caps('variable.')}\n\n"
            f"{small_caps('Example:')} <code>/setcaption &lt;b&gt;{{filename}}&lt;/b&gt;</code>",
            parse_mode="HTML"
        )
        return
    
    # Save the caption format
    await set_caption_format(user_id, caption_format)
    
    # Show preview with sample filename
    sample_filename = "My_Awesome_Video_File.mp4"
    replace_underscores = await get_replace_underscores(user_id)
    show_extension = await get_show_extension(user_id)
    
    formatted_filename = sample_filename.replace("_", " ") if replace_underscores else sample_filename
    if not show_extension and "." in formatted_filename:
        formatted_filename = formatted_filename.rsplit(".", 1)[0]
    
    preview = caption_format.replace("{filename}", formatted_filename)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ Caption Settings", callback_data="caption_settings")],
    ])
    
    await message.answer(
        f"<b>✅ {small_caps('Caption Format Saved!')}</b>\n\n"
        f"<b>{small_caps('Format:')}</b> <code>{caption_format}</code>\n\n"
        f"<b>{small_caps('Preview:')}</b>\n"
        f"<blockquote>{preview}</blockquote>",
        parse_mode="HTML",
        reply_markup=keyboard
    )

@router.callback_query(F.data == "caption_underscore")
async def show_underscore_menu(callback: CallbackQuery, bot: Bot):
    """Show underscore replacement menu."""
    user_id = callback.from_user.id
    enabled = await get_replace_underscores(user_id)
    
    text = (
        f"<b>🔤 {small_caps('Replace Underscores')}</b>\n\n"
        f"<blockquote>"
        f"{small_caps('When enabled, underscores in filenames will be replaced with spaces.')}\n\n"
        f"{small_caps('Example:')}\n"
        f"<code>My_Video_File.mp4</code> → <code>My Video File.mp4</code>"
        f"</blockquote>\n\n"
        f"{small_caps('Current:')} {'✅ ON' if enabled else '❌ OFF'}"
    )
    
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass
    
    await bot.send_message(
        chat_id=callback.message.chat.id,
        text=text,
        parse_mode="HTML",
        reply_markup=get_underscore_keyboard(enabled)
    )
    await callback.answer()

@router.callback_query(F.data == "toggle_underscore")
async def toggle_underscore_handler(callback: CallbackQuery, bot: Bot):
    """Toggle underscore replacement."""
    user_id = callback.from_user.id
    current = await get_replace_underscores(user_id)
    await set_replace_underscores(user_id, not current)
    await show_underscore_menu(callback, bot)
    await callback.answer("Setting updated!")

@router.callback_query(F.data == "caption_extension")
async def show_extension_menu(callback: CallbackQuery, bot: Bot):
    """Show extension display menu."""
    user_id = callback.from_user.id
    enabled = await get_show_extension(user_id)
    
    text = (
        f"<b>📎 {small_caps('Show File Extension')}</b>\n\n"
        f"<blockquote>"
        f"{small_caps('When enabled, file extensions will be shown in the caption.')}\n\n"
        f"{small_caps('Example:')}\n"
        f"✅ ON: <code>My Video File.mp4</code>\n"
        f"❌ OFF: <code>My Video File</code>"
        f"</blockquote>\n\n"
        f"{small_caps('Current:')} {'✅ ON' if enabled else '❌ OFF'}"
    )
    
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass
    
    await bot.send_message(
        chat_id=callback.message.chat.id,
        text=text,
        parse_mode="HTML",
        reply_markup=get_extension_keyboard(enabled)
    )
    await callback.answer()

@router.callback_query(F.data == "toggle_extension")
async def toggle_extension_handler(callback: CallbackQuery, bot: Bot):
    """Toggle extension display."""
    user_id = callback.from_user.id
    current = await get_show_extension(user_id)
    await set_show_extension(user_id, not current)
    await show_extension_menu(callback, bot)
    await callback.answer("Setting updated!")

# CantarellaBots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat
