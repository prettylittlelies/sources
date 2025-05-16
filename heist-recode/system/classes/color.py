from typing import Optional
from system.classes.db import Database

class ColorManager:
    def __init__(self, db: Database):
        self.db = db
    
    async def get(self, user_id: int) -> int:
        """Get the embed color for a user"""
        return await self.db.get_embed_color(user_id)
    
    async def set(self, user_id: int, color: int) -> None:
        """Set the embed color for a user"""
        await self.db.set_embed_color(user_id, color)
    
    async def resolve(self, user_id: Optional[int], color: Optional[int] = None) -> int:
        """
        Resolve the final color to use.
        If color is provided, use that. Otherwise use the user's color.
        If no user_id, use default color.
        """
        if color is not None:
            return color
        if user_id is not None:
            return await self.get(user_id)
        return 0xd3d6f1