from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Union
import aiohttp
import asyncio
from cachetools import TTLCache
from io import BytesIO
from aiohttp import FormData
import os

@dataclass
class TikTokVideo:
    title: str
    author_id: str
    author_username: str
    author_nickname: str
    author_pfp: str
    video_url: str
    likes: int
    comments: int
    shares: int
    play_count: int = 0
    images: List[str] = None
    audio_url: str = None

class TikTok:
    BASE_URL = "https://tikwm.com"
    API_URL = f"{BASE_URL}/api"

    def __init__(self, bot):
        self.bot = bot
        self._session: Optional[aiohttp.ClientSession] = None
        self.video_cache = TTLCache(maxsize=100, ttl=300)
        self.download_semaphore = asyncio.Semaphore(15)
        self.request_semaphore = asyncio.Semaphore(10)

    async def _get_session(self) -> aiohttp.ClientSession:
        """Ensure a single aiohttp session is used."""
        if not self._session or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10),
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "application/json",
                    "Origin": self.BASE_URL,
                    "Referer": self.BASE_URL
                }
            )
        return self._session

    async def close(self):
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()

    @staticmethod
    def _format_counts(num: Union[int, str]) -> str:
        """Format large numbers into human-readable strings."""
        if isinstance(num, str):
            try:
                num = int(num.replace(',', ''))
            except ValueError:
                return num

        if num >= 1_000_000:
            return f"{num / 1_000_000:.1f}M"
        if num >= 1_000:
            return f"{num / 1_000:.1f}K"
        return str(num)

    async def get_trending_videos(self, region: str = "US", count: int = 12) -> List[TikTokVideo]:
        """Fetch trending TikTok videos with improved concurrency."""

        videos = []
        chunk_size = 30
        chunks_needed = (count + chunk_size - 1) // chunk_size
        session = await self._get_session()

        async def fetch_chunk(offset: int) -> List[TikTokVideo]:
            async with self.request_semaphore:
                try:
                    async with session.post(
                        f"{self.API_URL}/feed/list",
                        data={
                            "region": region,
                            "count": chunk_size,
                            "cursor": offset,
                            "web": 1,
                            "hd": 1
                        },
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        if response.status != 200:
                            return []

                        data = await response.json()
                        if data.get("code") != 0:
                            return []

                        return [
                            TikTokVideo(
                                title=video.get("title", ""),
                                likes=video.get("digg_count", 0),
                                comments=video.get("comment_count", 0),
                                shares=video.get("share_count", 0),
                                play_count=video.get("play_count", 0),
                                author_id=video["author"]["id"],
                                author_username=video["author"]["unique_id"],
                                author_pfp=f"{self.BASE_URL}{video['author']['avatar']}" if video['author'].get('avatar') else None,
                                author_nickname=video["author"]["nickname"],
                                images=[f"{self.BASE_URL}{img}" if not img.startswith(('http://', 'https://')) else img 
                                       for img in video.get("images", [])] if video.get("images") else None,
                                audio_url=f"{self.BASE_URL}{video['music']}" if video.get('music') and not video['music'].startswith(('http://', 'https://')) else video.get('music'),
                                video_url=f"{self.BASE_URL}{video['play']}" if not video['play'].startswith(('http://', 'https://')) else video['play']
                            )
                            for video in data.get("data", [])
                        ]
                except asyncio.TimeoutError:
                    return []
                except Exception:
                    return []

        chunk_tasks = [fetch_chunk(i * chunk_size) for i in range(chunks_needed)]
        all_results = await asyncio.gather(*chunk_tasks, return_exceptions=True)
        
        for result in all_results:
            if isinstance(result, list):
                videos.extend(result)
                if len(videos) >= count:
                    videos = videos[:count]
                    break


        return videos[:count]

    async def download_media_bulk(self, urls: List[str]) -> List[BytesIO]:
        """Download multiple media files with improved concurrency."""
        if not urls:
            return []

        async def download_single(url: str) -> Optional[BytesIO]:
            async with self.download_semaphore:
                try:
                    async with (await self._get_session()).get(
                        url, 
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        if response.status != 200:
                            return None
                        buffer = BytesIO(await response.read())
                        buffer.seek(0)
                        return buffer
                except (asyncio.TimeoutError, Exception):
                    return None

        batch_size = 5
        results = []
        
        for i in range(0, len(urls), batch_size):
            batch = urls[i:i + batch_size]
            batch_tasks = [download_single(url) for url in batch]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            results.extend([r for r in batch_results if isinstance(r, BytesIO)])

        return results

    async def get_video_data(self, url: str) -> TikTokVideo:
        """Fetch TikTok video data asynchronously."""
        if not url or not isinstance(url, str) or not url.strip().startswith(('http://', 'https://')):
            raise ValueError("A valid TikTok URL is required")

        cache_key = f"video_{url.strip()}"
        if cache_key in self.video_cache:
            return self.video_cache[cache_key]

        async with self.request_semaphore:
            session = await self._get_session()
            async with session.post(
                self.API_URL,
                params={"url": url.strip()}
            ) as response:
                if response.status != 200:
                    raise ValueError(f"Failed to fetch video data: {response.status}")

                data = await response.json()
                if data.get("code") != 0:
                    raise ValueError(data.get("msg", "Failed to fetch video information"))

                video = data["data"]
                video_data = TikTokVideo(
                    title=video.get("title", ""),
                    likes=video.get("digg_count", 0),
                    comments=video.get("comment_count", 0),
                    shares=video.get("share_count", 0),
                    play_count=video.get("play_count", 0),
                    author_id=video["author"]["id"],
                    audio_url=f"{self.BASE_URL}{video['music']}" if video.get('music') and not video['music'].startswith(('http://', 'https://')) else video.get('music'),
                    author_username=video["author"]["unique_id"],
                    author_pfp=f"{self.BASE_URL}{video['author']['avatar']}" if video['author'].get('avatar') and not video['author']['avatar'].startswith(('http://', 'https://')) else video['author'].get('avatar'),
                    author_nickname=video["author"]["nickname"],
                    images=[f"{self.BASE_URL}{img}" if not img.startswith(('http://', 'https://')) else img 
                           for img in video.get("images", [])] if video.get("images") else None,
                    video_url=f"{self.BASE_URL}{video['play']}" if not video['play'].startswith(('http://', 'https://')) else video['play']
                )
                self.video_cache[cache_key] = video_data
                return video_data

    async def upload_to_catbox(self, buffer: BytesIO) -> Optional[str]:
        """Upload to catbox.moe with improved error handling and timeout."""
        try:
            buffer.seek(0, os.SEEK_END)
            size = buffer.tell()
            buffer.seek(0)
            
            if size <= 8 * 1024 * 1024:
                return None

            form = FormData()
            form.add_field('reqtype', 'fileupload')
            form.add_field('fileToUpload', buffer, 
                         filename='video.mp4',
                         content_type='video/mp4')

            async with self.download_semaphore:
                async with self._get_session() as session:
                    async with session.post(
                        'https://catbox.moe/user/api.php',
                        data=form,
                        headers={'User-Agent': 'TikTok-Discord-Bot'},
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        if response.status == 200:
                            result = await response.text()
                            if result.startswith('https://files.catbox.moe/'):
                                return result
            return None
        except Exception:
            return None

    async def download_video(self, video_url: str) -> Union[BytesIO, str]:
        """Download a TikTok video asynchronously. Returns either BytesIO or catbox.moe URL."""
        if not video_url.startswith(('http://', 'https://')):
            video_url = f"{self.BASE_URL}{video_url}"
            
        session = await self._get_session()
        async with session.get(video_url) as response:
            if response.status != 200:
                raise ValueError(f"Failed to download video: {response.status}")
                
            buffer = BytesIO(await response.read())
            buffer.seek(0)
            
            catbox_url = await self.upload_to_catbox(buffer)
            if catbox_url:
                return catbox_url
                
            buffer.seek(0)
            return buffer

    async def download_media(self, path: str) -> BytesIO:
        """Download media from a given path asynchronously."""
        if not path.startswith(('http://', 'https://')):
            path = f"{self.BASE_URL}{path}"
            
        session = await self._get_session()
        async with session.get(path) as response:
            if response.status != 200:
                raise ValueError(f"Failed to download media: {response.status}")
            buffer = BytesIO(await response.read())
            buffer.seek(0)
            return buffer

    def format_stats(self, data: Dict[str, Any]) -> str:
        """Format TikTok video statistics into a readable string."""
        return (
            f"❤️ {self._format_counts(data['digg_count'])}  "
            f"💬 {self._format_counts(data['comment_count'])}  "
            f"🔗 {self._format_counts(data['share_count'])}  "
            f"👀 {self._format_counts(data['play_count'])}"
        )