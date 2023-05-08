import datetime
import random
import re

from drawingstate import DrawingState
import error_msg
from lsystem_exceptions import *

class LSystem:
    def __init__(self, data):
        self.data = data
        self.baseconfig_keys = ["variables","constants","axiom","rules"]
        self.drawconfig_key = "translations"
        self.stack = []

        self.configure()

    def configure(self):
        # Base
        self.validate_baseconfig()
        self.set_attributes({key: self.data[key] for key in self.baseconfig_keys})
        self.alphabet = set(self.variables).union(set(self.constants))

        # Drawing
        if self.drawconfig_key in self.data:
            self.validate_drawconfig()
            self.set_attributes({self.drawconfig_key : self.data[self.drawconfig_key]})

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
        translations = self.data.get(self.drawconfig_key)

        if not (isinstance(translations, dict) and all((isinstance(key, str) and isinstance(value, str)) for key, value in translations.items())):
            raise TypeError(error_msg.invalid_translations_type)
        
        for operation in translations.values():
            if operation in ["nop","push","pop"]:
                continue
            
            parameters = operation.split(" ")[1:]
            operation = operation.split(" ")[0]

            if operation in ["angle","forward","draw"]:
                if not (len(parameters) == 1 and self.is_numeric(parameters[0])):
                    raise UnsupportedTranslationError(error_msg.unsupported_translations)
            elif operation == "color":
                if not ((len(parameters) == 1 and self.is_color(parameters[0])) or (len(parameters) == 3 and self.is_color(parameters[-3:]))):
                    raise UnsupportedTranslationError
            else:
                raise UnsupportedTranslationError(error_msg.unsupported_translations)
        
        if set(translations.keys()) != set(self.alphabet):
            raise TranslationSymbolMismatchError(error_msg.translations_false_one_to_one_correspondence_with_vars_and_consts)
    
    def is_numeric(self, string):
        try:
            float(string)
            return True
        except ValueError:
            return False

    def is_color(self, color):
        if isinstance(color, str):
            colors_str = ["red", "orange", "yellow", "green", "blue", "purple", "pink", "brown", "black", "gray", "white"]
            hexadec_pattern = r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
            return (color in colors_str or bool(re.match(hexadec_pattern, color))) 
        elif isinstance(color, list):
            return all((self.is_numeric(value) and 0 <= int(value) <= 255) for value in color)
        return False

    def set_attributes(self, data):
        for key, value in data.items():
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

    def draw(self, turtle, parameter):
        turtle.forward(float(parameter))

    def forward(self, turtle, parameter):
        turtle.penup()
        turtle.forward(float(parameter))
        turtle.pendown()

    def angle(self, turtle, parameter):
        turtle.right(float(parameter))

    def color(self, turtle, parameter):
        if " " in parameter:
            turtle.pencolor(*[int(x)/255 for x in parameter.split(" ")])
        else:
            turtle.pencolor(parameter)

    def push(self, turtle, _):
        self.stack.append(DrawingState(x=turtle.xcor(), y=turtle.ycor(), angle=turtle.heading()))

    def pop(self, turtle, _):
        drawing_state = self.stack.pop()
        turtle.penup()
        turtle.setpos(drawing_state.x, drawing_state.y)
        turtle.setheading(drawing_state.angle)
        turtle.pendown()

    def nop(*args):
        pass

    def render(self, string, turtle):
        if hasattr(self, self.drawconfig_key):
            for symbol in string:
                operation = self.translations[symbol]
                if " " in operation:
                    parameter = operation.split(" ", 1)[1]
                    operation =  operation.split(" ")[0]
                method = getattr(self, operation)
                method(turtle, parameter)
        else:
            raise AttributeError("LSystem is not drawable. Define 'translations' in configuration file.")