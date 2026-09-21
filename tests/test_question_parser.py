from examsuite_importer.models import QuestionType
from examsuite_importer.parser.question_parser import QuestionParser


def test_parse_theory_question():
    parser = QuestionParser(1)

    parser.append("What is chemistry?")

    question = parser.parse()

    assert question.number == 1
    assert question.content == "What is chemistry?"
    assert question.type == QuestionType.THEORY
    assert question.answer == ""
    assert question.mark == 1.0
    assert question.choices == []
    assert parser.errors == []


def test_parse_fill_in_blank_question():
    parser = QuestionParser(1)

    parser.append("The chemical symbol for sodium is ______.")
    parser.append("answer Na")
    parser.append("mark 1")

    question = parser.parse()

    assert question.number == 1
    assert question.content == (
        "The chemical symbol for sodium is ______."
    )
    assert question.type == QuestionType.FILL_IN_BLANK
    assert question.answer == "Na"
    assert question.mark == 1.0
    assert question.choices == []
    assert parser.errors == []


def test_parse_single_choice_question():
    parser = QuestionParser(1)

    parser.append("What is the chemical symbol for sodium?")
    parser.append("(a) Na")
    parser.append("(b) Ca")
    parser.append("(c) K")
    parser.append("(d) Cl")
    parser.append("answer a")
    parser.append("mark 2")

    question = parser.parse()

    assert question.number == 1
    assert question.content == (
        "What is the chemical symbol for sodium?"
    )
    assert question.type == QuestionType.SINGLE_CHOICE
    assert question.answer == "a"
    assert question.mark == 2.0

    assert len(question.choices) == 4

    assert question.choices[0].label == "a"
    assert question.choices[0].text == "Na"

    assert question.choices[1].label == "b"
    assert question.choices[1].text == "Ca"

    assert question.choices[2].label == "c"
    assert question.choices[2].text == "K"

    assert question.choices[3].label == "d"
    assert question.choices[3].text == "Cl"

    assert parser.errors == []


def test_choice_text_keeps_entire_text():
    parser = QuestionParser(1)

    parser.append("Which organelle is responsible for cellular respiration?")
    parser.append(
        "(a) The mitochondrion produces energy for the cell"
    )
    parser.append(
        "(b) The nucleus controls the activities of the cell"
    )
    parser.append(
        "(c) The ribosome synthesizes proteins in the cell"
    )
    parser.append(
        "(d) The cell wall provides structural support"
    )
    parser.append("answer a")

    question = parser.parse()

    assert question.choices[0].text == (
        "The mitochondrion produces energy for the cell"
    )

    assert question.choices[1].text == (
        "The nucleus controls the activities of the cell"
    )

    assert question.choices[2].text == (
        "The ribosome synthesizes proteins in the cell"
    )

    assert question.choices[3].text == (
        "The cell wall provides structural support"
    )


def test_control_keywords_are_case_insensitive():
    parser = QuestionParser(1)

    parser.append("What is H2O?")
    parser.append("(A) Oxygen")
    parser.append("(B) Hydrogen")
    parser.append("(C) Water")
    parser.append("(D) Carbon dioxide")
    parser.append("ANSWER C")
    parser.append("MARK 3")

    question = parser.parse()

    assert question.answer == "C"
    assert question.mark == 3.0

    assert [choice.label for choice in question.choices] == [
        "a",
        "b",
        "c",
        "d",
    ]

    assert parser.errors == []


def test_original_question_content_is_not_lowercased():
    parser = QuestionParser(1)

    parser.append(
        "DNA contains the genetic information required by the cell."
    )

    question = parser.parse()

    assert question.content == (
        "DNA contains the genetic information required by the cell."
    )


def test_formatted_content_is_preserved():
    parser = QuestionParser(1)

    parser.append(
        "What is <strong>ATP</strong>?"
    )

    question = parser.parse()

    assert question.content == (
        "What is <strong>ATP</strong>?"
    )


def test_equation_content_is_preserved():
    parser = QuestionParser(1)

    parser.append(
        r"Solve $x^2 + 2x + 1 = 0$."
    )

    question = parser.parse()

    assert question.content == (
        r"Solve $x^2 + 2x + 1 = 0$."
    )


def test_default_mark_is_one():
    parser = QuestionParser(1)

    parser.append("What is an atom?")

    question = parser.parse()

    assert question.mark == 1.0


def test_mark_can_be_decimal():
    parser = QuestionParser(1)

    parser.append("Calculate the value of x.")
    parser.append("answer 2")
    parser.append("mark 2.5")

    question = parser.parse()

    assert question.mark == 2.5


def test_missing_answer_value_creates_error():
    parser = QuestionParser(1)

    parser.append("What is an atom?")
    parser.append("answer")

    question = parser.parse()

    assert question.type == QuestionType.THEORY

    assert any(
        "Answer was provided without a value."
        in error.message
        for error in parser.errors
    )


def test_missing_mark_value_creates_error():
    parser = QuestionParser(1)

    parser.append("What is an atom?")
    parser.append("mark")

    question = parser.parse()

    assert question.mark == 1.0

    assert any(
        "Mark was provided without a value."
        in error.message
        for error in parser.errors
    )


def test_invalid_mark_creates_error():
    parser = QuestionParser(1)

    parser.append("What is an atom?")
    parser.append("mark abc")

    question = parser.parse()

    assert question.mark == 1.0

    assert any(
        "Invalid mark value: 'abc'."
        in error.message
        for error in parser.errors
    )


def test_negative_mark_creates_error():
    parser = QuestionParser(1)

    parser.append("What is an atom?")
    parser.append("mark -2")

    question = parser.parse()

    assert question.mark == -2.0

    assert any(
        "Mark must be greater than zero."
        in error.message
        for error in parser.errors
    )


def test_zero_mark_creates_error():
    parser = QuestionParser(1)

    parser.append("What is an atom?")
    parser.append("mark 0")

    question = parser.parse()

    assert question.mark == 0.0

    assert any(
        "Mark must be greater than zero."
        in error.message
        for error in parser.errors
    )


def test_question_with_only_three_choices():
    parser = QuestionParser(1)

    parser.append("Which is a noble gas?")
    parser.append("(a) Oxygen")
    parser.append("(b) Nitrogen")
    parser.append("(c) Neon")
    parser.append("answer c")

    question = parser.parse()

    assert question.type == QuestionType.SINGLE_CHOICE
    assert len(question.choices) == 3


def test_duplicate_answer_declaration_creates_error():
    parser = QuestionParser(1)

    parser.append("What is 2 + 2?")
    parser.append("answer 4")
    parser.append("answer five")

    parser.parse()

    assert any(
        "Multiple answer declarations were found."
        in error.message
        for error in parser.errors
    )


def test_question_number_is_preserved():
    parser = QuestionParser(17)

    parser.append("What is an element?")

    question = parser.parse()

    assert question.number == 17