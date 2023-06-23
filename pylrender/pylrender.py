#! /usr/bin/env python3

import sys
import os
import datetime
import random
from turtle import Turtle, Screen
import json

from utils import *

HISTORY_PATH = os.path.join(os.path.dirname(__file__), '../app/history.txt')

class PyLRender:
    def __init__(self) -> None:
        # Check for export option
        export_filename = None
        if len(sys.argv) == 3 and sys.argv[1] == '--export':
            export_filename = sys.argv[2]
        elif len(sys.argv) != 1:
            print('Usage: python3 PyLRender [--export <filename>]')
            return

        filename = input("Name of file containing l-system description: ")
        iterations = int(input("Number of iterations: "))
        
        # Create and process L-System
        lsystem = LSysConfigFileParser.parse(filename)
        lsys_string = lsystem.process(iterations)
        
        # Render L-System using Turtle graphics
        turtle = Turtle()
        lsysrenderer = LSystemRenderer(lsystem, turtle)
        lsysrenderer.render(lsys_string)

        # Export image if specified
        if export_filename: 
            PyLRender.export_image(Screen(), export_filename)

    @staticmethod
    def export_image(screen, export_filename):
        import io
        from PIL import Image
        screenshot = screen.getcanvas().postscript()
        image = Image.open(io.BytesIO(screenshot.encode('utf-8')))
        image.save(export_filename)

BASE_CONFIG_KEYS = {"variables","constants","axiom","rules"}
DEFAULT_WIDTH = 1
SUPPORTED_OPERATIONS = ["nop","push","pop","angle","forward","draw","color"]
NON_PARAMETERIZED_OPERATIONS = ["nop", "push", "pop"]
SINGLE_NUMERIC_PARAMETER_OPERATIONS = ["angle", "forward", "draw"]
COLOR_OPERATION = "color"
SUPPORTED_COLOUR_STRINGS = ["red", "orange", "yellow", "green", "blue", "purple", "pink", "brown", "black", "gray", "white"]

