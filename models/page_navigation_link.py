from dataclasses import dataclass
from typing import Optional


@dataclass
class PageNavigationLink:
    page_title: str
    url_path_after_course_path: str
    course_id: str

    nested_links: Optional[list[any]] = None
