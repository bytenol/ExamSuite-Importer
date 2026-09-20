class ParagraphParser:

    def __init__(self, text: str):
        self.text = text


    def getText(self):
        return f"{self.text}"


    def __str__(self):
        return self.getText()