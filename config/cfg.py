from typing import List

from pydantic import BaseModel


class Config(BaseModel):
    forwarding_chat: int
    admins_ids: List[int]
    subscription_price: int
    bot_link: str
