from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    full_name: str
    email: str
    user_id: Optional[str] = None
