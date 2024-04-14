from typing import Dict, List

import yaml
from pydantic import BaseModel


class Config(BaseModel):
    forwarding_chat: int
    admins_ids: List[int]
    subscription_price: int
    bot_link: str
    general_chats: Dict[str, str]
    additional_chats: Dict[str, str]
    folder_with_chats: str


with open("config.yaml") as cfg_file:
    data = yaml.safe_load(cfg_file)

cfg = Config(**data)
