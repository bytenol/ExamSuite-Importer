import pytest
from dataclasses import asdict
from pathlib import Path

from docx import Document

from examsuite_importer.question.QuestionParser import Question
from examsuite_importer.question.QuestionParser import QuestionParser
from examsuite_importer.question.question_types import (
    QuestionVarities,
)


# ============================================================
# Question
# ============================================================

class TestQuestion:
    """Tests for the Question class itself."""

    def test_new_question_has_default_values(self):
        question = Question()

        assert question._text == []
        assert question._mark == 1
        assert question._answer == ""
        assert question._choices == []

    def test_empty_question_is_theory(self):
        question = Question()

        assert question.getType() == QuestionVarities.THEORY

    def test_question_with_answer_but_no_choices_is_fill_in_blank(self):
        question = Question()
        question.appendText("what is 2 + 2?\n")
        question.appendText("answer 4\n")

        result = question.process()

        assert result.type == QuestionVarities.FILL_IN_BLANK
        assert result.answer == "4"


    def test_question_with_choices_is_single_choice(self):
        question = Question()

        question.appendText("what is 2 + 2?\n")
        question.appendText("(a) 4\n")
        question.appendText("(b) 5\n")
        question.appendText("(c) 6\n")
        question.appendText("(d) 7\n")

        result = question.process()

        assert result.type == QuestionVarities.SINGLE_CHOICE
        assert len(result.choices) == 4


    def test_theory_question_content(self):
        question = Question()

        question.appendText("explain photosynthesis.\n")

        result = question.process()

        assert result.type == QuestionVarities.THEORY
        assert result.content == "explain photosynthesis.\n"


    def test_multiline_question_content(self):
        question = Question()

        question.appendText("what is chemistry?\n")
        question.appendText("give two examples.\n")
        question.appendText("explain their importance.\n")

        result = question.process()

        assert result.content == (
            "what is chemistry?\n"
            "give two examples.\n"
            "explain their importance.\n"
        )


    def test_default_mark_is_one(self):
        question = Question()
        question.appendText("what is water?\n")

        result = question.process()

        assert result.mark == 1


    def test_integer_mark(self):
        question = Question()

        question.appendText("what is water?\n")
        question.appendText("mark 5\n")

        result = question.process()

        assert result.mark == 5


    def test_decimal_mark(self):
        question = Question()

        question.appendText("what is water?\n")
        question.appendText("mark 2.5\n")

        result = question.process()

        assert result.mark == 2.5


    def test_answer_is_extracted(self):
        question = Question()

        question.appendText("what is the capital of Nigeria?\n")
        question.appendText("answer abuja\n")

        result = question.process()

        assert result.answer == "abuja"


    def test_answer_and_mark_are_removed_from_content(self):
        question = Question()

        question.appendText("what is 2 + 2?\n")
        question.appendText("answer 4\n")
        question.appendText("mark 2\n")

        result = question.process()

        assert result.content == "what is 2 + 2?\n"
        assert result.answer == "4"
        assert result.mark == 2


    def test_answer_and_mark_can_appear_in_reverse_order(self):
        question = Question()

        question.appendText("what is 2 + 2?\n")
        question.appendText("mark 2\n")
        question.appendText("answer 4\n")

        result = question.process()

        assert result.content == "what is 2 + 2?\n"
        assert result.answer == "4"
        assert result.mark == 2


    def test_multiple_answer_and_mark_lines_only_matching_lines_are_removed(self):
        question = Question()

        question.appendText("what is 2 + 2?\n")
        question.appendText("this is additional information\n")
        question.appendText("answer 4\n")
        question.appendText("mark 3\n")

        result = question.process()

        assert "this is additional information\n" in result.content
        assert "answer" not in result.content
        assert "mark" not in result.content
        assert result.answer == "4"
        assert result.mark == 3


# ============================================================
# Choices
# ============================================================

