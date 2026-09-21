from __future__ import annotations

import re

from examsuite_importer.models import (
    ImportError,
    QuestionChoice,
    QuestionData,
    QuestionType,
)


QUESTION_PATTERN = re.compile(
    r"^\s*question\s*$",
    re.IGNORECASE,
)

CHOICE_PATTERN = re.compile(
    r"^\s*\(([a-dA-D])\)\s*(.*)$"
)

ANSWER_PATTERN = re.compile(
    r"^\s*answer\s*(.*)$",
    re.IGNORECASE,
)

MARK_PATTERN = re.compile(
    r"^\s*mark\s*(.*)$",
    re.IGNORECASE,
)


class QuestionParser:
    """
    Builds a QuestionData object from the paragraphs belonging
    to one question.
    """

    def __init__(self, number: int):
        self.number = number
        self._lines: list[str] = []
        self.errors: list[ImportError] = []

    def append(self, text: str) -> None:
        self._lines.append(text)

    def is_question_marker(self, text: str) -> bool:
        return bool(QUESTION_PATTERN.fullmatch(text.strip()))

    def parse(self) -> QuestionData:
        lines = list(self._lines)

        answer = ""
        mark = 1.0
        choices: list[QuestionChoice] = []

        content_lines: list[str] = []

        for line in reversed(lines):
            stripped = line.strip()

            answer_match = ANSWER_PATTERN.fullmatch(stripped)

            if answer_match:
                value = answer_match.group(1).strip()

                if not value:
                    self._add_error(
                        "Answer was provided without a value."
                    )
                elif answer:
                    self._add_error(
                        "Multiple answer declarations were found."
                    )
                else:
                    answer = value

                continue

            mark_match = MARK_PATTERN.fullmatch(stripped)

            if mark_match:
                value = mark_match.group(1).strip()

                if not value:
                    self._add_error(
                        "Mark was provided without a value."
                    )
                else:
                    try:
                        mark = float(value)

                        if mark <= 0:
                            self._add_error(
                                "Mark must be greater than zero."
                            )

                    except ValueError:
                        self._add_error(
                            f"Invalid mark value: '{value}'."
                        )

                continue

            content_lines.append(line)

        content_lines.reverse()

        choice_start = self._find_choice_start(content_lines)

        if choice_start is not None:
            choice_lines = content_lines[choice_start:]
            content_lines = content_lines[:choice_start]

            for line in choice_lines:
                choice = self._parse_choice(line)

                if choice is not None:
                    choices.append(choice)
                elif line.strip():
                    self._add_error(
                        "Invalid text found inside the choice section.",
                        content="".join(choice_lines),
                    )

        content = "".join(content_lines).strip()

        question_type = self._determine_type(
            answer=answer,
            choices=choices,
        )

        return QuestionData(
            number=self.number,
            content=content,
            type=question_type,
            answer=answer,
            mark=mark,
            choices=choices,
        )

    def _find_choice_start(
        self,
        lines: list[str],
    ) -> int | None:
        for index, line in enumerate(lines):
            if CHOICE_PATTERN.match(line):
                return index

        return None

    def _parse_choice(
        self,
        line: str,
    ) -> QuestionChoice | None:
        match = CHOICE_PATTERN.fullmatch(line)

        if match is None:
            return None

        label = match.group(1).lower()
        text = match.group(2).strip()

        if not text:
            self._add_error(
                f"Choice '{label}' has no text."
            )

        return QuestionChoice(
            label=label,
            text=text,
        )

    @staticmethod
    def _determine_type(
        answer: str,
        choices: list[QuestionChoice],
    ) -> QuestionType:
        if choices:
            return QuestionType.SINGLE_CHOICE

        if answer:
            return QuestionType.FILL_IN_BLANK

        return QuestionType.THEORY

    def _add_error(
        self,
        message: str,
        content: str = "",
    ) -> None:
        self.errors.append(
            ImportError(
                question_number=self.number,
                message=message,
                content=content,
            )
        )
