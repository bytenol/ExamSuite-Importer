from dataclasses import dataclass



@dataclass(slots=True)
class ExamMetadata:
    subject: str = ""
    class_name: str = ""
    section: str = ""