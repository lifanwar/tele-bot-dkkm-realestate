"""
Main bot application
"""
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)

from config import TELEGRAM_TOKEN
from utils.redis_manager import RedisLifecycle

# Import Apps
from flows.handle_location import (handle_location, search_nearby, handle_search_again)
from flows.get_gedung import (get_gedung_detail, back_to_results)
from flows.get_detail_unit import (get_unit_detail, back_to_gedung)

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    await update.message.reply_text(
        "👋 *Selamat datang di DKKM Bot!*\n\n"
        "🏢 Bot ini membantu Anda mencari gedung dan unit terdekat.\n\n"
        "📍 *Cara Menggunakan:*\n"
        "1. Klik icon 📎 (attachment)\n"
        "2. Pilih *Location*\n"
        "3. Kirim lokasi Anda saat ini\n"
        "4. Pilih radius pencarian\n"
        "5. Lihat hasil gedung terdekat\n\n"
        "💡 Ketik /help untuk bantuan lebih lanjut",
        parse_mode='Markdown'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    await update.message.reply_text(
        "❓ *Bantuan DKKM Bot*\n\n"
        "*Fitur Utama:*\n"
        "• 📍 Cari gedung terdekat berdasarkan lokasi\n"
        "• 🏢 Lihat detail gedung & unit\n"
        "• 🗺️ Lihat lokasi di Google Maps\n"
        "• 📊 Informasi lengkap tiap unit\n\n"
        "*Command:*\n"
        "/start - Mulai bot\n"
        "/help - Bantuan ini\n\n"
        "*Cara Pakai:*\n"
        "Share lokasi Anda → Bot akan mencari gedung terdekat!",
        parse_mode='Markdown'
    )


async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Route all callback queries"""
    query = update.callback_query
    data = query.data
    
    logger.info(f"Callback: {data} from user {query.from_user.id}")
    
    # Radius selection
    if data.startswith('radius_'):
        radius = int(data.replace('radius_', ''))
        await search_nearby(update, context, radius)
    
    # Gedung selection
    elif data.startswith('gedung_'):
        uuid = data.replace('gedung_', '')
        await get_gedung_detail(query, uuid, context)
    
    # Unit selection
    elif data.startswith('unit_'):
        uuid = data.replace('unit_', '')
        await get_unit_detail(query, uuid, context)
    
    # Navigation
    elif data == 'back_results':
        await back_to_results(query, context)
    
    elif data == 'back_gedung':
        await back_to_gedung(query, context)
    
    elif data == 'search_again':
        await handle_search_again(query, context)
    
    elif data == 'no_action':
        await query.answer("Tidak ada aksi")
    
    else:
        await query.answer("Aksi tidak dikenal")
        logger.warning(f"Unknown callback data: {data}")


def main():
    """Main function"""
    
    if not TELEGRAM_TOKEN:
        logger.error("❌ TELEGRAM_TOKEN not found in .env file!")
        return
    
    logger.info("🚀 Starting DKKM Bot...")
    
    # Create application
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Lifecycle hooks - pakai RedisLifecycle class
    app.post_init = RedisLifecycle.post_init
    app.post_shutdown = RedisLifecycle.post_shutdown
    
    # Handlers
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(CallbackQueryHandler(callback_router))
    
    logger.info("✅ DKKM Bot is running!")
    logger.info("   Send /start to begin")
    
    # Run bot
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
