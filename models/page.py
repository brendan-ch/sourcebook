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

    created_by_user_id: Optional[int] = None

    page_id: Optional[int] = None

    def __post_init__(self):
        # TODO add URL validation
        # Attempt to auto-convert, and throws an obvious error if it fails
        if not isinstance(self.page_visibility_setting, VisibilitySetting):
            self.page_visibility_setting = VisibilitySetting(int(self.page_visibility_setting))

        if not isinstance(self.course_id, int):
            self.course_id = int(self.course_id)

        if self.created_by_user_id and not isinstance(self.created_by_user_id, int):
            self.created_by_user_id = int(self.created_by_user_id)

        if self.page_id and not isinstance(self.page_id, int):
            self.page_id = int(self.page_id)
