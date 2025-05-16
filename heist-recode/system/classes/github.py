import aiohttp
import discord
from discord import Webhook, Embed
from data.config import CONFIG
from typing import Optional
from aiohttp import web

class GitHubWebhook:
    def __init__(self, bot):
        self.bot = bot
        self.webhook_url = CONFIG['github']['webhook']
        self.webhook_secret = CONFIG['github']['secret'] 
        
        self.commits_channel = CONFIG['channels']['commits']
        self._webhook: Optional[Webhook] = None
        self._session: Optional[aiohttp.ClientSession] = None
        self._app = web.Application()
        self._app.router.add_post('/github/webhook', self._handle_webhook)
        self._runner = None
        
    async def initialize(self) -> None:
        """Initialize webhook session and start webhook server"""
        self._session = aiohttp.ClientSession()
        self._webhook = Webhook.from_url(
            self.webhook_url,
            session=self._session
        )
        
        self._runner = web.AppRunner(self._app)
        await self._runner.setup()
        site = web.TCPSite(self._runner, '0.0.0.0', 56384)
        await site.start()
        self.bot.logger.info("GitHub webhook server started")

    async def close(self) -> None:
        """Cleanup webhook session and server"""
        if self._session:
            await self._session.close()
        if self._runner:
            await self._runner.cleanup()

    async def _handle_webhook(self, request: web.Request) -> web.Response:
        """Handle incoming GitHub webhook requests"""
        signature = request.headers.get('X-Hub-Signature-256')
        if not self._verify_signature(signature, await request.read()):
            return web.Response(status=401)
        
        data = await request.json()
        event_type = request.headers.get('X-GitHub-Event')
        
        if event_type == 'push':
            await self.handle_push(data)
        
        return web.Response(status=200)

    def _verify_signature(self, signature: str, payload: bytes) -> bool:
        """Verify GitHub webhook signature"""
        import hmac
        import hashlib
        
        if not signature or not signature.startswith('sha256='):
            return False
            
        expected = signature[7:]
        actual = hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected, actual)

    async def handle_push(self, data: dict) -> None:
        """Handle GitHub push event webhook data"""
        try:
            commits = data.get('commits', [])
            if not commits:
                return
                
            repo_info = data.get('repository', {})
            repo_name = repo_info.get('full_name', 'unknown/repo')
            repo_url = repo_info.get('html_url', '')

            for commit in commits:
                commit_msg = commit.get('message', 'No message provided')
                commit_id = commit.get('id', '')[:7]
                author = commit.get('author', {})
                author_name = author.get('username') or author.get('name', 'Unknown')
                author_avatar = "https://github.com/ghost.png"

                if author_name != "Unknown":
                    github_api_url = f"https://api.github.com/users/{author_name}"
                    async with self._session.get(github_api_url) as resp:
                        if resp.status == 200:
                            user_data = await resp.json()
                            author_avatar = user_data.get('avatar_url', author_avatar)
                
                modified = commit.get('modified', [])
                added = commit.get('added', [])
                removed = commit.get('removed', [])
                
                files_text = []
                if added:
                    files_text.extend(f"! {f}" for f in added)
                if modified:  
                    files_text.extend(f"! {f}" for f in modified)
                if removed:
                    files_text.extend(f"! {f}" for f in removed)
                    
                modified_text = "\n".join(files_text) if files_text else "No files modified"
                
                embed = Embed(
                    color=0x2B2D31,
                    title=f"{repo_name}",
                    description=(
                        f">>> There has been 1 commit to [`{repo_name}`]({repo_url}) **```diff\n{modified_text}```**"
                    ) 
                )
                
                #embed.set_author(
                #    name=f"@{author_name}",
                #    url=f"https://github.com/{author_name}",
                #    icon_url=author_avatar
                #)
                embed.set_footer(
                    text=f"{commit_id} - {commit_msg}",
                    icon_url="https://imgs.search.brave.com/1W9nfD5z8XJIbkkoCNiJRgkIOrGHj_NuZ7wN5rjKWJ0/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9zdGF0/aWMtMDAuaWNvbmR1/Y2suY29tL2Fzc2V0/cy4wMC9naXRodWIt/aWNvbi0yNTZ4MjQ5/LTdpbWdqNTRtLnBu/Zw"
                )
                await self._webhook.send(embed=embed)
                
        except Exception as e:
            self.bot.logger.error(f"Error handling GitHub webhook: {e}")