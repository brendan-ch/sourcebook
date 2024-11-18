from dataclasses import dataclass


@dataclass
class User:
    user_id: str
    full_name: str
    email: str