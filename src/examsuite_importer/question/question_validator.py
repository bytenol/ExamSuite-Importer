from examsuite_importer.question.question_types import QuestionChoice, QuestionData, QuestionValidatorError, QuestionVarities


class QuestionValidator:


    def __init__(self, questions: list[QuestionData]):
        self._questions = questions
        self._error: list[QuestionValidatorError] = []


    def validate(self):
        for question in self._questions:
            cn = self._validateContent(question.content)
            ch = self._validateChoice(question.choices)
            an = self._validateAnswer(question.answer)
            mk = self._validateMark(question.mark)
            ty = self._validateType(question.type)
             
    
        return cn and ch and an and mk and ty 



    def _validateType(self, type: QuestionVarities):
        return True 
    

    def _validateMark(self, mark: float):

        return True 

    def _validateAnswer(self, answer: str):
        return True 
    

    def _validateContent(self, content: str):
        return True 


    def _validateChoice(self, choices: list[QuestionChoice]):
        for choice in choices:
            pass 

        return True 