from docx import Document

from examsuite_importer.question.ParagraphParser import ParagraphParser
from examsuite_importer.question.question_types import (
    QuestionChoice, 
    QuestionData,
    QuestionParserResult, 
    QuestionVarities
)
from examsuite_importer.question.question_validator import QuestionValidator


class Question:

    def __init__(self):
        self._text: list[str] = []
        self._mark: float = 1
        self._answer: str = ""
        self._type: QuestionVarities = QuestionVarities.SINGLE_CHOICE
        self._choices: list[QuestionChoice] = []

    def getType(self):
        if len(self._choices):
            return QuestionVarities.SINGLE_CHOICE

        return (QuestionVarities.FILL_IN_BLANK if self._answer 
                else QuestionVarities.THEORY)
    

    def process(self):
        self._extractAnswerMark()
        self._extractChoice()

        return QuestionData(
            type=self.getType(),
            content="".join(self._text),
            answer=self._answer,
            mark=self._mark,
            choices=self._choices
        )
        

    def appendText(self, text: str):
        self._text.append(text) 


    def _extractChoice(self):
        option_start = list(filter(lambda x: x.startswith("(a) "), self._text))

        if not len(option_start):
            return

        last_index = self._text.index(option_start[len(option_start) - 1])

        for  i in range(last_index, len(self._text)):
            text = self._text[i].replace("\n", "").split(" ")

            if len(text) > 1:
                self._choices.append(QuestionChoice(
                    label=text[0].replace(r"(", "").replace(")", "").strip(),
                    text=" ".join(text[1:]).strip().replace("\n", "")
                ))

        del self._text[last_index:]


    def _extractAnswerMark(self):
        iter = len(self._text)
        index: list[int] = []

        for line in self._text[::-1]:
            iter -= 1
            if line.startswith("mark") or line.startswith("answer"):
                l = line.split(" ")
                if line.startswith("mark"):
                    self._mark = float(l[1].strip().replace("\n", "") or "1")
                    index.append(iter)            
                elif line.startswith("answer"):
                    self._answer = l[1].strip().replace("\n", "")
                    index.append(iter)

        self._clearTextRange(index)


    def _clearTextRange(self, range: list[int]):
        for i in range:
            del self._text[i:i+1]


    def __str__(self):
        return "".join(self._text)




class QuestionParser:

    def __init__(self, filePath: str):
        self.filePath = filePath


    def parse(self):
        try:
            document = Document(self.filePath)
        except Exception as e:
            return QuestionParserResult(
                success=False,
                exception=f"Unable to import Document: {str(e)}"
            )


        questions: list[Question] = []

        for _, paragraph in enumerate(document.paragraphs):
            p = ParagraphParser(paragraph.text)

            text = p.getText().lower().strip()

            if text == "question":
                questions.append(Question())
                continue

            if not len(questions):
                continue

            questions[len(questions) - 1].appendText(text + "\n")

        parsed_questions = [q.process() for q in questions]

        validator = QuestionValidator(parsed_questions).validate()

        return QuestionParserResult(
            success=len(validator) == 0,
            exception="",
            errors=validator,
            questions=parsed_questions
        )
            