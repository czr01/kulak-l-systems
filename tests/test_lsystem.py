import pytest
import string

from lsystems.lsystem import *

@pytest.fixture
def lsystem_data():
    """
    Generates basic L-System description used for testing.

    :return: L-System description (dict)
    """
    return {
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
        }
    }

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

## Test Suite

def test_missing_required_field(lsystem_data):
    """
    Test that a missing required field (variables, constants, axiom, rules) raises a KeyError.
    """
    del lsystem_data["axiom"]
    with pytest.raises(KeyError):
        LSystem(lsystem_data)

def test_invalid_variables(lsystem_data):
    """
    Test that invalid L-System variables value type returns TypeError. Expected list of string entries.
    """
    lsystem_data["variables"] = "F"
    with pytest.raises(TypeError):
        LSystem(lsystem_data)

def test_invalid_constants(lsystem_data):
    """
    Test that invalid L-System constants value type returns TypeError. Expected list of string entries.
    """
    lsystem_data["constants"] = [23,1,18]
    with pytest.raises(TypeError):
        LSystem(lsystem_data)

def test_invalid_axiom(lsystem_data):
    """
    Test that invalid L-System axiom value type returns TypeError. Expected string.
    """
    lsystem_data["axiom"] = 5
    with pytest.raises(TypeError):
        LSystem(lsystem_data)

def test_invalid_rules(lsystem_data):
    """
    Test that invalid L-System rules value type returns TypeError. Expected dict.
    """
    lsystem_data["rules"] = "ABA"
    with pytest.raises(TypeError):
        LSystem(lsystem_data)

def test_invalid_rules(lsystem_data):
    """
    Test that invalid L-System rules value type returns TypeError. Expected dict of string:string entries.
    """
    lsystem_data["rules"] = {
        defined_symb(lsystem_data,0) : 50
    }
    with pytest.raises(TypeError):
        LSystem(lsystem_data)

def test_invalid_stochastic1(lsystem_data):
    """
    Test that invalid L-System stochastic rules value type returns TypeError. Expected dict of string:list entries with dict values as list of lists with
    exclusively 2 values: float and string.
    """
    lsystem_data["rules"]["key1"] = [["some_string", "ABA"]]
    with pytest.raises(TypeError):
        LSystem(lsystem_data)

def test_invalid_stochastic2(lsystem_data):
    """
    Test that invalid L-System stochastic rules value type returns TypeError. Expected dict of string:list entries with dict values as list of lists with
    exclusively 2 values: float and string.
    """
    lsystem_data["rules"]["key1"] = [[25, "ABA", " "]]
    with pytest.raises(TypeError):
        LSystem(lsystem_data)

def test_invalid_stochastic3(lsystem_data):
    """
    Test that invalid L-System stochastic rules value type returns TypeError. Expected dict of string:list entries with dict values as list of lists with
    exclusively 2 values: float and string.
    """
    lsystem_data["rules"]["key1"] = ["0.5", 31]
    with pytest.raises(TypeError):
        LSystem(lsystem_data)

def test_valid_stochastic(lsystem_data):
    """
    Test that valid L-System stochastic rules do not raise any Errors.
    """
    lsystem_data["variables"].append("B")
    lsystem_data["rules"]["B"] = [[0.5,"ABA"], [0.5,"BAB"]]

def test_invalid_translations(lsystem_data):
    """
    Test that invalid L-System translations value type returns TypeError. Expected dict of string:string entries.
    """
    lsystem_data["translations"] = 13
    with pytest.raises(TypeError):
        LSystem(lsystem_data)

def test_invalid_width(lsystem_data):
    """
    Test that invalid L-System width value type returns TypeError. Expected positive integer != 0.
    """
    lsystem_data["width"] = -5
    with pytest.raises(TypeError):
        LSystem(lsystem_data)

def test_undefined_width(lsystem_data):
    """
    Test that undefined L-System width value defaults to default_width.
    """
    lsys = LSystem(lsystem_data)
    assert lsys.default_width == lsys.width

