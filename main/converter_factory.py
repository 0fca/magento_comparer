from converter import Converter


class TypeConverterFactory:
    def create(self, type_name, converter_rule):
        self.converter_rule = converter_rule
        self.type_name = type_name
        converter = Converter(type_name, converter_rule)
        return converter

    def get_type_name(self):
        return self.type_name

    def get_converter_rule(self):
        return self.converter_rule
