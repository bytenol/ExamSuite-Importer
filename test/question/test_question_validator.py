import pytest

from examsuite_importer.question.question_types import (
    QuestionChoice,
    QuestionData,
    QuestionValidatorError,
    QuestionVarities,
)
from examsuite_importer.question.question_validator import QuestionValidator


# ============================================================
# Helpers
# ============================================================

def make_question(
    *,
    content="What is the answer?",
    answer="",
    question_type=QuestionVarities.THEORY,
    mark=1,
    choices=None,
):
    return QuestionData(
        type=question_type,
        content=content,
        answer=answer,
        mark=mark,
        choices=choices or [],
    )


def make_choice(label, text):
    return QuestionChoice(
        label=label,
        text=text,
    )


# ============================================================
# Basic validator behavior
# ============================================================

class TestQuestionValidator:
    def test_empty_question_list_returns_no_errors(self):
        validator = QuestionValidator([])

        errors = validator.validate()

        assert errors == []

    def test_valid_theory_question(self):
        question = make_question(
            content="Explain photosynthesis.",
            question_type=QuestionVarities.THEORY,
        )

        errors = QuestionValidator([question]).validate()

        assert errors == []

    def test_valid_fill_in_blank_question(self):
        question = make_question(
            content="What is the capital of Nigeria?",
            answer="abuja",
            question_type=QuestionVarities.FILL_IN_BLANK,
        )

        errors = QuestionValidator([question]).validate()

        assert errors == []

    def test_valid_single_choice_question(self):
        choices = [
            make_choice("a", "Hydrogen"),
            make_choice("b", "Oxygen"),
            make_choice("c", "Nitrogen"),
            make_choice("d", "Carbon"),
        ]

        question = make_question(
            content="Which is an element?",
            answer="a",
            question_type=QuestionVarities.SINGLE_CHOICE,
            choices=choices,
        )

        errors = QuestionValidator([question]).validate()

        assert errors == []


# ============================================================
# Answer validation
# ============================================================

class TestAnswerValidation:
    def test_theory_question_does_not_require_answer(self):
        question = make_question(
            content="Explain the process of photosynthesis.",
            answer="",
            question_type=QuestionVarities.THEORY,
        )

        errors = QuestionValidator([question]).validate()

        assert errors == []

    def test_fill_in_blank_requires_answer(self):
        question = make_question(
            content="What is the capital of Nigeria?",
            answer="",
            question_type=QuestionVarities.FILL_IN_BLANK,
        )

        errors = QuestionValidator([question]).validate()

        assert len(errors) == 1

        assert errors[0].message == (
            "Answer must be provided for this question"
        )

    def test_single_choice_requires_answer(self):
        choices = [
            make_choice("a", "One"),
            make_choice("b", "Two"),
            make_choice("c", "Three"),
            make_choice("d", "Four"),
        ]

        question = make_question(
            content="Choose the correct answer.",
            answer="",
            question_type=QuestionVarities.SINGLE_CHOICE,
            choices=choices,
        )

        errors = QuestionValidator([question]).validate()

        assert len(errors) == 1

        assert errors[0].message == (
            "Answer must be provided for this question"
        )

    def test_single_choice_accepts_a(self):
        question = make_question(
            answer="a",
            question_type=QuestionVarities.SINGLE_CHOICE,
            choices=[
                make_choice("a", "One"),
                make_choice("b", "Two"),
                make_choice("c", "Three"),
                make_choice("d", "Four"),
            ],
        )

        errors = QuestionValidator([question]).validate()

        assert errors == []

    def test_single_choice_accepts_b(self):
        question = make_question(
            answer="b",
            question_type=QuestionVarities.SINGLE_CHOICE,
            choices=[
                make_choice("a", "One"),
                make_choice("b", "Two"),
                make_choice("c", "Three"),
                make_choice("d", "Four"),
            ],
        )

        errors = QuestionValidator([question]).validate()

        assert errors == []

    def test_single_choice_accepts_c(self):
        question = make_question(
            answer="c",
            question_type=QuestionVarities.SINGLE_CHOICE,
            choices=[
                make_choice("a", "One"),
                make_choice("b", "Two"),
                make_choice("c", "Three"),
                make_choice("d", "Four"),
            ],
        )

        errors = QuestionValidator([question]).validate()

        assert errors == []

    def test_single_choice_accepts_d(self):
        question = make_question(
            answer="d",
            question_type=QuestionVarities.SINGLE_CHOICE,
            choices=[
                make_choice("a", "One"),
                make_choice("b", "Two"),
                make_choice("c", "Three"),
                make_choice("d", "Four"),
            ],
        )

        errors = QuestionValidator([question]).validate()

        assert errors == []


