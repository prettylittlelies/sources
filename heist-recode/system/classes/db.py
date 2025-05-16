import asyncpg
import asyncio
from typing import Optional, Dict, Any, List, Tuple
from data.config import CONFIG
from system.classes.redis import RedisManager
from .logger import Logger

class Database:
    def __init__(self):
        self.pool = None
        self._redis = None
        self._redis_ready = asyncio.Event()
        self.logger = Logger()

    async def initialize(self):
        self.logger.debug("Initializing database connection...")
        try:
            self.pool = await asyncpg.create_pool(
                dsn="postgresql://postgres:cosmingyatrizz44@localhost/heist",
                min_size=5,
                max_size=20
            )
            self._redis = RedisManager()
            await self._redis.initialize()
            self._redis_ready.set()
            self.logger.info("Database and Redis initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise

    async def register_user(self, discord_id: int, username: str, displayname: str) -> None:
        self.logger.debug(f"Registering user {discord_id} ({username})")
        await self._redis_ready.wait()
        redis_key = self._redis.key(f"user:{discord_id}:exists")
        user_exists_in_cache = await self._redis.redis.get(redis_key)

        if not user_exists_in_cache:
            async with self.pool.acquire() as conn:
                user_exists = await conn.fetchval(
                    "SELECT 1 FROM user_data WHERE user_id = $1",
                    str(discord_id)
                )
                if not user_exists:
                    self.logger.info(f"Creating new user record for {discord_id}")
                    await conn.execute("""
                        INSERT INTO user_data (user_id, username, displayname)
                        VALUES ($1, $2, $3)
                        ON CONFLICT (user_id) DO NOTHING
                    """, str(discord_id), username, displayname)
                    limited_key = self._redis.key(f"user:{discord_id}:limited")
                    await self._redis.redis.setex(limited_key, 7 * 24 * 60 * 60, '')
                    untrusted_key = self._redis.key(f"user:{discord_id}:untrusted")
                    await self._redis.redis.setex(untrusted_key, 60 * 24 * 60 * 60, '')
                    await self._redis.redis.setex(redis_key, 600, '1')
                    self.logger.debug(f"User {discord_id} registered and cached")

    async def check_blacklisted(self, user_id: int) -> bool:
        self.logger.debug(f"Checking blacklist status for user {user_id}")
        await self._redis_ready.wait()
        redis_key = self._redis.key(f"blacklist:{user_id}")
        cached = await self._redis.redis.get(redis_key)
        if cached is not None:
            self.logger.debug(f"Blacklist cache hit for {user_id}: {cached}")
            return cached == "True"
        
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT 1 FROM blacklisted WHERE user_id = $1",
                str(user_id))
            is_blacklisted = bool(result)
            await self._redis.redis.setex(redis_key, 300, str(is_blacklisted))
            self.logger.debug(f"Blacklist DB query for {user_id}: {is_blacklisted}")
            return is_blacklisted

    async def check_donor(self, user_id: int) -> bool:
        self.logger.debug(f"Checking donor status for user {user_id}")
        await self._redis_ready.wait()
        redis_key = self._redis.key(f"donor:{user_id}")
        cached = await self._redis.redis.get(redis_key)
        if cached is not None:
            self.logger.debug(f"Donor cache hit for {user_id}: {cached}")
            return cached == "True"
        
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT 1 FROM donors WHERE user_id = $1",
                str(user_id))
            is_donor = bool(result)
            await self._redis.redis.setex(redis_key, 300, str(is_donor))
            self.logger.debug(f"Donor DB query for {user_id}: {is_donor}")
            return is_donor

    async def check_owner(self, user_id: int) -> bool:
        self.logger.debug(f"Checking owner status for user {user_id}")
        await self._redis_ready.wait()
        self.logger.debug(f"Checking Redis for owner status of {user_id}")
        redis_key = self._redis.key(f"owner:{user_id}")
        cached = await self._redis.redis.get(redis_key)
        self.logger.debug(f"Owner cache check for {user_id}: {cached}")
        if cached is not None:
            self.logger.debug(f"Owner cache hit for {user_id}: {cached}")
            return cached == "True"
        
        self.logger.debug(f"Owner cache miss for {user_id}")
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT 1 FROM owners WHERE user_id = $1",
                str(user_id))
            is_owner = bool(result)
            self.logger.debug(f"Owner DB query result for {user_id}: {is_owner}")
            await self._redis.redis.setex(redis_key, 300, str(is_owner))
            self.logger.debug(f"Owner DB query for {user_id}: {is_owner}")
            return is_owner

    async def check_booster(self, user_id: int) -> bool:
        self.logger.debug(f"Checking booster status for user {user_id}")
        await self._redis_ready.wait()
        redis_key = self._redis.key(f"booster:{user_id}")
        cached = await self._redis.redis.get(redis_key)
        if cached is not None:
            self.logger.debug(f"Booster cache hit for {user_id}: {cached}")
            return cached == "True"
        
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT booster FROM user_data WHERE user_id = $1",
                str(user_id))
            is_booster = bool(result)
            await self._redis.redis.setex(redis_key, 300, str(is_booster))
            self.logger.debug(f"Booster DB query for {user_id}: {is_booster}")
            return is_booster

    async def check_famous(self, user_id: int) -> bool:
        self.logger.debug(f"Checking famous status for user {user_id}")
        await self._redis_ready.wait()
        redis_key = self._redis.key(f"famous:{user_id}")
        cached = await self._redis.redis.get(redis_key)
        if cached is not None:
            self.logger.debug(f"Famous cache hit for {user_id}: {cached}")
            return cached == "True"
        
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT fame FROM user_data WHERE user_id = $1",
                str(user_id))
            is_famous = bool(result)
            await self._redis.redis.setex(redis_key, 300, str(is_famous))
            self.logger.debug(f"Famous DB query for {user_id}: {is_famous}")
            return is_famous
        
    async def get_emoji(self, name: str) -> Optional[str]:
        self.logger.debug(f"Fetching emoji: {name}")
        async with self.pool.acquire() as conn:
            return await conn.fetchval(
                "SELECT dname FROM emojis WHERE name = $1",
                name)
        
    async def fetchrow(self, query: str, *params) -> Optional[Dict[str, Any]]:
        self.logger.debug(f"Executing fetchrow: {query[:50]}...")
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *params)

    async def fetchval(self, query: str, *params) -> Optional[Any]:
        self.logger.debug(f"Executing fetchval: {query[:50]}...")
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *params)

    async def set_embed_color(self, user_id: int, color: int) -> None:
        self.logger.debug(f"Setting embed color for user {user_id}: {color}")
        await self._redis_ready.wait()
        if isinstance(color, str):
            color = int(color, 16)
        if not (0 <= color <= 0xFFFFFF):
            raise ValueError("Color must be between 0 and 0xFFFFFF")
        redis_key = self._redis.key(f"embed_color:{user_id}")
        await self._redis.redis.setex(redis_key, 3600, str(color))
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO settings (user_id, embed_color)
                VALUES ($1, $2)
                ON CONFLICT (user_id) DO UPDATE SET embed_color = $2
            """, str(user_id), color)

    async def get_embed_color(self, user_id: int) -> int:
        self.logger.debug(f"Getting embed color for user {user_id}")
        await self._redis_ready.wait()
        redis_key = self._redis.key(f"embed_color:{user_id}")
        cached_color = await self._redis.redis.get(redis_key)
        if cached_color is not None:
            self.logger.debug(f"Embed color cache hit for {user_id}: {cached_color}")
            return int(cached_color)
        
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT embed_color FROM settings WHERE user_id = $1",
                str(user_id))
            if result is None:
                default_color = 0xd3d6f1
                await self.set_embed_color(user_id, default_color)
                return default_color
            await self._redis.redis.setex(redis_key, 3600, str(result))
            self.logger.debug(f"Embed color DB query for {user_id}: {result}")
            return result