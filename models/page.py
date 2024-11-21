from dataclasses import dataclass
from enum import Enum
from typing import Optional


class VisibilitySetting(Enum):
    HIDDEN = 0
    UNLISTED = 1
    LISTED = 2


@dataclass
class Page:
    url_path_after_course_path: str
    course_id: int
    page_title: str
    page_content: str

    page_visibility_setting: VisibilitySetting

    created_by_user_id: Optional[int]

    page_id: Optional[int]
