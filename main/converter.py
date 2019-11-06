import sys
import numpy
from converter_rule import ConverterRule


class Converter:
    def __init__(self, type_name: str, converter_rule: ConverterRule):
        self.converter_rule = converter_rule
        self.type_name = type_name

    def convert(self, value):
        expressions_tuples_list: list = self.__parse__expression__()
        ret_val = None
        if expressions_tuples_list:
            for expression_split in expressions_tuples_list:
                val = eval(expression_split[0])
                if isinstance(value, str):
                    value = eval(value)

                if isinstance(val, str):
                    ret_val = eval(expression_split[1])
                elif isinstance(val, range) or isinstance(val, numpy.ndarray):
                    if value in val:
                        ret_val = eval(expression_split[1])
                    else:
                        ret_val = False
            return ret_val
        else:
            print("None received as iterable, isnt doable.")

    def __parse__expression__(self):
        if self.converter_rule:
            expression_str: str = self.converter_rule.get_expression()
            expression_list: list = expression_str.split(";")
            expresion_tuples_list = list()

            for expression in expression_list:
                expression_split = str(expression).split(":")
                expresion_tuples_list.append(expression_split)

            return expresion_tuples_list
        else:
            print("converter rule is None!")
            return None