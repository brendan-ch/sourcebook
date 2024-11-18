from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    user_id: Optional[str]
    full_name: str
    email: str