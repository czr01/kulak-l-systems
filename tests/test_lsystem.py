import string
import tempfile
import json
from copy import deepcopy

import pytest

from pylrender.main import *

regular_lsystem_description = {
    "variables" : ["F","G"],
    "constants" : ["+","X"],
    "axiom" : "F",
    "rules" : {
        "F"  : "F+FG",
        "G"  : "FX"
    },
    "translations" : {
        "F" : "draw 10",
        "G" : "forward 10",
        "+" : "angle 90",
        "X" : "color red"
    },
    "width" : 5
}

def get_lsys_description():
    return deepcopy(regular_lsystem_description)
    
def defined_symb(lsys_data, i):
    """
    Returns defined symbol in L-System alphabet.

    :param lsys_data: L-System description (dict)
    :param i: index
    :return: Defined L-System symbol at index i
    """
    alphabet = lsys_data["variables"] + lsys_data["constants"]
    return alphabet[i]

def undefined_symb(lsys_data):
    """
    Returns undefined symbol in L-System.

    :param lsys_data: L-System description (dict)
    :return: Undefined L-System symbol
    """
    for ch in string.ascii_letters + string.punctuation:
        if ch not in [lsys_data["variables"] + lsys_data["constants"]]:
            return ch

@pytest.fixture
def setup_file():
    temp_file_path = None

    def create_file(data):
        nonlocal temp_file_path
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".json") as tmp:
            json.dump(data, tmp)
            tmp.close()
            temp_file_path = tmp.name
            return tmp.name
    
    yield create_file

## Test Suite

def test_missing_required_field(setup_file):
    """
    Test that a missing required field (variables, constants, axiom, rules) raises a KeyError.
    """
    data = get_lsys_description()
    del data["axiom"]
    file = setup_file(data)
    with pytest.raises(KeyError):
        LSysConfigFileParser.parse(file)

def test_invalid_variables(setup_file):
    """
    Test that invalid L-System variables value type returns TypeError. Expected list of string entries.
    """
    data = get_lsys_description()
    data["variables"] = "F"
    file = setup_file(data)
    with pytest.raises(TypeError):
        LSysConfigFileParser.parse(file)

def test_invalid_constants(setup_file):
    """
    Test that invalid L-System constants value type returns TypeError. Expected list of string entries.
    """
    data = get_lsys_description()
    data["constants"] = [23,1,18]
    file = setup_file(data)
    with pytest.raises(TypeError):
        LSysConfigFileParser.parse(file)

def test_invalid_axiom(setup_file):
    """
    Test that invalid L-System axiom value type returns TypeError. Expected string.
    """
    data = get_lsys_description()
    data["axiom"] = 5
    file = setup_file(data)
    with pytest.raises(TypeError):
        LSysConfigFileParser.parse(file)

def test_invalid_rules(setup_file):
    """
    Test that invalid L-System rules value type returns TypeError. Expected dict.
    """
    data = get_lsys_description()
    data["rules"] = "ABA"
    file = setup_file(data)
    with pytest.raises(TypeError):
        LSysConfigFileParser.parse(file)

def test_invalid_rules(setup_file):
    """
    Test that invalid L-System rules value type returns TypeError. Expected dict of string:string entries.
    """
    data = get_lsys_description()
    data["rules"] = {
        defined_symb(data,0) : 50
    }
    file = setup_file(data)
    with pytest.raises(TypeError):
        LSysConfigFileParser.parse(file)

def test_invalid_stochastic1(setup_file):
    """
    Test that invalid L-System stochastic rules value type returns TypeError. Expected dict of string:list entries with dict values as list of lists with
    exclusively 2 values: float and string.
    """
    data = get_lsys_description()
    data["rules"]["key1"] = [["some_string", "ABA"]]
    file = setup_file(data)
    with pytest.raises(TypeError):
        LSysConfigFileParser.parse(file)

def test_invalid_stochastic2(setup_file):
    """
    Test that invalid L-System stochastic rules value type returns TypeError. Expected dict of string:list entries with dict values as list of lists with
    exclusively 2 values: float and string.
    """
    data = get_lsys_description()
    data["rules"]["key1"] = [[25, "ABA", " "]]
    file = setup_file(data)
    with pytest.raises(TypeError):
        LSysConfigFileParser.parse(file)

def test_invalid_stochastic3(setup_file):
    """
    Test that invalid L-System stochastic rules value type returns TypeError. Expected dict of string:list entries with dict values as list of lists with
    exclusively 2 values: float and string.
    """
    data = get_lsys_description()
    data["rules"]["key1"] = ["0.5", 31]
    file = setup_file(data)
    with pytest.raises(TypeError):
        LSysConfigFileParser.parse(file)

