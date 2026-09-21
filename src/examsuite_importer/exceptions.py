class InvalidFileNameError(Exception):
    """Raised when the docx file naming does not match the required convention
    The convention is subject_class_section
    """


class ExamSuiteImporterError(Exception):
    """Base exception for ExamSuite Importer."""


class DocumentImportError(ExamSuiteImporterError):
    """Raised when a DOCX document cannot be opened or read."""


class QuestionParseError(ExamSuiteImporterError):
    """Raised when a question cannot be parsed."""


class EquationParseError(ExamSuiteImporterError):
    """Raised when a Word equation cannot be converted."""