# ============================================================
# Invalid SingleChoice answers
# ============================================================

class TestInvalidSingleChoiceAnswers:
    @pytest.mark.parametrize(
        "answer",
        [
            "A",
            "B",
            "C",
            "D",
            "e",
            "x",
            "1",
            "0",
            "ab",
            "abc",
            " a",
            "a ",
            " a ",
            "aa",
            "abcd",
        ],
    )
    def test_invalid_single_choice_answer(self, answer):
        question = make_question(
            answer=answer,
            question_type=QuestionVarities.SINGLE_CHOICE,
            choices=[
                make_choice("a", "One"),
                make_choice("b", "Two"),
                make_choice("c", "Three"),
                make_choice("d", "Four"),
            ],
        )

        errors = QuestionValidator([question]).validate()

        assert len(errors) == 1

        assert errors[0].message == (
            "Answer to a SingleChoice Question must be "
            "a single character 'a','b','c','d'"
        )


# ============================================================
# Choice count validation
# ============================================================

class TestChoiceCount:
    @pytest.mark.parametrize(
        "choices",
        [
            [],
            [
                make_choice("a", "One"),
            ],
            [
                make_choice("a", "One"),
                make_choice("b", "Two"),
            ],
            [
                make_choice("a", "One"),
                make_choice("b", "Two"),
                make_choice("c", "Three"),
            ],
            [
                make_choice("a", "One"),
                make_choice("b", "Two"),
                make_choice("c", "Three"),
                make_choice("d", "Four"),
                make_choice("e", "Five"),
            ],
        ],
    )
    def test_single_choice_must_have_exactly_four_choices(self, choices):
        question = make_question(
            answer="a",
            question_type=QuestionVarities.SINGLE_CHOICE,
            choices=choices,
        )

        errors = QuestionValidator([question]).validate()

        assert len(errors) == 1

        assert errors[0].message == (
            "SingleChoice Question must provide 4 options"
        )

    def test_exactly_four_choices_are_valid(self):
        choices = [
            make_choice("a", "One"),
            make_choice("b", "Two"),
            make_choice("c", "Three"),
            make_choice("d", "Four"),
        ]

        question = make_question(
            answer="a",
            question_type=QuestionVarities.SINGLE_CHOICE,
            choices=choices,
        )

        errors = QuestionValidator([question]).validate()

        assert errors == []


# ============================================================
# Error metadata
# ============================================================

class TestValidationErrorMetadata:
    def test_error_contains_question_line(self):
        question = make_question(
            content="What is the capital of Nigeria?",
            answer="",
            question_type=QuestionVarities.FILL_IN_BLANK,
        )

        errors = QuestionValidator([question]).validate()

        assert errors[0].line == 1

    def test_error_contains_first_30_characters_of_content(self):
        content = "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789"

        question = make_question(
            content=content,
            answer="",
            question_type=QuestionVarities.FILL_IN_BLANK,
        )

        errors = QuestionValidator([question]).validate()

        assert errors[0].content == content[:30]

    def test_error_content_is_shortened_to_30_characters(self):
        content = "This is a very long question that exceeds thirty characters."

        question = make_question(
            content=content,
            answer="",
            question_type=QuestionVarities.FILL_IN_BLANK,
        )

        errors = QuestionValidator([question]).validate()

        assert len(errors[0].content) == 30
        assert errors[0].content == content[:30]


