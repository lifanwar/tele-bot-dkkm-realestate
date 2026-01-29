"""Handle location sharing and nearby search"""
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import API_BASE_URL, API_KEY, RADIUS_OPTIONS


async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle when user shares location"""
    location = update.message.location
    
    # Simpan location di context
    context.user_data['lat'] = location.latitude
    context.user_data['long'] = location.longitude
    
    # Tampilkan pilihan radius dengan layout yang lebih baik
    keyboard = []
    
    # 3 kolom untuk radius kecil-menengah
    keyboard.append([
        InlineKeyboardButton("📏 5m", callback_data='radius_5'),
        InlineKeyboardButton("📏 25m", callback_data='radius_25'),
        InlineKeyboardButton("📏 50m", callback_data='radius_50'),
    ])
    
    # 2 kolom untuk radius menengah-besar
    keyboard.append([
        InlineKeyboardButton("📏 100m", callback_data='radius_100'),
        InlineKeyboardButton("📏 200m", callback_data='radius_200'),
    ])
    
    keyboard.append([
        InlineKeyboardButton("📏 500m", callback_data='radius_500'),
        InlineKeyboardButton("📏 1000m", callback_data='radius_1000'),
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Kirim pesan dengan format yang lebih menarik
    await update.message.reply_text(
        f"📍 *Lokasi Diterima*\n\n"
        f"📊 Koordinat:\n"
        f"• Latitude: `{location.latitude:.6f}`\n"
        f"• Longitude: `{location.longitude:.6f}`\n\n"
        f"🔍 Pilih radius pencarian:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def search_nearby(update: Update, context: ContextTypes.DEFAULT_TYPE, radius: int):
    """Search nearby buildings"""
    query = update.callback_query
    await query.answer("🔍 Mencari gedung terdekat...")
    
    lat = context.user_data.get('lat')
    long = context.user_data.get('long')
    
    if not lat or not long:
        await query.edit_message_text("❌ Lokasi tidak ditemukan. Silakan share lokasi lagi.")
        return
    
    # Call API
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{API_BASE_URL}/gedung/nearby"
            headers = {
                'accept': 'application/json',
                'X-API-Key': API_KEY,
                'Content-Type': 'application/json'
            }
            payload = {
                'lat': lat,
                'long': long,
                'radius': radius
            }
            
            async with session.post(url, json=payload, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    await show_nearby_results(query, data, context)
                else:
                    error_text = await resp.text()
                    await query.edit_message_text(
                        f"❌ *Error {resp.status}*\n\n"
                        f"```\n{error_text[:200]}\n```",
                        parse_mode='Markdown'
                    )
    
    except Exception as e:
        await query.edit_message_text(
            f"❌ *Terjadi Kesalahan*\n\n"
            f"Detail: `{str(e)}`",
            parse_mode='Markdown'
        )


async def show_nearby_results(query, data, context):
    """Display nearby buildings results with beautiful format"""
    
    if not data.get('success'):
        await query.edit_message_text("❌ Pencarian gagal. Coba lagi.")
        return
    
    results = data.get('results', [])
    count = data.get('count', 0)
    radius = data.get('radius', 0)
    
    if count == 0:
        # Format pesan tidak ada hasil
        keyboard = [[InlineKeyboardButton("🔄 Coba Radius Lain", callback_data="search_again")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"🔍 *Pencarian Selesai*\n\n"
            f"📏 Radius: *{radius}m*\n"
            f"📊 Hasil: *Tidak ada gedung ditemukan*\n\n"
            f"💡 Coba perbesar radius atau share lokasi berbeda.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return
    
    # Simpan results di context
    context.user_data['search_results'] = results
    context.user_data['search_radius'] = radius
    
    # Format text hasil (seperti WhatsApp tapi lebih rapi)
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
        
        # Format text list
        text_lines.append(
            f"{idx}. *{nama}*\n"
            f"   📍 {alamat}\n"
            f"   📏 Jarak: *{distance:.0f}m* | {total_units} unit"
        )
        
        # Tambahkan separator kecuali item terakhir
        if idx < len(results[:10]):
            text_lines.append("━━━━━━━━━━━━━━━━")
        
        # Button untuk gedung
        button_text = f"{idx}. {nama} ({distance:.0f}m)"
        keyboard.append([InlineKeyboardButton(
            button_text,
            callback_data=f"gedung_{gedung['uuid']}"
        )])
    
    # Navigation buttons
    keyboard.append([InlineKeyboardButton("🔄 Pencarian Baru", callback_data="search_again")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Gabungkan text
    caption = "\n".join(text_lines)
    
    await query.edit_message_text(
        caption,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def handle_search_again(query):
    """Handle search again button"""
    await query.answer()
    
    keyboard = []
    keyboard.append([
        InlineKeyboardButton("📏 5m", callback_data='radius_5'),
        InlineKeyboardButton("📏 25m", callback_data='radius_25'),
        InlineKeyboardButton("📏 50m", callback_data='radius_50'),
    ])
    keyboard.append([
        InlineKeyboardButton("📏 100m", callback_data='radius_100'),
        InlineKeyboardButton("📏 200m", callback_data='radius_200'),
    ])
    keyboard.append([
        InlineKeyboardButton("📏 500m", callback_data='radius_500'),
        InlineKeyboardButton("📏 1000m", callback_data='radius_1000'),
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🔍 *Pencarian Baru*\n\n"
        f"Pilih radius pencarian:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
