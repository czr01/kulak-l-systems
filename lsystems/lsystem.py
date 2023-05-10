import datetime
import random
import re
import os
from turtle import Turtle

from drawingstate import DrawingState
from error import *

class LSysConfigError(Exception):
    pass

class NoVariablesDefinedError(LSysConfigError):
    pass

class FixedAxiomError(LSysConfigError):
    pass

class VariableConstantOverlapError(LSysConfigError):
    pass

class AxiomWithUndefinedSymbolErrror(LSysConfigError):
    pass

class RulesVariablesMismatchError(LSysConfigError):
    pass

class UndefinedSymbolInRuleOutputError(LSysConfigError):
    pass

class TranslationAlphabetMismatchError(LSysConfigError):
    pass

class UnsupportedTranslationError(LSysConfigError):
    pass

"""
    A class representing an L-System.
"""
class LSystem:

    app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../app'))
    history_file = os.path.join(app_dir, 'history.txt')

    def __init__(self, data):
        """
        Initializes a new L-System object with the given data.

        :param data: Description of L-System (dict)
        """

        self.data = data
        self.baseconfig_keys = ["variables","constants","axiom","rules"]
        self.drawconfig_key = "translations"
        self.default_width = 1
        self.stack = []

        self.configure()

    def configure(self):
        """
        Validifies and sets L-System attributes.
        """

        # Base configuration
        self.validate_baseconfig()
        self.set_attributes({key: self.data[key] for key in self.baseconfig_keys})
        self.alphabet = set(self.variables).union(set(self.constants))

        # Drawing configuration
        if self.drawconfig_key in self.data:
            self.validate_drawconfig()
            self.set_attributes({self.drawconfig_key : self.data[self.drawconfig_key], "width" : self.data["width"]})

        self.data = None

    def validate_baseconfig(self):
        """
        Validifies base configuration attributes
        """

        # Checks if all required fields for instantiation are present in self.data dictionary.
        if not all(entry in self.data for entry in self.baseconfig_keys):
            raise KeyError(MISSING_BASE_FIELDS)

        # Get variables, constants, axiom and rules from self.data dictionary.
        variables = self.data.get("variables")
        constants = self.data.get("constants")
        axiom = self.data.get("axiom")
        rules = self.data.get("rules")
        alphabet = set(variables).union(set(constants))

        # Check if variables is a list of strings.
        if not (isinstance(variables, list) and all(isinstance(var, str) for var in variables)):
            raise TypeError(INVALID_VARIABLES_TYPE)

        # Check if constants is a list of strings.
        if not (isinstance(constants, list) and all(isinstance(const, str) for const in constants)):
            raise TypeError(INVALID_CONSTANTS_TYPE)

        # Check if axiom is a string.
        if not isinstance(axiom, str):
            raise TypeError(INVALID_AXIOM_TYPE)

        # Check if rules is a dictionary.
        if not isinstance(rules, dict):
            raise TypeError(INVALID_RULES_TYPE)
        
        # Check if each rule key is a string, and each value is either a string or a list of (float, string) tuples.
        for key, value in rules.items():
            if not isinstance(key, str):
                raise TypeError(INVALID_RULES_TYPE)
            if not isinstance(value, str):
                if not isinstance(value, list):
                    raise TypeError(INVALID_RULES_TYPE)
                else:
                    for item in value:
                        if not isinstance(item, list) or len(item) != 2 or not self.__is_numeric(item[0]) or not isinstance(item[1], str):
                            raise TypeError(INVALID_RULES_TYPE)

        # Check if variables list is not empty
        if len(variables) == 0:
            raise NoVariablesDefinedError(MISSING_VARIABLE)
        
        # Check if all symbols in axiom are defined in the alphabet
        if not set(axiom).issubset(alphabet):
            raise AxiomWithUndefinedSymbolErrror(AXIOM_UNDEFINED_SYMBOL)
        
        # Check if at least one symbol from axiom is in variables
        if not any(symbol in variables for symbol in axiom):
            raise FixedAxiomError(AXIOM_MISSING_VARIABLE)

        # Check if each variable has a corresponding rule
        if set(rules.keys()) != set(variables):
            raise RulesVariablesMismatchError(RULES_VARIABLES_MISMATCH)
        
        # Check if all symbols in the rule outputs are defined in the alphabet
        for value in rules.values():
            if isinstance(value, str):
                if not set(value).issubset(alphabet):
                    raise UndefinedSymbolInRuleOutputError(RULES_UNDEFINED_REPRODUCTION)
            elif isinstance(value, list):
                for outcome in value:
                    if not set(outcome[1]).issubset(alphabet):
                        raise UndefinedSymbolInRuleOutputError(RULES_UNDEFINED_REPRODUCTION)

        # Check if variables and constants have no overlapping symbols
        if not set(variables).isdisjoint(constants):
            raise VariableConstantOverlapError(VARIABLES_CONSTANTS_OVERLAP)

    def validate_drawconfig(self):
        """
        Validifies drawing configuration attributes
        """

        # Get the translations from the self.data dictionary.
        translations = self.data.get("translations")

        # Check if translations is a dictionary with string key-value pairs.
        if not (isinstance(translations, dict) and all((isinstance(key, str) and isinstance(value, str)) for key, value in translations.items())):
            raise TypeError(INVALID_TRANSLATIONS_TYPE)  
        
        # Check if optional width parameter is numerical.
        if "width" in self.data:
            if not self.__is_pos_int(self.data["width"]):
                raise TypeError(INVALID_WIDTH_TYPE)
        else:
            self.data["width"] = self.default_width

        # Check if translations are supported.
        for operation in translations.values():
            if operation.split(" ")[0] in ["nop","push","pop","angle","forward","draw","color"]:
                if operation in ["nop","push","pop"]:
                    continue
                
                if len(operation.split(" ",1)) != 2: 
                    raise UnsupportedTranslationError(UNSUPPORTED_TRANSLATION + f" '{operation}'")
                
                parameter = operation.split(" ", 1)[1]
                operation = operation.split(" ")[0]

                if operation in ["angle","forward","draw"]:
                    if not (self.__is_numeric(parameter)):
                        raise UnsupportedTranslationError(UNSUPPORTED_TRANSLATION + f" '{operation} {parameter}'")
                elif operation == "color":
                    if not (self.__is_color(parameter)):
                        raise UnsupportedTranslationError(UNSUPPORTED_TRANSLATION + f" '{operation} {parameter}'")
            else:
                raise UnsupportedTranslationError(UNSUPPORTED_TRANSLATION + f" '{operation}'")
        
        # Check if each variable has a corresponding translation.
        if set(translations.keys()) != self.alphabet:
            raise TranslationAlphabetMismatchError(TRANSLATIONS_ALPHABET_MISMATCH)
    
    def __is_numeric(self, n):
        try:
            float(n)
            return True
        except ValueError:
            return False
        
    def __is_pos_int(self, n):
        try:
            int(n)
            return int(n) > 0
        except ValueError:
            return False 

    def __is_color(self, color):
        colors_str = ["red", "orange", "yellow", "green", "blue", "purple", "pink", "brown", "black", "gray", "white"]
        hexadec_pattern = r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"

        # String
        if color in colors_str:
            return True
        
        # Hexadecimal
        if bool(re.match(hexadec_pattern, color)):
            return True
        
        # RGB
        if len(color.split(" ")) == 3:
            if all((self.__is_numeric(value) and 0 <= int(value) <= 255) for value in color.split(" ")):
                return True
        
        return False

    def set_attributes(self, data):
        for key, value in data.items():
            setattr(self, key, value)

    def process(self, iterations):
        """
        Applies reproduction rules to axiom a given amount of times.

        :param iterations: Number of iteratations to perform (int)
        :return current: Iterated L-System string
        """

        if not self.__is_pos_int(iterations):
            raise ValueError("Unvalid number of iterations.")

        current = self.axiom
        for _ in range(int(iterations)):
            next = ""
            for symbol in current:
                if symbol in self.rules:
                    expansion = self.rules[symbol]
                    if isinstance(expansion, str):
                        next += expansion
                    elif isinstance(expansion, list):
                        weights, outcomes = zip(*expansion)
                        next += random.choices(outcomes, weights=[float(w) for w in weights], k=1)[0]
                else:
                    next += symbol
            current = next
        self.__log(iterations, current)
        return current

    def __log(self, iterations, string):
        """
        Logs processed (drawable) L-Systems to a history.txt file.
        """
        if hasattr(self, self.drawconfig_key):
            logging_message = f"{datetime.datetime.now()}\t{', '.join(self.variables)}\t{', '.join(self.constants)}\t{self.axiom}\t{', '.join([f'{key} -> {value}' for key, value in self.rules.items()])}\t{', '.join([f'{key} : {value}' for key, value in self.translations.items()])}\t{iterations}\t{string}\n"
            with open(LSystem.history_file,'a') as f:
                f.write(logging_message)
        #else: Alternate logging message

    def render(self, string, turtle):
        """
        Renders L-System using turtle graphics.

        :param string: Interpretable L-System instructions string
        :param turtle: Turtle object to draw with.
        """
        if not hasattr(self, self.drawconfig_key):
            raise AttributeError("L-System is not drawable. Define 'translations' in configuration file.")
        if not set(string).issubset(self.alphabet):
            raise ValueError(f"Non-interpretable L-System instructions string '{string}'.")
        if not isinstance(turtle, Turtle):
            raise ValueError(f"Unable to draw L-Sytem using {type(turtle)}. Expected Turtle object.")
        
        turtle.width(int(self.width))
        turtle.showturtle()
        for symbol in string:
            operation = self.translations[symbol]
            if " " in operation:
                parameter = operation.split(" ", 1)[1]
                operation =  operation.split(" ")[0]
            method = getattr(self, operation)
            method(turtle, parameter)  
        turtle.hideturtle()
    
    def draw(self, turtle, length):
        """
        Draws a line with given length.

        :param turtle: Turtle object to draw with
        :param length: Distance to move the turtle forward (float)
        """
        turtle.forward(float(length))

    def forward(self, turtle, length):
        """
        Moves turtle forward by given length without drawing a line.

        :param turtle: Turtle object to draw with
        :param length: Distance to move the turtle forward (float)
        """
        turtle.penup()
        turtle.forward(float(length))
        turtle.pendown()

    def angle(self, turtle, angle):
        """
        Rotates the turtle by a given angle to the left.
        
        :param turtle: Turtle object to rotate
        :param angle: Angle to rotate the turtle by (float)
        """
        turtle.left(float(angle))

    def color(self, turtle, color):
        """
        Sets the pen color of the turtle to given color.

        :param turtle: Turtle object to set pen color for
        """
        if " " in color:
            turtle.pencolor(*[int(x)/255 for x in color.split(" ")])
        else:
            turtle.pencolor(color)

    def push(self, turtle, _):
        """
        Pushes drawing state on stack.

        :param turtle: Turtle object to get drawing state from.
        """
        self.stack.append(DrawingState(x=turtle.xcor(), y=turtle.ycor(), angle=turtle.heading(), color=turtle.pencolor()))

    def pop(self, turtle, _):
        """
        Pops drawing state from stack.

        :param turtle: Turtle object to set drawing state to.
        """
        drawing_state = self.stack.pop()
        turtle.penup()
        turtle.setpos(drawing_state.x, drawing_state.y)
        turtle.setheading(drawing_state.angle)
        turtle.pencolor(drawing_state.color)
        turtle.pendown()

    def nop(*args):
        """
        Do nothing.
        """
        pass