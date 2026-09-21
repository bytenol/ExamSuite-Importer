from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.opc.exceptions import PackageNotFoundError

from examsuite_importer.models import (
    ExamMetadata,
    ImportError,
    ImportResult,
    QuestionData,
)

from examsuite_importer.validation.question_validator import (
    QuestionValidator,
)

from .paragraph_parser import ParagraphParser
from .question_parser import QuestionParser


class DocumentParser:

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)

    def parse(self) -> ImportResult:
        try:
            document = Document(self.file_path)

        except (PackageNotFoundError, OSError, ValueError) as exc:
            return ImportResult(
                success=False,
                metadata=ExamMetadata(),
                errors=[
                    ImportError(
                        question_number=None,
                        message=(
                            f"Unable to open document: {exc}"
                        ),
                    )
                ],
            )

        metadata = ExamMetadata()

        questions: list[QuestionData] = []
        errors: list[ImportError] = []

        current_question: QuestionParser | None = None
        question_number = 0

        for paragraph in document.paragraphs:
            try:
                text = ParagraphParser(
                    paragraph
                ).parse()

            except Exception as exc:
                errors.append(
                    ImportError(
                        question_number=question_number or None,
                        message=(
                            f"Unable to parse paragraph: {exc}"
                        ),
                    )
                )
                continue

            if not text.strip():
                continue

            metadata_key = self._parse_metadata(
                text,
                metadata,
            )

            if metadata_key:
                continue

            if self._is_question_marker(text):
                if current_question is not None:
                    question, question_errors = (
                        self._finish_question(
                            current_question
                        )
                    )

                    questions.append(question)
                    errors.extend(question_errors)

                question_number += 1

                current_question = QuestionParser(
                    number=question_number
                )

                continue

            if current_question is None:
                continue

            current_question.append(text)

        if current_question is not None:
            question, question_errors = (
                self._finish_question(
                    current_question
                )
            )

            questions.append(question)
            errors.extend(question_errors)

        validation_errors = QuestionValidator().validate(
            questions
        )

        errors.extend(validation_errors)

        return ImportResult(
            success=len(errors) == 0,
            metadata=metadata,
            questions=questions,
            errors=errors,
        )

    @staticmethod
    def _is_question_marker(text: str) -> bool:
        return text.strip().lower() == "question"

    @staticmethod
    def _parse_metadata(
        text: str,
        metadata: ExamMetadata,
    ) -> bool:
        if ":" not in text:
            return False

        key, value = text.split(":", 1)

        key = key.strip().lower()
        value = value.strip()

        if key == "subject":
            metadata.subject = value
            return True

        if key == "class":
            metadata.class_name = value
            return True

        if key == "section":
            metadata.section = value
            return True

        return False

    @staticmethod
    def _finish_question(
        parser: QuestionParser,
    ) -> tuple[QuestionData, list[ImportError]]:
        question = parser.parse()

        return question, parser.errors