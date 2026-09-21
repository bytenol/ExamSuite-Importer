from examsuite_importer.models import (
    QuestionChoice,
    QuestionData,
    QuestionType,
    )
from examsuite_importer.validation import QuestionValidator

def validate(question: QuestionData):
    return QuestionValidator().validate([question])

def test_valid_theory_question():
    question = QuestionData(
    number=1,
    content="Explain the meaning of oxidation.",
    type=QuestionType.THEORY,
    mark=5,
    )

    
    errors = validate(question)

    assert errors == []
    

def test_valid_fill_in_blank_question():
    question = QuestionData(
    number=1,
    content="The chemical formula for water is ______.",
    type=QuestionType.FILL_IN_BLANK,
    answer="H2O",
    mark=1,
    )


    errors = validate(question)

    assert errors == []
    

def test_valid_single_choice_question():
    question = QuestionData(
    number=1,
    content="Which of the following is a noble gas?",
    type=QuestionType.SINGLE_CHOICE,
    answer="c",
    mark=1,
    choices=[
    QuestionChoice(label="a", text="Oxygen"),
    QuestionChoice(label="b", text="Nitrogen"),
    QuestionChoice(label="c", text="Neon"),
    QuestionChoice(label="d", text="Hydrogen"),
    ],
    )

    
    errors = validate(question)

    assert errors == []
    

def test_empty_question_content_is_invalid():
    question = QuestionData(
    number=1,
    content="",
    type=QuestionType.THEORY,
    mark=5,
    )

    
    errors = validate(question)

    assert any(
        error.message == "Question content cannot be empty."
        for error in errors
    )
    

def test_whitespace_only_question_content_is_invalid():
    question = QuestionData(
    number=1,
    content="   ",
    type=QuestionType.THEORY,
    mark=5,
    )

    
    errors = validate(question)

    assert any(
        error.message == "Question content cannot be empty."
        for error in errors
    )
    

def test_zero_mark_is_invalid():
    question = QuestionData(
    number=1,
    content="Explain diffusion.",
    type=QuestionType.THEORY,
    mark=0,
    )

    
    errors = validate(question)

    assert any(
        error.message == "Question mark must be greater than zero."
        for error in errors
    )
    

def test_negative_mark_is_invalid():
    question = QuestionData(
    number=1,
    content="Explain diffusion.",
    type=QuestionType.THEORY,
    mark=-2,
    )

    
    errors = validate(question)

    assert any(
        error.message == "Question mark must be greater than zero."
        for error in errors
    )
    

def test_fill_in_blank_requires_answer():
    question = QuestionData(
    number=1,
    content="The capital of Nigeria is ______.",
    type=QuestionType.FILL_IN_BLANK,
    answer="",
    mark=1,
    )

    
    errors = validate(question)

    assert any(
        error.message
        == "Answer must be provided for a fill-in-the-blank question."
        for error in errors
    )
    

def test_single_choice_requires_answer():
    question = QuestionData(
    number=1,
    content="Which is a programming language?",
    type=QuestionType.SINGLE_CHOICE,
    answer="",
    mark=1,
    choices=[
    QuestionChoice(label="a", text="Python"),
    QuestionChoice(label="b", text="HTML"),
    QuestionChoice(label="c", text="CSS"),
    QuestionChoice(label="d", text="SQL"),
    ],
    )

    
    errors = validate(question)

    assert any(
        error.message
        == "Answer must be provided for a single-choice question."
        for error in errors
    )
    

def test_single_choice_answer_must_be_valid_label():
    question = QuestionData(
    number=1,
    content="Which is a programming language?",
    type=QuestionType.SINGLE_CHOICE,
    answer="e",
    mark=1,
    choices=[
    QuestionChoice(label="a", text="Python"),
    QuestionChoice(label="b", text="HTML"),
    QuestionChoice(label="c", text="CSS"),
    QuestionChoice(label="d", text="SQL"),
    ],
    )

    
    errors = validate(question)

    assert any(
        "must be 'a', 'b', 'c', or 'd'"
        in error.message
        for error in errors
    )
    

def test_single_choice_requires_exactly_four_choices():
    question = QuestionData(
    number=1,
    content="Which is a programming language?",
    type=QuestionType.SINGLE_CHOICE,
    answer="a",
    mark=1,
    choices=[
    QuestionChoice(label="a", text="Python"),
    QuestionChoice(label="b", text="HTML"),
    QuestionChoice(label="c", text="CSS"),
    ],
    )

    
    errors = validate(question)

    assert any(
        error.message
        == "A single-choice question must provide exactly 4 options."
        for error in errors
    )
    

def test_single_choice_rejects_duplicate_labels():
    question = QuestionData(
    number=1,
    content="Which is a programming language?",
    type=QuestionType.SINGLE_CHOICE,
    answer="a",
    mark=1,
    choices=[
    QuestionChoice(label="a", text="Python"),
    QuestionChoice(label="a", text="Java"),
    QuestionChoice(label="c", text="CSS"),
    QuestionChoice(label="d", text="SQL"),
    ],
    )

    
    errors = validate(question)

    assert any(
        error.message == "Choice labels must be unique."
        for error in errors
    )
    

def test_single_choice_requires_a_b_c_and_d():
    question = QuestionData(
    number=1,
    content="Which is a programming language?",
    type=QuestionType.SINGLE_CHOICE,
    answer="a",
    mark=1,
    choices=[
    QuestionChoice(label="a", text="Python"),
    QuestionChoice(label="b", text="Java"),
    QuestionChoice(label="c", text="C++"),
    QuestionChoice(label="e", text="Rust"),
    ],
    )

    
    errors = validate(question)

    assert any(
        error.message
        == "Choices must contain exactly a, b, c, and d."
        for error in errors
    )
    

def test_multiple_validation_errors_are_returned():
    question = QuestionData(
    number=7,
    content="",
    type=QuestionType.SINGLE_CHOICE,
    answer="",
    mark=0,
    choices=[],
    )

    
    errors = validate(question)

    messages = {error.message for error in errors}

    assert "Question content cannot be empty." in messages
    assert "Question mark must be greater than zero." in messages
    assert (
        "Answer must be provided for a single-choice question."
        in messages
    )
    assert (
        "A single-choice question must provide exactly 4 options."
        in messages
    )
    

def test_validation_preserves_question_number():
    question = QuestionData(
    number=12,
    content="",
    type=QuestionType.THEORY,
    mark=1,
    )

    
    errors = validate(question)

    assert errors
    assert all(error.question_number == 12 for error in errors)
    

def test_validator_can_validate_multiple_questions():
    questions = [
    QuestionData(
    number=1,
    content="What is an atom?",
    type=QuestionType.THEORY,
    mark=2,
    ),
    QuestionData(
    number=2,
    content="",
    type=QuestionType.THEORY,
    mark=2,
    ),
    QuestionData(
    number=3,
    content="Water freezes at ___ °C.",
    type=QuestionType.FILL_IN_BLANK,
    answer="0",
    mark=1,
    ),
    ]

    
    errors = QuestionValidator().validate(questions)

    assert len(errors) == 1
    assert errors[0].question_number == 2
    assert errors[0].message == "Question content cannot be empty."
    
