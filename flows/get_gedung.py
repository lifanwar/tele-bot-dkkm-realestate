"""Get building details"""
import aiohttp
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import API_BASE_URL, API_KEY


async def get_gedung_detail(query, uuid: str, context):
    """Get building detail by UUID"""
    await query.answer("📥 Memuat detail gedung...")
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{API_BASE_URL}/gedung/{uuid}"
            headers = {
                'accept': 'application/json',
                'X-API-Key': API_KEY
            }
            
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    await show_gedung_detail(query, data, context)
                else:
                    await query.edit_message_text(
                        f"❌ *Error {resp.status}*\n\nGagal memuat data gedung.",
                        parse_mode='Markdown'
                    )
    
    except Exception as e:
        await query.edit_message_text(
            f"❌ *Error*\n\n`{str(e)}`",
            parse_mode='Markdown'
        )


async def show_gedung_detail(query, gedung, context, is_new_message=False):
    """Display building details with beautiful format"""
    
    # Simpan gedung data
    context.user_data['current_gedung'] = gedung
    
    nama = gedung['nama_gedung']
    alamat = gedung['alamat']
    lat = gedung['lat']
    lon = gedung['long']
    total_units = gedung['total_units']
    units = gedung.get('units', [])
    primary_image = gedung.get('primary_image')
    
    # Format text seperti WhatsApp tapi lebih rapi
    text_lines = [
        f"🏢 *{nama}*\n",
        f"📍 *{total_units}* Unit",
        f"📌 *{alamat}*",
        f"[📍 Lihat di Maps](https://www.google.com/maps?q={lat},{lon})\n",
        "━━━━━━━━━━━━━━━━",
        "🏠 *DAFTAR UNIT*",
        "━━━━━━━━━━━━━━━━\n"
    ]
    
    # Keyboard untuk units
    keyboard = []
    
    if units:
        for idx, unit in enumerate(units, 1):
            lantai = unit['lantai']
            unit_num = unit['unit_number']
            deskripsi = unit.get('deskripsi', 'N/A')
            alasan = unit.get('alasan_blacklist', '')
            
            # Format unit info
            text_lines.append(
                f"{idx}. *Lt {lantai} ({unit_num})*\n"
                f"   📝 {deskripsi}"
            )
            
            if alasan:
                text_lines.append(f"   🚫 {alasan}")
            
            text_lines.append("")  # Empty line
            
            # Button untuk unit
            button_text = f"{idx}. Lt {lantai} ({unit_num})"
            keyboard.append([InlineKeyboardButton(
                button_text,
                callback_data=f"unit_{unit['uuid']}"
            )])
        
        text_lines.append("━━━━━━━━━━━━━━━━")
    else:
        text_lines.append("_Tidak ada unit tersedia_\n")
        text_lines.append("━━━━━━━━━━━━━━━━")
    
    # Navigation buttons
    keyboard.append([InlineKeyboardButton("« Back to Awal", callback_data="back_results")])
    keyboard.append([InlineKeyboardButton("🔄 Pencarian Baru", callback_data="search_again")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Gabungkan text
    caption = "\n".join(text_lines)
    
    # Kirim dengan gambar jika ada
    if primary_image:
        try:
            if is_new_message:
                # Kirim sebagai message baru (dari back_to_gedung)
                await query.message.reply_photo(
                    photo=primary_image,
                    caption=caption,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            else:
                # Delete message lama dan kirim dengan photo (normal flow)
                await query.delete_message()
                await query.message.reply_photo(
                    photo=primary_image,
                    caption=caption,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
        except Exception as e:
            # Fallback ke text
            if is_new_message:
                await query.message.reply_text(
                    caption,
                    reply_markup=reply_markup,
                    parse_mode='Markdown',
                    disable_web_page_preview=False
                )
            else:
                try:
                    await query.edit_message_text(
                        caption,
                        reply_markup=reply_markup,
                        parse_mode='Markdown',
                        disable_web_page_preview=False
                    )
                except:
                    await query.message.reply_text(
                        caption,
                        reply_markup=reply_markup,
                        parse_mode='Markdown',
                        disable_web_page_preview=False
                    )
    else:
        if is_new_message:
            await query.message.reply_text(
                caption,
                reply_markup=reply_markup,
                parse_mode='Markdown',
                disable_web_page_preview=False
            )
        else:
            await query.edit_message_text(
                caption,
                reply_markup=reply_markup,
                parse_mode='Markdown',
                disable_web_page_preview=False
            )


async def back_to_results(query, context):
    """Back to search results"""
    await query.answer()
    
    results = context.user_data.get('search_results', [])
    radius = context.user_data.get('search_radius', 0)
    count = len(results)
    
    if not results:
        await query.edit_message_text(
            "❌ Data tidak ditemukan.\n\n"
            "Silakan share lokasi untuk pencarian baru."
        )
        return
    
    # Format text hasil
    text_lines = [
        f"🏢 Ditemukan *{count}* gedung dalam radius {radius}m\n"
    ]
    
    # Buat button untuk setiap gedung
    keyboard = []
    
    for idx, gedung in enumerate(results[:10], 1):
        nama = gedung['nama_gedung']
        alamat = gedung.get('alamat', 'N/A')
        distance = gedung['distance']
        total_units = gedung['total_units']
        
        text_lines.append(
            f"{idx}. *{nama}*\n"
            f"   📍 {alamat}\n"
            f"   📏 Jarak: *{distance:.0f}m* | {total_units} unit"
        )
        
        if idx < len(results[:10]):
            text_lines.append("━━━━━━━━━━━━━━━━")
        
        button_text = f"{idx}. {nama} ({distance:.0f}m)"
        keyboard.append([InlineKeyboardButton(
            button_text,
            callback_data=f"gedung_{gedung['uuid']}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔄 Pencarian Baru", callback_data="search_again")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    caption = "\n".join(text_lines)
    
    try:
        # Jika message adalah photo, delete dulu
        await query.delete_message()
        await query.message.reply_text(
            caption,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    except:
        # Fallback
        await query.edit_message_text(
            caption,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