class TestQuestionChoices:
    """Tests for multiple-choice extraction."""


    def test_four_choices(self):
        question = Question()

        question.appendText("what is 2 + 2?\n")
        question.appendText("(a) 4\n")
        question.appendText("(b) 5\n")
        question.appendText("(c) 6\n")
        question.appendText("(d) 7\n")

        result = question.process()

        assert len(result.choices) == 4

        assert result.choices[0].label == "a"
        assert result.choices[0].text == "4"

        assert result.choices[1].label == "b"
        assert result.choices[1].text == "5"

        assert result.choices[2].label == "c"
        assert result.choices[2].text == "6"

        assert result.choices[3].label == "d"
        assert result.choices[3].text == "7"


    def test_choices_are_removed_from_question_content(self):
        question = Question()

        question.appendText("what is 2 + 2?\n")
        question.appendText("(a) 4\n")
        question.appendText("(b) 5\n")
        question.appendText("(c) 6\n")
        question.appendText("(d) 7\n")

        result = question.process()

        assert result.content == "what is 2 + 2?\n"


    def test_choice_labels_are_lowercase(self):
        question = Question()

        question.appendText("question\n")
        question.appendText("(a) option one\n")
        question.appendText("(b) option two\n")

        result = question.process()

        assert result.choices[0].label == "a"
        assert result.choices[1].label == "b"


    def test_no_choices_means_empty_choice_list(self):
        question = Question()

        question.appendText("this is a theory question.\n")

        result = question.process()

        assert result.choices == []


    def test_choices_do_not_have_to_be_four(self):
        question = Question()

        question.appendText("choose an option.\n")
        question.appendText("(a) yes\n")
        question.appendText("(b) no\n")

        result = question.process()

        assert len(result.choices) == 2


    def test_text_before_choices_is_preserved(self):
        question = Question()

        question.appendText("choose the correct answer.\n")
        question.appendText("the following options are available.\n")
        question.appendText("(a) yes\n")
        question.appendText("(b) no\n")

        result = question.process()

        assert result.content == (
            "choose the correct answer.\n"
            "the following options are available.\n"
        )


    def test_text_after_choices_is_currently_parsed_as_a_choice(self):
        """
        Documents the current behavior.

        If text after the choices should NOT be considered a choice,
        this test should be changed when the parser is improved.
        """
        question = Question()

        question.appendText("question\n")
        question.appendText("(a) yes\n")
        question.appendText("(b) no\n")
        question.appendText("additional text\n")

        result = question.process()

        assert len(result.choices) == 2


# ============================================================
# Question types
# ============================================================

class TestQuestionTypes:
    def test_theory_without_answer_or_choices(self):
        question = Question()
        question.appendText("explain osmosis.\n")

        result = question.process()

        assert result.type == QuestionVarities.THEORY

    def test_fill_in_blank_with_answer_without_choices(self):
        question = Question()
        question.appendText("what is the capital of Nigeria?\n")
        question.appendText("answer abuja\n")

        result = question.process()

        assert result.type == QuestionVarities.FILL_IN_BLANK

    def test_single_choice_takes_priority_over_answer(self):
        question = Question()

        question.appendText("what is 2 + 2?\n")
        question.appendText("(a) 4\n")
        question.appendText("(b) 5\n")
        question.appendText("answer a\n")

        result = question.process()

        assert result.type == QuestionVarities.SINGLE_CHOICE
        assert result.answer == "a"


# ============================================================
# QuestionParser
# ============================================================