def test_string_processing():
    """
    Test that L-System processes L-Systems and applies L-System rules correctly.
    """
    my_lsys = LSystem({"variables":["A","B"],"constants":[],"axiom":"A","rules":{"A":"AB","B":"A"}})
    assert my_lsys.process(4) == "ABAABABA"

def test_empty_variable_list(lsystem_data):
    """
    Test that empty variable list raises NoVariablesDefinedError. L-System must include variables.
    """
    with pytest.raises(NoVariablesDefinedError):
        lsystem_data["variables"] = []
        LSystem(lsystem_data)

def test_axiom_with_no_variable(lsystem_data):
    """
    Test that axiom with no variables included raises FixedAxiomError. Axiom must be reproducible.
    """
    with pytest.raises(FixedAxiomError):
        lsystem_data["axiom"] = "".join([ch for ch in lsystem_data["axiom"] if ch not in lsystem_data["variables"]])
        LSystem(lsystem_data)

def test_axiom_with_undefined_symbol(lsystem_data):
    """
    Test that axiom with undefined L-System symbol raisees AxiomWithUndefinedSymbolError. All symbols in axiom must be defined in L-System alphabet.
    """
    with pytest.raises(AxiomWithUndefinedSymbolErrror):
        lsystem_data["axiom"] += undefined_symb(lsystem_data)
        LSystem(lsystem_data)

def test_variable_with_no_corresponding_rule(lsystem_data):
    """
    Test that variable with no appropriate reproduction rule raises RulesVariablesMismatchError. 
    There must be a one-to-one correspondence between variables and rule-keys.
    """
    with pytest.raises(RulesVariablesMismatchError):
        lsystem_data["variables"] += undefined_symb(lsystem_data)
        LSystem(lsystem_data)

def test_rule_input_undefined_symbol(lsystem_data):
    """
    Test that rule-key with undefined symbol raises RulesVariablesMismatchError.
    There must be a one-to-one correspondence between variables and rule-keys.
    """
    with pytest.raises(RulesVariablesMismatchError):
        undefined_chr = undefined_symb(lsystem_data)
        lsystem_data["rules"][undefined_chr] = lsystem_data["constants"][0]
        LSystem(lsystem_data)

def test_rule_output_undefined_symbol(lsystem_data):
    """
    Test that undefined symbol in rule output raises UndefinedSymbolInRuleOutputError.
    """
    with pytest.raises(UndefinedSymbolInRuleOutputError):
        key = list(lsystem_data["rules"].keys())[0]
        lsystem_data["rules"][key] += undefined_symb(lsystem_data)
        LSystem(lsystem_data)

def test_symbol_with_no_corresponding_translation(lsystem_data):
    """
    Test that symbol with no appropriate translation raises TranslationAlphabetMismatch. 
    There must be a one-to-one correspondence between symbols and translation-keys.
    """
    with pytest.raises(TranslationAlphabetMismatchError):
        lsystem_data["constants"] += undefined_symb(lsystem_data)
        LSystem(lsystem_data)

def test_translation_with_undefined_symbol(lsystem_data):
    """
    Test that translation-key with undefined symbol TranslationAlphabetMismatch. 
    There must be a one-to-one correspondence between symbols and translation-keys.
    """
    with pytest.raises(TranslationAlphabetMismatchError):
        undefined_chr = undefined_symb(lsystem_data)
        lsystem_data["translations"][undefined_chr] = "forward 50"
        LSystem(lsystem_data)

def test_unsupported_translation_invalid_operation(lsystem_data):
    """
    Test that unsupported operation raises UnsupportedTranslationError.
    """
    lsystem_data["translations"][defined_symb(lsystem_data,0)] = "banana 25"
    with pytest.raises(UnsupportedTranslationError):
        LSystem(lsystem_data)

