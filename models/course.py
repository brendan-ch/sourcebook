from dataclasses import dataclass
from typing import Optional


@dataclass
class Course:
    title: str
    user_friendly_class_code: str

    # Example: /cpsc-408-f24
    starting_url_path: str

    course_term_id: Optional[id] = None
    course_id: Optional[int] = None