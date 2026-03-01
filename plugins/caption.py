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
    is_banned, set_auto_caption, get_auto_caption,
    set_caption_template, get_caption_template,
    set_caption_style, get_caption_style,
    set_replace_underscores, get_replace_underscores,
    set_show_extension, get_show_extension,
    set_caption_position, get_caption_position
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
    waiting_for_template = State()

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

def get_caption_menu_keyboard(auto_caption: bool) -> InlineKeyboardMarkup:
    """Return the caption menu keyboard."""
    status = "✅ ON" if auto_caption else "❌ OFF"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🤖 Auto Caption: {status}", callback_data="toggle_auto_caption")],
        [InlineKeyboardButton(text="📝 Caption Template", callback_data="caption_template")],
        [InlineKeyboardButton(text="🎨 Caption Style", callback_data="caption_style")],
        [InlineKeyboardButton(text="🔤 Replace _ to Space", callback_data="caption_underscore")],
        [InlineKeyboardButton(text="📎 Show Extension", callback_data="caption_extension")],
        [InlineKeyboardButton(text="📍 Caption Position", callback_data="caption_position")],
        [InlineKeyboardButton(text="👁️ Preview Caption", callback_data="preview_caption")],
        [InlineKeyboardButton(text="🔙 Back to Settings", callback_data="settings")],
    ])