def test_unsupported_translation_invalid_parameter(lsystem_data):
    """
    Test that invalid parameter raises UnsupportedTranslationError. Angle-operation expects numeric value.
    """
    lsystem_data["translations"][defined_symb(lsystem_data,0)] = "angle pineapple"
    with pytest.raises(UnsupportedTranslationError):
        LSystem(lsystem_data)

def test_unsupported_translation_missing_parameter(lsystem_data):
    """
    Test that missing parameter raises UnsupportedTranslationError. Draw-operation expects parameter.
    """
    lsystem_data["translations"][defined_symb(lsystem_data,0)] = "draw"
    with pytest.raises(UnsupportedTranslationError):
        LSystem(lsystem_data)

def test_unsupported_translation_parameter_invalid_rgb(lsystem_data):
    """
    Test that invalid RGB-value as color-parameter raises UnsupportedTranslationError.
    """
    lsystem_data["translations"][defined_symb(lsystem_data,0)] = "color 348 -12 25"
    with pytest.raises(UnsupportedTranslationError):
        LSystem(lsystem_data)

def test_unsupported_translation_parameter_invalid_hex(lsystem_data):
    """
    Test that invalid hexadecimal as color-parameter raises UnsupportedTranslationError.
    """
    lsystem_data["translations"][defined_symb(lsystem_data,0)] = "color #GGG"
    with pytest.raises(UnsupportedTranslationError):
        LSystem(lsystem_data)

def test_unsupported_translation_parameter_invalid_color_string(lsystem_data):
    """
    Test that invalid color string as color parameter raises UnsupportedTranslationError.
    """
    lsystem_data["translations"][defined_symb(lsystem_data,0)] = "color appelblauwzeegroen"
    with pytest.raises(UnsupportedTranslationError):
        LSystem(lsystem_data)

def test_valid_color(lsystem_data):
    """
    Test that valid color parameters do not raise any Errors.
    """
    lsystem_data["translations"][defined_symb(lsystem_data,0)] = "color 255 0 13"
    lsystem_data["translations"][defined_symb(lsystem_data,1)] = "color #E0E000"
    lsystem_data["translations"][defined_symb(lsystem_data,2)] = "color blue"
    LSystem(lsystem_data)

def test_overlapping_variables_and_constants(lsystem_data):
    """
    Test that overlapping variables and constants raise VariableConstantOverlapError. Variables and Constants must be disjoint.
    """
    with pytest.raises(VariableConstantOverlapError):
        lsystem_data["constants"] += lsystem_data["variables"] 
        LSystem(lsystem_data)

def test_render_non_drawable_system_translations(lsystem_data):
    """
    Test that calling .render method on L-System with no translations defined raises AttributeError.
    """
    del lsystem_data["translations"]
    lsys = LSystem(lsystem_data)
    iterated_string = lsys.process(2)
    with pytest.raises(AttributeError):
        lsys.render(iterated_string, Turtle())

def test_render_with_invalid_turtle(lsystem_data):
    """
    Test that calling .render() method on L-System without passing proper Turtle() object as argument raises ValueError.
    """
    lsys = LSystem(lsystem_data)
    iterated_string = lsys.process(2)
    with pytest.raises(ValueError):
        lsys.render(iterated_string, "z")

def test_render_with_invalid_instructions_string(lsystem_data):
    """
    Test that calling .render() method on L-System without passing valid iterated string as argument raises ValueError.
    Iterated string must be interpretable by L-System defined translations and so must be subset of L-System alphabet.
    """
    lsys = LSystem(lsystem_data)
    with pytest.raises(ValueError):
        lsys.render(undefined_symb(lsystem_data), Turtle())

def test_invalid_process_iterations(lsystem_data):
    """
    Test that calling .process() method without passing proper iterations argument raises ValueError.
    Iterations must be a positive integer != 0.
    """
    lsys = LSystem(lsystem_data)
    with pytest.raises(ValueError):
        lsys.process(-19)