def test_valid_stochastic():
    """
    Test that valid L-System stochastic rules do not raise any Errors.
    """
    data = get_lsys_description()
    data["variables"].append("B")
    data["rules"]["B"] = [[0.5,"ABA"], [0.5,"BAB"]]

def test_invalid_translations(setup_file):
    """
    Test that invalid L-System translations value type returns TypeError. Expected dict of string:string entries.
    """
    data = get_lsys_description()
    data["translations"] = 13
    file = setup_file(data)
    with pytest.raises(TypeError):
        LSysConfigFileParser.parse(file)

def test_invalid_width(setup_file):
    """
    Test that invalid L-System width value type returns TypeError. Expected positive integer != 0.
    """
    data = get_lsys_description()
    data["width"] = -5
    file = setup_file(data)
    with pytest.raises(TypeError):
        LSysConfigFileParser.parse(file)

def test_undefined_width(setup_file):
    """
    Test that undefined L-System width value defaults to default_width.
    """
    data = get_lsys_description()
    del data["width"]
    file = setup_file(data)
    lsys = LSysConfigFileParser.parse(file)
    assert lsys.width == LSysConfigFileParser.default_width

def test_string_processing():
    """
    Test that L-System processes L-Systems and applies L-System rules correctly.
    """
    my_lsys = LSystem(variables=["A","B"], constants=[], axiom="A", rules={"A":"AB","B":"A"})
    assert my_lsys.process(4) == "ABAABABA"

def test_empty_variable_list(setup_file):
    """
    Test that empty variable list raises NoVariablesDefinedError. L-System must include variables.
    """
    data = get_lsys_description()
    data["variables"] = []
    file = setup_file(data)
    with pytest.raises(NoVariablesDefinedError):
        LSysConfigFileParser.parse(file)

def test_axiom_with_no_variable(setup_file):
    """
    Test that axiom with no variables included raises FixedAxiomError. Axiom must be reproducible.
    """
    data = get_lsys_description()
    data["axiom"] = "".join([ch for ch in data["axiom"] if ch not in data["variables"]])
    file = setup_file(data)
    with pytest.raises(FixedAxiomError):
        LSysConfigFileParser.parse(file)

def test_axiom_with_undefined_symbol(setup_file):
    """
    Test that axiom with undefined L-System symbol raisees AxiomWithUndefinedSymbolError. All symbols in axiom must be defined in L-System alphabet.
    """
    data = get_lsys_description()
    data["axiom"] += undefined_symb(data)
    file = setup_file(data)
    with pytest.raises(AxiomWithUndefinedSymbolErrror):
        LSysConfigFileParser.parse(file)

def test_variable_with_no_corresponding_rule(setup_file):
    """
    Test that variable with no appropriate reproduction rule raises RulesVariablesMismatchError. 
    There must be a one-to-one correspondence between variables and rule-keys.
    """
    data = get_lsys_description()
    data["variables"] += undefined_symb(data)
    file = setup_file(data)
    with pytest.raises(RulesVariablesMismatchError):
        LSysConfigFileParser.parse(file)

def test_rule_input_undefined_symbol(setup_file):
    """
    Test that rule-key with undefined symbol raises RulesVariablesMismatchError.
    There must be a one-to-one correspondence between variables and rule-keys.
    """
    data = get_lsys_description()
    undefined_chr = undefined_symb(data)
    data["rules"][undefined_chr] = data["constants"][0]
    file = setup_file(data)
    with pytest.raises(RulesVariablesMismatchError):
        LSysConfigFileParser.parse(file)

def test_rule_output_undefined_symbol(setup_file):
    """
    Test that undefined symbol in rule output raises UndefinedSymbolInRuleOutputError.
    """
    data = get_lsys_description()
    key = list(data["rules"].keys())[0]
    data["rules"][key] += undefined_symb(data)
    file = setup_file(data)
    with pytest.raises(UndefinedSymbolInRuleOutputError):
        LSysConfigFileParser.parse(file)

def test_symbol_with_no_corresponding_translation(setup_file):
    """
    Test that symbol with no appropriate translation raises TranslationAlphabetMismatch. 
    There must be a one-to-one correspondence between symbols and translation-keys.
    """
    data = get_lsys_description()
    data["constants"] += undefined_symb(data)
    file = setup_file(data)
    with pytest.raises(TranslationAlphabetMismatchError):
        LSysConfigFileParser.parse(file)

def test_translation_with_undefined_symbol(setup_file):
    """
    Test that translation-key with undefined symbol TranslationAlphabetMismatch. 
    There must be a one-to-one correspondence between symbols and translation-keys.
    """
    data = get_lsys_description()
    undefined_chr = undefined_symb(data)
    data["translations"][undefined_chr] = "forward 50"
    file = setup_file(data)
    with pytest.raises(TranslationAlphabetMismatchError):
        LSysConfigFileParser.parse(file)

