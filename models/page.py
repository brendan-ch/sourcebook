from dataclasses import dataclass
from enum import Enum
from typing import Optional


class VisibilitySetting(Enum):
    HIDDEN = 0
    UNLISTED = 1
    LISTED = 2


@dataclass
class Page:
    url_path: str
    page_title: str
    page_content: str

    page_visibility_setting: VisibilitySetting

    created_by_user_id: Optional[int]

    page_id: Optional[int]
    course_id: Optional[int]
