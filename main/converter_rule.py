class ConverterRule:
    expression = ""

    def __init__(self, convert_expression):
        self.expression = convert_expression

    def get_expression(self):
        return self.expression