from dataclasses import dataclass

@dataclass
class PageNavigationLink:
    title: str
    url_path_after_course_path: str
    course_id: str

    nested_links: list
