from dataclasses import dataclass


@dataclass
class Section:
    section_name: str
    course_id: str
    section_id: str
    students: list[str]
