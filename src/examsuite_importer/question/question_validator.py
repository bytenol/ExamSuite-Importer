from examsuite_importer.question.question_types import QuestionChoice, QuestionData, QuestionValidatorError, QuestionVarities


class QuestionValidator:


    def __init__(self, questions: list[QuestionData]):
        self._questions = questions
        self._error: list[QuestionValidatorError] = []


    def validate(self):
        iter = 0
        for question in self._questions:
            iter += 1
            content=question.content[:30]

            if not question.answer and not question.type == QuestionVarities.THEORY:
                self._error.append(
                    QuestionValidatorError(
                        line=iter,
                        content=content,
                        message="Answer must be provided for this question"
                    )
                )
                continue 

            if question.type == QuestionVarities.SINGLE_CHOICE:
                # single choice question expects just a character as an answer 
                if len(question.answer) != 1 or not question.answer in "abcd":
                    self._error.append(
                        QuestionValidatorError(
                            line=iter,
                            content=content,
                            message="Answer to a SingleChoice Question must be a single character 'a','b','c','d'"
                        )
                    )

                    continue    

                if len(question.choices) != 4:
                    self._error.append(
                        QuestionValidatorError(
                            line=iter,
                            content=content,
                            message="SingleChoice Question must provide 4 options"
                        )
                    )
                    continue 

        return self._error