from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(kw_only=True)
class CourseTerm:
    title: str
    position_from_top: int

    course_term_id: Optional[int] = None