class LSysConfigFileParser():
    @staticmethod
    def parse(filename):
        data = LSysConfigFileParser.load_lsystem_data_from_file(filename)
        variables, constants, axiom, rules = LSysConfigFileParser.base_config(data)
        translations, width = LSysConfigFileParser.draw_config(data)
        return LSystem(variables, constants, axiom, rules, translations, width)

    @staticmethod
    def load_lsystem_data_from_file(filename):
        """
        Load L-System data from JSON file.

        :param filename: Filename to load L-System data from.
        :return: Dictionary containing L-System loaded from file. 
        """
        if not filename.endswith(".json"):
            raise ValueError(".json file required.")
        with open(filename,'r') as f:
            return json.load(f)

    @staticmethod
    def base_config(data):
        """
        Validifies base configuration attributes
        """

        # Checks if all required fields for instantiation are present in data dictionary.
        if not BASE_CONFIG_KEYS.issubset(set(data.keys())):
            raise KeyError(MISSING_BASE_FIELDS)
        
        variables = data.get("variables")
        constants = data.get("constants")
        axiom = data.get("axiom")
        rules = data.get("rules")
        alphabet = set(variables).union(set(constants))

        # Check if variables is a list of strings.
        if not (isinstance(variables, list) and all(isinstance(var, str) for var in variables)):
            raise TypeError(INVALID_VARIABLES_TYPE)

        # Check if constants is a list of strings.
        if not (isinstance(constants, list) and all(isinstance(const, str) for const in constants)):
            raise TypeError(INVALID_CONSTANTS_TYPE)

        variables = list(set(variables))
        constants = list(set(constants))

        # Check if axiom is a string.
        if not isinstance(axiom, str):
            raise TypeError(INVALID_AXIOM_TYPE)

        # Check if rules is a dictionary.
        if not isinstance(rules, dict):
            raise TypeError(INVALID_RULES_TYPE)
        
        # Check if each rule key is a string, and each value is either a string or a list of (float, string) tuples.
        for value in rules.values():
            if not isinstance(value, str):
                if not isinstance(value, list):
                    raise TypeError(INVALID_RULES_TYPE)
                else:
                    for item in value:
                        #print(value)
                        if not isinstance(item, list) or len(item) != 2 or not is_numeric(item[0]) or not isinstance(item[1], str):
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

        return variables, constants, axiom, rules

    @staticmethod
    def draw_config(data):
        """
        Validifies drawing configuration attributes
        """

        # Get the translations from the self.data dictionary.
        translations = data.get("translations")
        if translations == None:
            return None, None
        width = data.get("width") if data.get("width") != None else DEFAULT_WIDTH

        # Check if translations is a dictionary with string values.
        if not (isinstance(translations, dict) and all(isinstance(value, str) for value in translations.values())):
            raise TypeError(INVALID_TRANSLATIONS_TYPE)  

        # Check if optional width parameter is numerical.
        if not is_pos_int(width):
            raise TypeError(INVALID_WIDTH_TYPE)

        # Check if translations are supported.
        for translation in translations.values():
            operation = translation.split(" ", 1)[0]

            if not operation in SUPPORTED_OPERATIONS:
                raise UnsupportedTranslationError(UNSUPPORTED_TRANSLATION + f" '{translation}'")

            if operation in NON_PARAMETERIZED_OPERATIONS:
                continue

            if len(translation.split(" ", 1)) != 2:
                raise UnsupportedTranslationError(UNSUPPORTED_TRANSLATION + f" '{translation}'")

            parameter = translation.split(" ", 1)[1]

            if operation in SINGLE_NUMERIC_PARAMETER_OPERATIONS:
                if not (is_numeric(parameter)):
                    raise UnsupportedTranslationError(UNSUPPORTED_TRANSLATION + f" '{operation} {parameter}'")

            if operation == COLOR_OPERATION:
                if not (is_color(parameter, SUPPORTED_COLOUR_STRINGS)):
                     raise UnsupportedTranslationError(UNSUPPORTED_TRANSLATION + f" '{operation} {parameter}'")
            
        # Check if each variable has a corresponding translation.
        if set(translations.keys()) != set(data.get("variables")).union(set(data.get("constants"))):
            raise TranslationAlphabetMismatchError(TRANSLATIONS_ALPHABET_MISMATCH)

        return translations, width

"""
    A class representing an L-System.
"""
class LSystem:
    def __init__(self, variables, constants, axiom, rules, translations=None, width=None):
        """
        Initializes a new L-System object with the given data.

        :param data: Description of L-System (dict)
        """

        self.variables = variables
        self.constants = constants
        self.alphabet = set(variables).union(set(constants))
        self.axiom = axiom
        self.rules = rules
        self.translations = translations
        self.width = width

    def process(self, iterations):
        """
        Applies reproduction rules to axiom a given amount of times.

        :param iterations: Number of iteratations to perform (int)
        :return current: Iterated L-System string
        """

        if not is_pos_int(iterations):
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
        if self.translations != None:
            logging_message = "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
                datetime.datetime.now(),
                ", ".join(self.variables),
                ", ".join(self.constants),
                self.axiom,
                ", ".join([f"{key} -> {value}" for key, value in self.rules.items()]),
                ", ".join([f"{key} : {value}" for key, value in self.translations.items()]),
                iterations,
                string
            )
            with open(HISTORY_PATH,'a') as f:
                f.write(logging_message)

"""
    A class representing a DrawingState.
"""
class DrawingState:
    def __init__(self, x, y, angle, color):
        """
        Initializes a new DrawingState object.

        :param x: x-coordinate of the drawing state 
        :param y: y-coordinate of the drawing state
        :param angle: angle of the drawing state
        :param color: color of the drawing state
        """
        self.x = x
        self.y = y
        self.angle = angle
        self.color = color

