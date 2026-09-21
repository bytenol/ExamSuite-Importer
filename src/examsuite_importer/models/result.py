from dataclasses import dataclass, field

from .metadata import ExamMetadata
from .question import QuestionData


@dataclass(slots=True)
class ImportError:
    question_number: int | None
    message: str
    content: str = ""


@dataclass(slots=True)
class ImportResult:
    success: bool
    metadata: ExamMetadata
    questions: list[QuestionData] = field(default_factory=list)
    errors: list[ImportError] = field(default_factory=list)

    @property
    def passed(self) -> list[QuestionData]:
        failed_numbers = {
            error.question_number
            for error in self.errors
            if error.question_number is not None
        }

        return [
            question
            for question in self.questions
            if question.number not in failed_numbers
        ]