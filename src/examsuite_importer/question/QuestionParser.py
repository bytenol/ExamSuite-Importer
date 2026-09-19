from io import StringIO

from docx import Document

from examsuite_importer.question.question_types import QuestionParserError


class QuestionParser:

    def __init__(self, filePath: str):
        self.filePath = filePath


    def _openDocument(self):
        document = Document(self.filePath)


    def run(self):
        try:
            document = Document(self.filePath)
        except Exception as e:
            return QuestionParserError(error="Unable to import docx")

        print(document)