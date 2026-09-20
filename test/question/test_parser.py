from examsuite_importer.question.QuestionParser import QuestionParser




def test_parser_creation():
    parser = QuestionParser("./scratch/question_test.docx")
    parsed = parser.parse()
    assert parsed.success == True
    assert parsed.errors == []
    assert parsed.exception.strip() == ""



def test_parser_exception():
    parser = QuestionParser("./scratch/question_ttest.docx")
    parsed = parser.parse()

    assert parsed.success == False 
    assert parsed.errors == []
    assert parsed.exception.strip() != ""