class LSystemRenderer:
    def __init__(self, lsystem, turtle):
        self.lsystem = lsystem
        self.turtle = turtle
        self.stack = []

    def render(self, string):
        """
        Renders L-System using turtle graphics.

        :param string: Interpretable L-System instructions string
        """
        if not isinstance(self.lsystem, LSystem):
            raise ValueError(f"Unable to interpret L-System of type {type(self.lsystem)}. Expected LSystem object.")

        if self.lsystem.translations == None:
            raise AttributeError("L-System is not drawable. Define 'translations' in configuration file.")

        if not set(string).issubset(self.lsystem.alphabet):
            raise ValueError(f"Non-interpretable L-System instructions string '{string}'.")

        if not isinstance(self.turtle, Turtle):
            raise ValueError(f"Unable to draw L-Sytem using {type(self.turtle)}. Expected Turtle object.")

        self.turtle.width(self.lsystem.width)
        self.turtle.showturtle()

        for symbol in string:
            translation = self.lsystem.translations[symbol]
            if " " in translation:
                parameter = translation.split(" ", 1)[1]
                translation = translation.split(" ")[0]
            translation_method = getattr(self, translation)
            translation_method(parameter)
        self.turtle.hideturtle()

    def draw(self, length):
        """
        Draws a line with given length.

        :param length: Distance to move the turtle forward (float)
        """
        self.turtle.forward(float(length))

    def forward(self, length):
        """
        Moves turtle forward by given length without drawing a line.

        :param length: Distance to move the turtle forward (float)
        """
        self.turtle.penup()
        self.turtle.forward(float(length))
        self.turtle.pendown()

    def angle(self, angle):
        """
        Rotates the turtle by a given angle to the left.
        
        :param angle: Angle to rotate the turtle by (float)
        """
        self.turtle.left(float(angle))

    def color(self, color):
        """
        Sets the pen color of the turtle to given color.

        :param color: Color to change pen color to
        """
        if " " in color:
            self.turtle.pencolor(*[int(x)/255 for x in color.split(" ")])
        else:
            self.turtle.pencolor(color)

    def push(self, _):
        """
        Pushes drawing state on stack.
        """
        self.stack.append(DrawingState(
            x = self.turtle.xcor(), 
            y = self.turtle.ycor(), 
            angle = self.turtle.heading(), 
            color = self.turtle.pencolor())
            )
    
    def pop(self, _):
        """
        Pops drawing state from stack.
        """
        drawing_state = self.stack.pop()
        self.turtle.penup()
        self.turtle.setpos(drawing_state.x, drawing_state.y)
        self.turtle.setheading(drawing_state.angle)
        self.turtle.pencolor(drawing_state.color)
        self.turtle.pendown()

    def nop(self, _):
        """
        Do nothing.
        """
        pass

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

MISSING_BASE_FIELDS = "Missing base L-System configuration field(s) required for instantiation."
INVALID_VARIABLES_TYPE = "Invalid L-System variables type. Expected 'list' of 'string' entries"
INVALID_CONSTANTS_TYPE = "Invalid L-System constants type. Expected 'list' of 'string' entries"
INVALID_AXIOM_TYPE = "Invalid L-System axiom type. Expected 'string'"
INVALID_RULES_TYPE = "Invalid L-System rules type. Expected 'dict' with string:string or string:list(float, int) key-value pairs."
MISSING_VARIABLE = "Missing at least one defined variable in L-System variables."
AXIOM_UNDEFINED_SYMBOL = "Undefined symbol in L-System axiom."
AXIOM_MISSING_VARIABLE = "Missing at least one defined variable from L-System variables in L-System axiom."
RULES_VARIABLES_MISMATCH = "False one-to-one correspondence between L-System rule keys and L-System variables."
RULES_UNDEFINED_REPRODUCTION = "Undefined symbol in L-System rule reproduction values."
VARIABLES_CONSTANTS_OVERLAP = "L-System variables and L-System constants share common symbol"
INVALID_TRANSLATIONS_TYPE = "Invalid L-System translations type. Expected 'dict' with string:string key-value pairs."
TRANSLATIONS_ALPHABET_MISMATCH = "False one-to-one correspondence between L-System translation keys and L-System alphabet."
UNSUPPORTED_TRANSLATION = "Unsupported translation"
INVALID_WIDTH_TYPE = "Invalid L-System width. Expected positive integer value."