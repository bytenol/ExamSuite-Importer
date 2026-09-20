from examsuite_importer.question.QuestionParser import QuestionParser



if __name__ == "__main__":
    parser = QuestionParser("/home/user/Documents/Programming/ByteNol/ExamSuite-Importer/scratch/question_test.docx")
    parser.parse()