def test_unsupported_translation_invalid_operation(setup_file):
    """
    Test that unsupported operation raises UnsupportedTranslationError.
    """
    data = get_lsys_description()
    data["translations"][defined_symb(data,0)] = "banana 25"
    file = setup_file(data)
    with pytest.raises(UnsupportedTranslationError):
        LSysConfigFileParser.parse(file)

def test_unsupported_translation_invalid_parameter(setup_file):
    """
    Test that invalid parameter raises UnsupportedTranslationError. Angle-operation expects numeric value.
    """
    data = get_lsys_description()
    data["translations"][defined_symb(data,0)] = "angle pineapple"
    file = setup_file(data)
    with pytest.raises(UnsupportedTranslationError):
        LSysConfigFileParser.parse(file)

def test_unsupported_translation_missing_parameter(setup_file):
    """
    Test that missing parameter raises UnsupportedTranslationError. Draw-operation expects parameter.
    """
    data = get_lsys_description()
    data["translations"][defined_symb(data,0)] = "draw"
    file = setup_file(data)
    with pytest.raises(UnsupportedTranslationError):
        LSysConfigFileParser.parse(file)

def test_unsupported_translation_parameter_invalid_rgb(setup_file):
    """
    Test that invalid RGB-value as color-parameter raises UnsupportedTranslationError.
    """
    data = get_lsys_description()
    data["translations"][defined_symb(data,0)] = "color 348 -12 25"
    file = setup_file(data)
    with pytest.raises(UnsupportedTranslationError):
        LSysConfigFileParser.parse(file)

def test_unsupported_translation_parameter_invalid_hex(setup_file):
    """
    Test that invalid hexadecimal as color-parameter raises UnsupportedTranslationError.
    """
    data = get_lsys_description()
    data["translations"][defined_symb(data,0)] = "color #GGG"
    file = setup_file(data)
    with pytest.raises(UnsupportedTranslationError):
        LSysConfigFileParser.parse(file)

def test_unsupported_translation_parameter_invalid_color_string(setup_file):
    """
    Test that invalid color string as color parameter raises UnsupportedTranslationError.
    """
    data = get_lsys_description()
    data["translations"][defined_symb(data,0)] = "color appelblauwzeegroen"
    file = setup_file(data)
    with pytest.raises(UnsupportedTranslationError):
        LSysConfigFileParser.parse(file)

def test_valid_color(setup_file):
    """
    Test that valid color parameters do not raise any Errors.
    """
    data = get_lsys_description()
    data["translations"][defined_symb(data,0)] = "color 255 0 13"
    data["translations"][defined_symb(data,1)] = "color #E0E000"
    data["translations"][defined_symb(data,2)] = "color blue"
    file = setup_file(data)
    LSysConfigFileParser.parse(file)

def test_overlapping_variables_and_constants(setup_file):
    """
    Test that overlapping variables and constants raise VariableConstantOverlapError. Variables and Constants must be disjoint.
    """
    data = get_lsys_description()
    data["constants"] += data["variables"] 
    file = setup_file(data)
    with pytest.raises(VariableConstantOverlapError):
        LSysConfigFileParser.parse(file)


'''
def test_render_with_invalid_turtle(setup_file)    
    """
    Test that calling .render() method on L-System without passing proper Turtle() object as argument raises ValueError.
    """
    lsys = LSystem(data)
    iterated_string = lsys.process(2)
    file = setup_file(data)
    with pytest.raises(ValueError):
        lsys.render(iterated_string, "z")

def test_invalid_process_iterations(setup)    
    """
    Test that calling .process() method without passing proper iterations argument raises ValueError.
    Iterations must be a positive integer != 0.
    """
    lsys = LSystem(lsystem_data)
    file = setup_file(data)
    with pytest.raises(ValueError):
        lsys.process(-19)

# Tests below include the Turtle graphics module, which rely on a graphical user interface
# and thus won't work with CI pipeline test environment which do not have access to a graphical
# interface. Instead the turtle argument will me mocked. This only works because validity of 
# turtle parameter is last condition to be checked.

def test_render_non_drawable_system_translations(setup):
    """
    Test that calling .render method on L-System with no translations defined raises AttributeError.
    """
    del lsystem_data["translations"]
    lsys = LSystem(lsystem_data)
    iterated_string = lsys.process(2)
    file = setup_file(data)
    with pytest.raises(AttributeError):
        lsys.render(iterated_string, "Turtle()")

def test_render_with_invalid_instructions_string():  
    """
    Test that calling .render() method on L-System without passing valid iterated string as argument raises ValueError.
    Iterated string must be interpretable by L-System defined translations and so must be subset of L-System alphabet.
    """
    lsys = LSystem(lsystem_data)
    file = setup_file(data)
    with pytest.raises(ValueError):
        lsys.render(undefined_symb(lsystem_data), "Turtle()")
'''
