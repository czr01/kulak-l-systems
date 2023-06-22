#! /usr/bin/env python3

import sys
from turtle import Turtle, Screen
import json

from lsystem import LSystem
from error import *
from utils import *

def export_image(screen, export_filename):
    """
    Export the turtle graphics as an image.

    :param screen: Screen object to save image of.
    :param export_filename: Filname to export image to.
    """
    import io
    from PIL import Image
    screenshot = screen.getcanvas().postscript()
    image = Image.open(io.BytesIO(screenshot.encode('utf-8')))
    image.save(export_filename)

def main():
    """Main function for running the L-system program."""

    # Check for export option
    export_filename = None
    if len(sys.argv) == 3 and sys.argv[1] == '--export':
        export_filename = sys.argv[2]
    elif len(sys.argv) != 1:
        print('Usage: python3 lsystems [--export <filename>]')
        return

    # Load L-System data from file
    filename = input("Name of file containing l-system description: ")
    
    # Get number of iterations
    iterations = int(input("Number of iterations: "))
    
    # Create and process L-System
    lsystem = LSysConfigFileParser.parse(filename)
    lsys_string = lsystem.process(iterations)
    
    # Render L-System using Turtle graphics
    turtle = Turtle()
    lsystem.render(lsys_string, turtle)

    # Export image if specified
    if export_filename: 
        export_image(Screen(), export_filename)

class LSysConfigFileParser():
    base_configuration_keys = {"variables","constants","axiom","rules"}
    draw_configuration_key = "translations"
    default_width = 1
    supported_operations = ["nop","push","pop","angle","forward","draw","color"]
    non_parameterized_operations = ["nop", "push", "pop"]
    single_numeric_parameter_operations = ["angle", "forward", "draw"]
    color_operation = "color"

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
        if not LSysConfigFileParser.base_configuration_keys.issubset(set(data.keys())):
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
        width = data.get("width") if data.get("width") != None else LSysConfigFileParser.default_width 

        # Check if translations is a dictionary with string values.
        if not (isinstance(translations, dict) and all(isinstance(value, str) for value in translations.values())):
            raise TypeError(INVALID_TRANSLATIONS_TYPE)  

        # Check if optional width parameter is numerical.
        if not is_pos_int(width):
            raise TypeError(INVALID_WIDTH_TYPE)

        # Check if translations are supported.
        for translation in translations.values():
            operation = translation.split(" ", 1)[0]

            if not operation in LSysConfigFileParser.supported_operations:
                raise UnsupportedTranslationError(UNSUPPORTED_TRANSLATION + f" '{translation}'")

            if operation in LSysConfigFileParser.non_parameterized_operations:
                continue

            if len(translation.split(" ", 1)) != 2:
                raise UnsupportedTranslationError(UNSUPPORTED_TRANSLATION + f" '{translation}'")

            parameter = translation.split(" ", 1)[1]

            if operation in LSysConfigFileParser.single_numeric_parameter_operations:
                if not (is_numeric(parameter)):
                    raise UnsupportedTranslationError(UNSUPPORTED_TRANSLATION + f" '{operation} {parameter}'")

            if operation == LSysConfigFileParser.color_operation:
                if not (is_color(parameter)):
                     raise UnsupportedTranslationError(UNSUPPORTED_TRANSLATION + f" '{operation} {parameter}'")
            
        # Check if each variable has a corresponding translation.
        if set(translations.keys()) != set(data.get("variables")).union(set(data.get("constants"))):
            raise TranslationAlphabetMismatchError(TRANSLATIONS_ALPHABET_MISMATCH)

        return translations, width

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