def get_style_keyboard(current_style: str) -> InlineKeyboardMarkup:
    """Return style selection keyboard."""
    styles = [
        ("📝 Normal", "normal"),
        ("𝗕 Bold", "bold"),
        ("𝚃𝚎𝚡𝚝 Mono", "mono"),
        ("𝗠𝗼𝗻𝗼 Bold+Mono", "bold_mono")
    ]
    buttons = []
    for label, style in styles:
        mark = "✅ " if current_style == style else ""
        buttons.append([InlineKeyboardButton(text=f"{mark}{label}", callback_data=f"set_style_{style}")])
    buttons.append([InlineKeyboardButton(text="🔙 Back", callback_data="caption_settings")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_position_keyboard(current_position: str) -> InlineKeyboardMarkup:
    """Return position selection keyboard."""
    positions = [
        ("🔄 Replace Original", "replace"),
        ("⬆️ Before Original", "before"),
        ("⬇️ After Original", "after")
    ]
    buttons = []
    for label, position in positions:
        mark = "✅ " if current_position == position else ""
        buttons.append([InlineKeyboardButton(text=f"{mark}{label}", callback_data=f"set_position_{position}")])
    buttons.append([InlineKeyboardButton(text="🔙 Back", callback_data="caption_settings")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_template_help_keyboard() -> InlineKeyboardMarkup:
    """Return template help keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Done", callback_data="caption_settings")],
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

@router.callback_query(F.data == "caption_settings")
async def show_caption_settings(callback: CallbackQuery, bot: Bot):
    """Show caption settings menu."""
    user_id = callback.from_user.id
    
    if await is_banned(user_id):
        await callback.answer(small_caps("You are banned!"), show_alert=True)
        return
    
    auto_caption = await get_auto_caption(user_id)
    
    text = (
        f"<b>📝 {small_caps('Auto Caption Settings')}</b>\n\n"
        f"<blockquote>"
        f"🤖 {small_caps('Auto Caption')}: {'✅ ON' if auto_caption else '❌ OFF'}\n"
        f"🔤 {small_caps('Replace _ with spaces')}\n"
        f"📎 {small_caps('Show full filename')}\n"
        f"🎨 {small_caps('Custom styles: Bold/Mono')}\n"
        f"📍 {small_caps('Position: Before/After/Replace')}"
        f"</blockquote>\n\n"
        f"{small_caps('Choose an option below:')}"
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

@router.callback_query(F.data == "caption_template")
async def show_template_info(callback: CallbackQuery, bot: Bot):
    """Show caption template information."""
    user_id = callback.from_user.id
    template = await get_caption_template(user_id)
    
    text = (
        f"<b>📝 {small_caps('Caption Template')}</b>\n\n"
        f"<blockquote>"
        f"{small_caps('Current Template:')}\n"
        f"<code>{template}</code>"
        f"</blockquote>\n\n"
        f"<b>📌 {small_caps('Available Variables:')}</b>\n"
        f"<blockquote>"
        f"<code>{{filename}}</code> - {small_caps('Video filename')}\n"
        f"<code>{{original}}</code> - {small_caps('Original caption')}\n"
        f"</blockquote>\n\n"
        f"<b>💡 {small_caps('Examples:')}</b>\n"
        f"<blockquote>"
        f"<code>{{filename}}</code> - {small_caps('Just filename')}\n"
        f"<code>📁 {{filename}}</code> - {small_caps('With emoji')}\n"
        f"<code>{{filename}}\n\n{{original}}</code> - {small_caps('With original')}\n"
        f"<code>🎬 {{filename}} | @YourChannel</code> - {small_caps('With channel')}\n"
        f"</blockquote>\n\n"
        f"{small_caps('Send new template or click Done:')}"
    )
    
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass
    
    await bot.send_message(
        chat_id=callback.message.chat.id,
        text=text,
        parse_mode="HTML",
        reply_markup=get_template_help_keyboard()
    )
    await callback.answer()

@router.message(CaptionState.waiting_for_template)
async def receive_template(message: types.Message, state: FSMContext):
    """Receive and save new caption template."""
    user_id = message.from_user.id
    template = message.text
    
    await set_caption_template(user_id, template)
    await state.clear()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ Caption Settings", callback_data="caption_settings")]
    ])
    
    await message.answer(
        f"<b>✅ {small_caps('Template Saved!')}</b>\n\n"
        f"<blockquote><code>{template}</code></blockquote>",
        parse_mode="HTML",
        reply_markup=keyboard
    )

@router.callback_query(F.data == "caption_style")
async def show_style_menu(callback: CallbackQuery, bot: Bot):
    """Show caption style menu."""
    user_id = callback.from_user.id
    current_style = await get_caption_style(user_id)
    
    style_names = {
        "normal": "Normal",
        "bold": "Bold",
        "mono": "Mono",
        "bold_mono": "Bold + Mono"
    }
    
    text = (
        f"<b>🎨 {small_caps('Caption Style')}</b>\n\n"
        f"<blockquote>"
        f"{small_caps('Current:')} {style_names.get(current_style, 'Normal')}\n\n"
        f"📝 {small_caps('Normal')}: My Video File\n"
        f"𝗕 {small_caps('Bold')}: <b>My Video File</b>\n"
        f"𝚃𝚎𝚡𝚝 {small_caps('Mono')}: <code>My Video File</code>\n"
        f"𝗠𝗼𝗻𝗼 {small_caps('Bold+Mono')}: <b><code>My Video File</code></b>"
        f"</blockquote>\n\n"
        f"{small_caps('Select a style:')}"
    )
    
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass
    
    await bot.send_message(
        chat_id=callback.message.chat.id,
        text=text,
        parse_mode="HTML",
        reply_markup=get_style_keyboard(current_style)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("set_style_"))
async def set_style_handler(callback: CallbackQuery, bot: Bot):
    """Set caption style."""
    user_id = callback.from_user.id
    style = callback.data.replace("set_style_", "")
    
    await set_caption_style(user_id, style)
    await show_style_menu(callback, bot)
    await callback.answer("Style updated!")

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

@router.callback_query(F.data == "caption_position")
async def show_position_menu(callback: CallbackQuery, bot: Bot):
    """Show caption position menu."""
    user_id = callback.from_user.id
    current_position = await get_caption_position(user_id)
    
    position_names = {
        "replace": "Replace Original",
        "before": "Before Original",
        "after": "After Original"
    }
    
    text = (
        f"<b>📍 {small_caps('Caption Position')}</b>\n\n"
        f"<blockquote>"
        f"{small_caps('Current:')} {position_names.get(current_position, 'Replace')}\n\n"
        f"🔄 {small_caps('Replace')}: {small_caps('Replace original caption')}\n"
        f"⬆️ {small_caps('Before')}: {small_caps('Add before original caption')}\n"
        f"⬇️ {small_caps('After')}: {small_caps('Add after original caption')}"
        f"</blockquote>\n\n"
        f"{small_caps('Select position:')}"
    )
    
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass
    
    await bot.send_message(
        chat_id=callback.message.chat.id,
        text=text,
        parse_mode="HTML",
        reply_markup=get_position_keyboard(current_position)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("set_position_"))
async def set_position_handler(callback: CallbackQuery, bot: Bot):
    """Set caption position."""
    user_id = callback.from_user.id
    position = callback.data.replace("set_position_", "")
    
    await set_caption_position(user_id, position)
    await show_position_menu(callback, bot)
    await callback.answer("Position updated!")

@router.callback_query(F.data == "preview_caption")
async def preview_caption(callback: CallbackQuery, bot: Bot):
    """Show caption preview."""
    user_id = callback.from_user.id
    
    template = await get_caption_template(user_id)
    style = await get_caption_style(user_id)
    replace_underscores = await get_replace_underscores(user_id)
    show_extension = await get_show_extension(user_id)
    position = await get_caption_position(user_id)
    
    # Sample filename for preview
    sample_filename = "My_Awesome_Video_File.mp4"
    sample_original = "This is the original caption from the video."
    
    preview = generate_caption(
        template, sample_filename, sample_original,
        replace_underscores, show_extension, style, position
    )
    
    text = (
        f"<b>👁️ {small_caps('Caption Preview')}</b>\n\n"
        f"<b>📄 {small_caps('Sample Filename:')}</b> <code>{sample_filename}</code>\n"
        f"<b>📝 {small_caps('Original Caption:')}</b> <code>{sample_original}</code>\n\n"
        f"<b>✨ {small_caps('Result:')}</b>\n"
        f"<blockquote>{preview}</blockquote>"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ Caption Settings", callback_data="caption_settings")]
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