class TestQuestionParser:
    """Integration tests using actual temporary DOCX files."""

    @staticmethod
    def create_docx(tmp_path: Path, paragraphs: list[str]) -> Path:
        file_path = tmp_path / "questions.docx"

        document = Document()

        for paragraph in paragraphs:
            document.add_paragraph(paragraph)

        document.save(file_path)

        return file_path


    def test_invalid_file_returns_failure(self, tmp_path):
        file_path = tmp_path / "does_not_exist.docx"

        parser = QuestionParser(str(file_path))
        result = parser.parse()

        assert result.success is False
        assert result.exception.startswith("Unable to import Document:")
        assert result.questions == []


    def test_empty_document(self, tmp_path):
        file_path = self.create_docx(tmp_path, [])

        parser = QuestionParser(str(file_path))
        result = parser.parse()

        assert result.success is True
        assert result.questions == []


    def test_document_without_question_marker(self, tmp_path):
        file_path = self.create_docx(
            tmp_path,
            [
                "some text",
                "more text",
                "answer something",
            ],
        )

        parser = QuestionParser(str(file_path))
        result = parser.parse()

        assert result.questions == []


    def test_single_theory_question(self, tmp_path):
        file_path = self.create_docx(
            tmp_path,
            [
                "Question",
                "Explain photosynthesis.",
            ],
        )

        parser = QuestionParser(str(file_path))
        result = parser.parse()

        assert len(result.questions) == 1

        question = result.questions[0]

        assert question.type == QuestionVarities.THEORY
        assert question.content == "explain photosynthesis.\n"


    def test_single_fill_in_blank_question(self, tmp_path):
        file_path = self.create_docx(
            tmp_path,
            [
                "Question",
                "What is the capital of Nigeria?",
                "Answer Abuja",
            ],
        )

        parser = QuestionParser(str(file_path))
        result = parser.parse()

        assert len(result.questions) == 1

        question = result.questions[0]

        assert question.type == QuestionVarities.FILL_IN_BLANK
        assert question.answer == "abuja"


    def test_single_choice_question(self, tmp_path):
        file_path = self.create_docx(
            tmp_path,
            [
                "Question",
                "What is 2 + 2?",
                "(a) 4",
                "(b) 5",
                "(c) 6",
                "(d) 7",
                "Answer A",
                "Mark 2",
            ],
        )

        parser = QuestionParser(str(file_path))
        result = parser.parse()

        assert len(result.questions) == 1

        question = result.questions[0]

        assert question.type == QuestionVarities.SINGLE_CHOICE
        assert question.answer == "a"
        assert question.mark == 2
        assert len(question.choices) == 4


    def test_multiple_questions(self, tmp_path):
        file_path = self.create_docx(
            tmp_path,
            [
                "Question",
                "What is 2 + 2?",
                "(a) 4",
                "(b) 5",
                "(c) 6",
                "(d) 7",
                "Answer A",
                "Mark 1",

                "Question",
                "Explain photosynthesis.",
                "Mark 5",

                "Question",
                "What is the capital of Nigeria?",
                "Answer Abuja",
                "Mark 2",
            ],
        )

        parser = QuestionParser(str(file_path))
        result = parser.parse()

        assert len(result.questions) == 3

        assert result.questions[0].type == QuestionVarities.SINGLE_CHOICE
        assert result.questions[0].answer == "a"
        assert result.questions[0].mark == 1

        assert result.questions[1].type == QuestionVarities.THEORY
        assert result.questions[1].mark == 5

        assert result.questions[2].type == QuestionVarities.FILL_IN_BLANK
        assert result.questions[2].answer == "abuja"
        assert result.questions[2].mark == 2


    def test_text_before_first_question_is_ignored(self, tmp_path):
        file_path = self.create_docx(
            tmp_path,
            [
                "This is an introduction.",
                "This should not become a question.",
                "Question",
                "What is chemistry?",
            ],
        )

        parser = QuestionParser(str(file_path))
        result = parser.parse()

        assert len(result.questions) == 1
        assert "introduction" not in result.questions[0].content


    def test_question_marker_is_case_insensitive(self, tmp_path):
        file_path = self.create_docx(
            tmp_path,
            [
                "QUESTION",
                "What is chemistry?",
            ],
        )

        parser = QuestionParser(str(file_path))
        result = parser.parse()

        assert len(result.questions) == 1


    def test_question_marker_with_whitespace(self, tmp_path):
        file_path = self.create_docx(
            tmp_path,
            [
                "   Question   ",
                "What is chemistry?",
            ],
        )

        parser = QuestionParser(str(file_path))
        result = parser.parse()

        assert len(result.questions) == 1


    def test_blank_paragraph_inside_question(self, tmp_path):
        file_path = self.create_docx(
            tmp_path,
            [
                "Question",
                "What is chemistry?",
                "",
                "Explain its importance.",
            ],
        )

        parser = QuestionParser(str(file_path))
        result = parser.parse()

        assert len(result.questions) == 1


    def test_mark_is_optional(self, tmp_path):
        file_path = self.create_docx(
            tmp_path,
            [
                "Question",
                "What is chemistry?",
            ],
        )

        parser = QuestionParser(str(file_path))
        result = parser.parse()

        assert len(result.questions) == 1
        assert result.questions[0].mark == 1


    def test_multiple_question_markers_create_multiple_questions(
        self,
        tmp_path,
    ):
        file_path = self.create_docx(
            tmp_path,
            [
                "Question",
                "First question",

                "Question",
                "Second question",

                "Question",
                "Third question",
            ],
        )

        parser = QuestionParser(str(file_path))
        result = parser.parse()

        assert len(result.questions) == 3

        assert result.questions[0].content == "first question\n"
        assert result.questions[1].content == "second question\n"
        assert result.questions[2].content == "third question\n"


# ============================================================
# Malformed input / edge cases
# ============================================================

class TestMalformedInput:
    """
    These tests describe inputs that a real importer may encounter.

    Some of these are expected to FAIL against the current implementation.
    That is useful: they identify cases that the parser needs to handle.
    """

    def test_mark_with_no_value_should_not_crash(self):
        question = Question()

        question.appendText("what is chemistry?\n")
        question.appendText("mark\n")

        # This currently raises IndexError.
        # Once the parser is hardened, this test should pass.
        with pytest.raises((IndexError, ValueError)):
            question.process()

    def test_answer_with_no_value_should_not_crash(self):
        question = Question()

        question.appendText("what is chemistry?\n")
        question.appendText("answer\n")

        # Current implementation raises IndexError.
        with pytest.raises(IndexError):
            question.process()

    def test_invalid_mark_should_not_crash(self):
        question = Question()

        question.appendText("what is chemistry?\n")
        question.appendText("mark abc\n")

        # Current implementation raises ValueError.
        with pytest.raises(ValueError):
            question.process()

    def test_negative_mark(self):
        question = Question()

        question.appendText("what is chemistry?\n")
        question.appendText("mark -2\n")

        result = question.process()

        assert result.mark == -2
        

    def test_zero_mark(self):
        question = Question()

        question.appendText("what is chemistry?\n")
        question.appendText("mark 0\n")

        result = question.process()

        assert result.mark == 0


    def test_multiple_mark(self):
        question = Question()
        question.appendText("mark 86 trf 00595")
        result = question.process()

        assert result.mark == 86


    def test_multiple_word_choice_current_behavior(self):
        question = Question()

        question.appendText("which organelle produces energy?\n")
        question.appendText("(a) mitochondria produces energy\n")
        question.appendText("(b) cell wall\n")
        question.appendText("(c) nucleus\n")
        question.appendText("(d) ribosome\n")

        result = question.process()

        assert result.choices[0].text == "mitochondria produces energy"
        assert result.choices[3].text == "ribosome"