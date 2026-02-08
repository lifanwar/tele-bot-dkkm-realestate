# utils/redis_manager.py
import redis.asyncio as redis
import json
import logging
from typing import Optional
from telegram.ext import Application

logger = logging.getLogger(__name__)


class RedisCache:
    """Simple Redis cache - Support URL atau host/port"""
    
    def __init__(self, redis_url: str = None, host: str = None, port: int = None, ttl=3600):
        self.redis_url = redis_url
        self.host = host
        self.port = port
        self.ttl = ttl
        self._client = None
        self._connected = False
    
    async def connect(self):
        """Connect ke Redis - auto detect URL atau host/port"""
        if not self._client:
            if self.redis_url:
                self._client = redis.from_url(
                    self.redis_url,
                    decode_responses=True
                )
                logger.info(f"📡 Connecting to Redis via URL...")
            elif self.host and self.port:
                self._client = redis.Redis(
                    host=self.host,
                    port=self.port,
                    decode_responses=True
                )
                logger.info(f"📡 Connecting to Redis at {self.host}:{self.port}...")
            else:
                raise ValueError("Redis config not set. Provide redis_url OR host+port")
            
            # TEST KONEKSI REAL
            try:
                await self._client.ping()
                self._connected = True
                logger.info("✅ Redis connection verified")
            except Exception as e:
                logger.error(f"❌ Redis PING failed: {e}")
                self._connected = False
                self._client = None
                raise
    
    async def close(self):
        """Close connection"""
        if self._client:
            try:
                await self._client.close()
                self._connected = False
                logger.info("🔌 Redis closed")
            except Exception as e:
                logger.error(f"Error closing Redis: {e}")
    
    # === GEDUNG ===
    
    async def save_gedung(self, uuid: str, data: dict):
        """Simpan gedung ke cache - graceful fail"""
        if not self._connected:
            return False
        
        try:
            key = f"gedung:{uuid}"
            value = json.dumps(data, ensure_ascii=False)
            await self._client.setex(key, self.ttl, value)
            logger.info(f"✅ Cached gedung: {uuid}")
            return True
        except Exception as e:
            logger.error(f"❌ Error save gedung {uuid}: {e}")
            self._connected = False
            return False
    
    async def get_gedung(self, uuid: str) -> Optional[dict]:
        """Ambil gedung dari cache - graceful fail"""
        if not self._connected:
            return None
        
        try:
            key = f"gedung:{uuid}"
            data = await self._client.get(key)
            if data:
                logger.info(f"🎯 Cache HIT: gedung {uuid}")
                return json.loads(data)
            logger.info(f"❌ Cache MISS: gedung {uuid}")
            return None
        except Exception as e:
            logger.error(f"❌ Error get gedung {uuid}: {e}")
            self._connected = False
            return None
    
    # === UNIT ===
    
    async def save_unit(self, uuid: str, data: dict):
        """Simpan unit ke cache - graceful fail"""
        if not self._connected:
            return False
        
        try:
            key = f"unit:{uuid}"
            value = json.dumps(data, ensure_ascii=False)
            await self._client.setex(key, self.ttl, value)
            logger.info(f"✅ Cached unit: {uuid}")
            return True
        except Exception as e:
            logger.error(f"❌ Error save unit {uuid}: {e}")
            self._connected = False
            return False
    
    async def get_unit(self, uuid: str) -> Optional[dict]:
        """Ambil unit dari cache - graceful fail"""
        if not self._connected:
            return None
        
        try:
            key = f"unit:{uuid}"
            data = await self._client.get(key)
            if data:
                logger.info(f"🎯 Cache HIT: unit {uuid}")
                return json.loads(data)
            logger.info(f"❌ Cache MISS: unit {uuid}")
            return None
        except Exception as e:
            logger.error(f"❌ Error get unit {uuid}: {e}")
            self._connected = False
            return None


# Global cache instance
cache = RedisCache()


# === LIFECYCLE MANAGER ===

class RedisLifecycle:
    """Lifecycle manager untuk Redis - dipakai di main.py"""
    
    @staticmethod
    async def post_init(app: Application):
        """Dipanggil setelah bot initialize - setup Redis"""
        from config import REDIS_URL, REDIS_HOST, REDIS_PORT, CACHE_TTL
        
        logger.info("🔧 Initializing Redis cache...")
        
        cache.redis_url = REDIS_URL
        cache.host = REDIS_HOST
        cache.port = REDIS_PORT
        cache.ttl = CACHE_TTL
        
        try:
            await cache.connect()
            logger.info("✅ Redis cache ready")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            logger.warning("⚠️ Bot will run without cache - All requests will use API")
    
    @staticmethod
    async def post_shutdown(app: Application):
        """Dipanggil sebelum bot shutdown - cleanup Redis"""
        try:
            await cache.close()
        except Exception as e:
            logger.error(f"Error closing Redis: {e}")
