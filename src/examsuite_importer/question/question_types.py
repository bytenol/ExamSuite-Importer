from dataclasses import dataclass, field
from enum import Enum


class QuestionVarities(Enum):
    SINGLE_CHOICE = 2
    FILL_IN_BLANK = 4
    THEORY = 6



@dataclass
class QuestionChoice:
    label: str 
    text: str


@dataclass
class QuestionData:
    type: QuestionVarities
    content: str
    answer: str
    mark: float
    choices: list[QuestionChoice] = field(default_factory=list)


@dataclass
class QuestionValidatorError:
    line: int 
    content: str 
    message: str 



@dataclass
class QuestionParserResult:
    success: bool 
    exception: str 
    errors: list[QuestionValidatorError] = field(default_factory=list)
    questions: list[QuestionData] = field(default_factory=list)
