from dataclasses import dataclass, field
from enum import Enum


class QuestionType(str, Enum):
    THEORY = "theory"
    FILL_IN_BLANK = "fill_in_blank"
    SINGLE_CHOICE = "single_choice"


@dataclass(slots=True)
class QuestionChoice:
    label: str
    text: str


@dataclass(slots=True)
class QuestionData:
    number: int
    content: str
    type: QuestionType
    answer: str = ""
    mark: float = 1.0
    choices: list[QuestionChoice] = field(default_factory=list)