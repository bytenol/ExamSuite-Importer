from examsuite_importer.parser.document_parser import DocumentParser


if __name__ == "__main__":
    parser = DocumentParser("./scratch/question_math.docx").parse()
    print(parser)
