"""Get unit details"""
import aiohttp
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import API_BASE_URL, API_KEY
# Import logger
import logging
logger = logging.getLogger(__name__)

async def get_unit_detail(query, uuid: str, context):
    """Get unit detail by UUID"""
    await query.answer("📥 Memuat detail unit...")
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{API_BASE_URL}/unit/{uuid}"
            headers = {
                'accept': 'application/json',
                'X-API-Key': API_KEY
            }
            
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    await show_unit_detail(query, data, context)
                else:
                    await query.edit_message_text(
                        f"❌ *Error {resp.status}*\n\nGagal memuat data unit.",
                        parse_mode='Markdown'
                    )
    
    except Exception as e:
        await query.edit_message_text(
            f"❌ *Error*\n\n`{str(e)}`",
            parse_mode='Markdown'
        )


async def show_unit_detail(query, unit, context):
    """Display unit details with beautiful format"""
    
    gedung_nama = unit['gedung_nama']
    lantai = unit['lantai']
    unit_number = unit['unit_number']
    deskripsi = unit.get('deskripsi', 'N/A')
    listing_type = unit.get('listing_type', 'unknown')
    pemilik = unit.get('pemilik', 'N/A')
    agen = unit.get('agen', 'N/A')
    alasan_blacklist = unit.get('alasan_blacklist', '')
    images = unit.get('images', [])
    
    # Status
    if listing_type == 'blacklist':
        status_emoji = '🚫'
        status_text = 'BLACKLIST'
    elif listing_type == 'available':
        status_emoji = '✅'
        status_text = 'AVAILABLE'
    else:
        status_emoji = '📋'
        status_text = listing_type.upper()
    
    # Format text seperti WhatsApp
    text_lines = [
        f"🏠 *Unit Lt {lantai} ({unit_number})*\n",
        f"🏢 *{gedung_nama}*",
        f"📝 {deskripsi}"
    ]
    
    if alasan_blacklist:
        text_lines.append(f"🚫 *{alasan_blacklist}*")
    
    text_lines.append("")  # Empty line
    text_lines.append(f"👤 *Pemilik:* {pemilik}")
    text_lines.append(f"🏢 *Agen:* {agen}")
    text_lines.append("")
    text_lines.append(f"{status_emoji} *Status:* {status_text}")
    text_lines.append("")
    text_lines.append("━━━━━━━━━━━━━━━━")
    text_lines.append("_Terima kasih telah melihat detail unit_")
    
    keyboard = []

    # Navigation buttons kolom 1
    keyboard.append([
        InlineKeyboardButton("« Back", callback_data="back_gedung"),
        InlineKeyboardButton("« Back to Awal", callback_data="back_results"),
    ])
    # Navigation Buttons Kolom 2
    keyboard.append([
        InlineKeyboardButton("🔄 Pencarian Baru", callback_data="search_again")
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Gabungkan text
    caption = "\n".join(text_lines)
    
    # Kirim dengan gambar jika ada
    if images and len(images) > 0:
        primary_image = images[0]
        
        try:
            await query.delete_message()
            await query.message.reply_photo(
                photo=primary_image,
                caption=caption,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except:
            # Fallback
            try:
                await query.edit_message_text(
                    caption,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            except:
                await query.delete_message()
                await query.message.reply_text(
                    caption,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
    else:
        try:
            await query.edit_message_text(
                caption,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except:
            await query.delete_message()
            await query.message.reply_text(
                caption,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )


async def back_to_gedung(query, context):
    """Back to gedung detail - FIXED"""
    await query.answer()
    
    gedung = context.user_data.get('current_gedung')
    
    if not gedung:
        try:
            await query.edit_message_text(
                "❌ Data tidak ditemukan.\n\n"
                "Silakan lakukan pencarian baru."
            )
        except:
            # Jika gagal edit (pesan adalah foto), kirim message baru
            await query.message.reply_text(
                "Sesi telah berakhir.\n"
                "Silakan share lokasi Anda kembali untuk memulai pencarian.",
            )
        return
    
    # Import di dalam function untuk avoid circular import
    from flows.get_gedung import show_gedung_detail
    
    try:
        # Delete message dengan gambar, lalu buat ulang
        await query.delete_message()
        
        # Buat dummy query object untuk show_gedung_detail
        # Karena show_gedung_detail perlu query object
        class DummyQuery:
            def __init__(self, message):
                self.message = message
                
            async def answer(self):
                pass
                
            async def edit_message_text(self, text, **kwargs):
                await self.message.reply_text(text, **kwargs)
                
            async def edit_message_caption(self, caption, **kwargs):
                await self.message.reply_text(caption, **kwargs)
                
            async def delete_message(self):
                pass
        
        dummy_query = DummyQuery(query.message)
        await show_gedung_detail(dummy_query, gedung, context)
        
    except Exception as e:
        logger.error(f"Error back_to_gedung: {str(e)}", exc_info=True)
        # Fallback jika error
        await query.message.reply_text(
            "❌ Terjadi kesalahan.\n\n"
            "Silakan coba lagi atau lakukan pencarian baru."
        )

