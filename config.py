"""Configuration file"""
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
API_BASE = os.getenv('API_BASE_URL')

# API Configuration
API_BASE_URL = f'https://{API_BASE}/api'
API_KEY = os.getenv('APIKEY_IMARAH_BLACKLIST')

# Radius presets
RADIUS_OPTIONS = [5, 25, 50, 100, 200, 500, 1000]
DEFAULT_RADIUS = 500