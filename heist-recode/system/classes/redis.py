from redis import asyncio as aioredis
import asyncio
from typing import Optional, Dict, Any, List, Tuple
from .logger import Logger

class RedisManager:
    def __init__(self):
        self.redis = None
        self._prefix = "heistv2:"
        self._pool_size = 1000
        self._connection_pool = None
        self._lock = asyncio.Lock()
        self._is_ready = False
        self.logger = Logger()
        
    async def initialize(self):
        try:
            self._connection_pool = aioredis.ConnectionPool.from_url(
                "redis://localhost:6379",
                max_connections=self._pool_size,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=5.0,
                socket_connect_timeout=5.0,
                health_check_interval=30,
                retry_on_timeout=True
            )
            self.redis = aioredis.Redis(
                connection_pool=self._connection_pool,
                socket_keepalive=True
            )
            await self.redis.ping()
            self._is_ready = True
            self.logger.info("[REDIS] Connection established successfully")
        except Exception as e:
            self._is_ready = False
            self.logger.error(f"[REDIS] Connection failed: {e}")
            raise

    async def close(self):
        if self._connection_pool:
            await self._connection_pool.disconnect()
            
    def key(self, name: str) -> str:
        return f"{self._prefix}{name}"

    async def handle_afk(self, user_ids: List[int], action: str = "get", data: Optional[Dict[int, Tuple[int, Optional[str]]]] = None) -> Dict[int, Dict[str, Any]]:
        if not self._is_ready:
            await self.initialize()
            
        async with self._lock:
            pipe = self.redis.pipeline(transaction=True)
            afk_key = self.key("afk")

            if action == "get":
                for uid in user_ids:
                    pipe.hget(afk_key, str(uid))
                results = await pipe.execute()
                processed = {}
                for uid, result in zip(user_ids, results):
                    if result:
                        timestamp, *reason_parts = result.split(":", 1)
                        processed[uid] = {
                            "timestamp": int(timestamp),
                            "reason": reason_parts[0] if reason_parts else None
                        }
                return processed

            elif action == "set":
                if not data:
                    return {}
                for uid in user_ids:
                    if uid in data:
                        timestamp, reason = data[uid]
                        pipe.hset(
                            afk_key,
                            str(uid),
                            f"{timestamp}:{reason if reason else ''}"
                        )
                await pipe.execute()
                return {}

            elif action == "remove":
                pipe.hdel(afk_key, *[str(uid) for uid in user_ids])
                await pipe.execute()
                return {}

            return {}