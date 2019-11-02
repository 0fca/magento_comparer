from converter import Converter


class TypeConverterFactory:
    type_name = None
    converter_rules_list = None

    def create(self, type_name, converter_rule):
        converter = Converter(type_name, converter_rule)
        return converter
