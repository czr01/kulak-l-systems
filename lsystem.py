import datetime
import random

import error_msg
from lsystem_exceptions import *

class LSystem:
    def __init__(self, data):
        self.data = data
        self.baseconfig_keys = ["variables","constants","axiom","rules"]
        self.drawconfig_keys = ["translations","angle","length"]
        self.supported_translations = ["forward","draw","angle","-angle","nop"]

        self.configure()

    def configure(self):
        # Base
        self.validate_baseconfig()
        self.set_attributes({key: self.data[key] for key in self.baseconfig_keys})
        self.alphabet = set(self.variables).union(set(self.constants))

        # Drawing
        if any(entry in self.data for entry in self.drawconfig_keys):
            self.validate_drawconfig()
            self.set_attributes({key: self.data[key] for key in self.drawconfig_keys})

        self.data = None

    def validate_baseconfig(self):
        if not all(entry in self.data for entry in self.baseconfig_keys):
            raise KeyError(error_msg.missing_base_fields)

        variables = self.data.get("variables")
        constants = self.data.get("constants")
        axiom = self.data.get("axiom")
        rules = self.data.get("rules")

        alphabet = set(variables).union(set(constants))

        if not (isinstance(variables, list) and all(isinstance(var, str) for var in variables)):
            raise TypeError(error_msg.invalid_vars_type)

        if not (isinstance(constants, list) and all(isinstance(const, str) for const in constants)):
            raise TypeError(error_msg.invalid_const_type)

        if not isinstance(axiom, str):
            raise TypeError(error_msg.invalid_axiom_type)

        if not isinstance(rules, dict):
            raise TypeError(error_msg.invalid_rules_type)
        for key, value in rules.items():
            if not isinstance(key, str):
                raise TypeError(error_msg.invalid_rules_type)
            if not isinstance(value, str):
                if not isinstance(value, list):
                    raise TypeError(error_msg.invalid_rules_type)
                else:
                    for item in value:
                        if not isinstance(item, list) or len(item) != 2 or not isinstance(item[0], float) or not isinstance(item[1], str):
                            raise TypeError(error_msg.invalid_rules_type)

        if len(variables) == 0:
            raise NoVariablesDefinedError(error_msg.lsys_missing_variable)

        if not any(symbol in variables for symbol in axiom):
            raise FixedAxiomError(error_msg.axiom_missing_variable)
        
        if not set(axiom).issubset(alphabet):
            raise AxiomWithUndefinedSymbolErrror(error_msg.axiom_undefined_symbol)

        if set(rules.keys()) != set(variables):
            raise RuleVariableMismatchError(error_msg.rules_false_one_to_one_correspondence_with_vars)
        
        for value in rules.values():
            if isinstance(value, str):
                if not set(value).issubset(alphabet):
                    raise UndefinedSymbolInRuleOutputError
            elif isinstance(value, list):
                for outcome in value:
                    if not set(outcome[1]).issubset(alphabet):
                        raise UndefinedSymbolInRuleOutputError

        if not set(variables).isdisjoint(constants):
            raise VariableConstantOverlapError(error_msg.vars_const_intersection)
    
    def validate_drawconfig(self):
        if not all(entry in self.data for entry in self.drawconfig_keys):
            raise KeyError(error_msg.missing_draw_fields)

        translations = self.data.get("translations")
        angle = self.data.get("angle")
        length = self.data.get("length")

        if not (isinstance(translations, dict) and all((isinstance(key, str) and isinstance(value, str)) for key, value in translations.items())):
            raise TypeError(error_msg.invalid_translations_type)
        
        if not (isinstance(length, int) or (isinstance(length, str) and length.isnumeric())):
            raise TypeError(error_msg.invalid_length_value)
        
        if not (isinstance(angle, int) or (isinstance(angle, str) and angle.isnumeric())):
            raise TypeError(error_msg.invalid_angle_value)
        
        if set(translations.keys()) != set(self.alphabet):
            raise TranslationSymbolMismatchError(error_msg.translations_false_one_to_one_correspondence_with_vars_and_consts)

        if not set(translations.values()).issubset(set(self.supported_translations)):
            raise UnsupportedTranslationError(error_msg.unsupported_translations)
        
    def set_attributes(self, data):
        for key, value in data.items():
            if isinstance(value, str) and value.isnumeric():
                setattr(self, key, int(value))
            else:
                setattr(self, key, value)

    def process(self, iterations):
        current = self.axiom
        for _ in range(iterations):
            next = ""
            for symbol in current:
                if symbol in self.rules:
                    expansion = self.rules[symbol]
                    if isinstance(expansion, str):
                        next += expansion
                    elif isinstance(expansion, list):
                        weights, outcomes = zip(*expansion)
                        next += random.choices(outcomes, weights=weights, k=1)[0]
                else:
                    next += symbol
            current = next
        self.log(iterations, current)
        return current

    def log(self, iterations, string):
        try:
            logging_message = f"{datetime.datetime.now()}\t{', '.join(self.variables)}\t{', '.join(self.constants)}\t{self.axiom}\t{', '.join([f'{key} -> {value}' for key, value in self.rules.items()])}\t{', '.join([f'{key} : {value}' for key, value in self.translations.items()])}\t{iterations}\t{string}\n"
            with open("history.txt",'a') as f:
                f.write(logging_message)
        except AttributeError:
            pass # Alternate logging message

    def draw(self, string, turtle):
        try:
            for symbol in string:
                if symbol in self.translations:
                    operation = self.translations[symbol]
                    if operation == "draw":
                        turtle.forward(self.length)                

                    elif operation == "forward":
                        turtle.forward(self.length)
                        turtle.draw()

                    elif operation == "angle":
                        turtle.right(self.angle)

                    elif operation == "-angle":
                        turtle.right(-self.angle)

                    elif operation == "nop":
                        pass
        except AttributeError:
            print("LSystem is not drawable")