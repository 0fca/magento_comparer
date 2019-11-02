from converter_rule import ConverterRule

class Converter:
    type_name  = ""
    converter_rule = None

    def __init__(self, type_name : str, converter_rule : ConverterRule):
        self.converter_rules_list = converter_rule
        self.type_name = type_name

    def convert(self, value):