# ============================================================
# Multiple questions
# ============================================================

class TestMultipleQuestions:
    def test_validator_validates_all_questions(self):
        questions = [
            make_question(
                content="Theory question",
                question_type=QuestionVarities.THEORY,
            ),
            make_question(
                content="Fill in the blank",
                answer="answer",
                question_type=QuestionVarities.FILL_IN_BLANK,
            ),
            make_question(
                content="Multiple choice",
                answer="a",
                question_type=QuestionVarities.SINGLE_CHOICE,
                choices=[
                    make_choice("a", "One"),
                    make_choice("b", "Two"),
                    make_choice("c", "Three"),
                    make_choice("d", "Four"),
                ],
            ),
        ]

        errors = QuestionValidator(questions).validate()

        assert errors == []

    def test_validator_returns_errors_for_multiple_invalid_questions(self):
        questions = [
            make_question(
                content="First invalid question",
                answer="",
                question_type=QuestionVarities.FILL_IN_BLANK,
            ),
            make_question(
                content="Second invalid question",
                answer="x",
                question_type=QuestionVarities.SINGLE_CHOICE,
                choices=[
                    make_choice("a", "One"),
                    make_choice("b", "Two"),
                    make_choice("c", "Three"),
                    make_choice("d", "Four"),
                ],
            ),
            make_question(
                content="Third invalid question",
                answer="a",
                question_type=QuestionVarities.SINGLE_CHOICE,
                choices=[
                    make_choice("a", "One"),
                    make_choice("b", "Two"),
                ],
            ),
        ]

        errors = QuestionValidator(questions).validate()

        assert len(errors) == 3

    def test_error_line_numbers_are_correct(self):
        questions = [
            make_question(
                content="Valid theory question",
                question_type=QuestionVarities.THEORY,
            ),
            make_question(
                content="Invalid fill question",
                answer="",
                question_type=QuestionVarities.FILL_IN_BLANK,
            ),
            make_question(
                content="Another valid theory question",
                question_type=QuestionVarities.THEORY,
            ),
            make_question(
                content="Invalid choice question",
                answer="x",
                question_type=QuestionVarities.SINGLE_CHOICE,
                choices=[
                    make_choice("a", "One"),
                    make_choice("b", "Two"),
                    make_choice("c", "Three"),
                    make_choice("d", "Four"),
                ],
            ),
        ]

        errors = QuestionValidator(questions).validate()

        assert len(errors) == 2

        assert errors[0].line == 2
        assert errors[1].line == 4


# ============================================================
# Validation order / continue behavior
# ============================================================

class TestValidationOrder:
    def test_missing_answer_stops_further_single_choice_validation(self):
        question = make_question(
            content="Invalid question",
            answer="",
            question_type=QuestionVarities.SINGLE_CHOICE,
            choices=[],
        )

        errors = QuestionValidator([question]).validate()

        assert len(errors) == 1

        assert errors[0].message == (
            "Answer must be provided for this question"
        )

    def test_invalid_answer_stops_choice_count_validation(self):
        question = make_question(
            content="Invalid question",
            answer="x",
            question_type=QuestionVarities.SINGLE_CHOICE,
            choices=[],
        )

        errors = QuestionValidator([question]).validate()

        assert len(errors) == 1

        assert errors[0].message == (
            "Answer to a SingleChoice Question must be "
            "a single character 'a','b','c','d'"
        )

    def test_valid_answer_but_wrong_choice_count_returns_choice_error(self):
        question = make_question(
            content="Invalid question",
            answer="a",
            question_type=QuestionVarities.SINGLE_CHOICE,
            choices=[
                make_choice("a", "One"),
                make_choice("b", "Two"),
            ],
        )

        errors = QuestionValidator([question]).validate()

        assert len(errors) == 1

        assert errors[0].message == (
            "SingleChoice Question must provide 4 options"
        )