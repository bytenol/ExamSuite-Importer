from __future__ import annotations
import re 

from docx import Document
from docx.opc.exceptions import PackageNotFoundError

from examsuite_importer.exceptions import InvalidFileNameError
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

    def __init__(self, file_path: str):
        self.file_path = file_path

    def parse(self) -> ImportResult:
        metadata = ExamMetadata()

        try:
            subject, class_name, section = self._get_metadata(self.file_path)
            metadata.section = section
            metadata.class_name = class_name
            metadata.subject = subject
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

        except InvalidFileNameError as exc:
            return ImportResult(
                success=False,
                metadata=ExamMetadata(),
                errors=[
                    ImportError(
                        question_number=None,
                        message=(
                            f"Filename mismatch: {exc}"
                        ),
                    )
                ],
            )

        questions: list[QuestionData] = []
        errors: list[ImportError] = []

        current_question: QuestionParser | None = None
        question_number = 0

        for paragraph in document.paragraphs:
            try:
                text = ParagraphParser(paragraph).parse()

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
    def _finish_question(parser: QuestionParser) -> tuple[QuestionData, list[ImportError]]:
        question = parser.parse()

        return question, parser.errors


    @staticmethod
    def _get_metadata(file_path: str):
        m = re.search(r"[^/\\]+\.docx$", str(file_path))
        if not m:
            return ("", "", "")

        name = (m.group().split(".docx")[0]).split("_")
        if  len(name) != 3:
            raise InvalidFileNameError("File must be named as subject_class_section")

        return (name[0], name[1], name[2])


