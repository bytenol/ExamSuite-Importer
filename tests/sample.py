from examsuite_importer.parser.document_parser import DocumentParser


if __name__ == "__main__":
    parser = DocumentParser("./scratch/mathematics_ss1_a.docx").parse()
    print(parser)
