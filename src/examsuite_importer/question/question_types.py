from dataclasses import dataclass


@dataclass
class QuestionParserError:
    error: str