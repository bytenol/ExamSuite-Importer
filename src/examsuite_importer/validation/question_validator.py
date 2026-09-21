from __future__ import annotations

from examsuite_importer.models import (
    ImportError,
    QuestionData,
    QuestionType,
)


class QuestionValidator:

    def validate(
        self,
        questions: list[QuestionData],
    ) -> list[ImportError]:
        errors: list[ImportError] = []

        for question in questions:
            errors.extend(
                self._validate_question(question)
            )

        return errors

    def _validate_question(
        self,
        question: QuestionData,
    ) -> list[ImportError]:
        errors: list[ImportError] = []

        if not question.content.strip():
            errors.append(
                ImportError(
                    question_number=question.number,
                    message="Question content cannot be empty.",
                )
            )

        if question.mark <= 0:
            errors.append(
                ImportError(
                    question_number=question.number,
                    message="Question mark must be greater than zero.",
                )
            )

        if question.type == QuestionType.SINGLE_CHOICE:
            errors.extend(
                self._validate_single_choice(question)
            )

        elif question.type == QuestionType.FILL_IN_BLANK:
            if not question.answer.strip():
                errors.append(
                    ImportError(
                        question_number=question.number,
                        message="Answer must be provided for a fill-in-the-blank question.",
                    )
                )

        return errors

    def _validate_single_choice(
        self,
        question: QuestionData,
    ) -> list[ImportError]:
        errors: list[ImportError] = []

        if not question.answer.strip():
            errors.append(
                ImportError(
                    question_number=question.number,
                    message="Answer must be provided for a single-choice question.",
                )
            )

        elif question.answer.lower() not in {
            "a",
            "b",
            "c",
            "d",
        }:
            errors.append(
                ImportError(
                    question_number=question.number,
                    message=(
                        "Answer to a single-choice question must be "
                        "'a', 'b', 'c', or 'd'."
                    ),
                )
            )

        if len(question.choices) != 4:
            errors.append(
                ImportError(
                    question_number=question.number,
                    message=(
                        "A single-choice question must provide exactly "
                        "4 options."
                    ),
                )
            )

        labels = [
            choice.label.lower()
            for choice in question.choices
        ]

        if len(labels) != len(set(labels)):
            errors.append(
                ImportError(
                    question_number=question.number,
                    message="Choice labels must be unique.",
                )
            )

        expected = {"a", "b", "c", "d"}

        if set(labels) != expected:
            errors.append(
                ImportError(
                    question_number=question.number,
                    message="Choices must contain exactly a, b, c, and d.",
                )
            )

        return errors