import pytest
import string

from lsystem import LSystem
from lsystem_exceptions import *

@pytest.fixture
def gen_config():
    return {
        "variables" : ["F"],
        "constants" : ["+"],
        "axiom" : "F",
        "rules" : {
            "F"  : "F+F"
        },
        "translations" : {
            "F" : "draw",
            "+" : "angle"
        },
        "angle" : 90,
        "length" : 50
    }

def get_undefined_char(lst):
    for ch in string.ascii_letters + string.punctuation:
        if ch not in lst:
            return ch

def test_missing_required_field(gen_config):
    with pytest.raises(KeyError):
        del gen_config["axiom"]
        LSystem(gen_config)

def test_incomplete_drawing_fields(gen_config):
    with pytest.raises(KeyError):
        del gen_config["translations"]
        LSystem(gen_config)

def test_invalid_variables_format(gen_config):
    with pytest.raises(TypeError):
        gen_config["variables"] = "F"
        LSystem(gen_config)

def test_invalid_constants_format(gen_config):
    with pytest.raises(TypeError):
        gen_config["constants"] = [23,1,18]
        LSystem(gen_config)

def test_invalid_axiom_format(gen_config):
    with pytest.raises(TypeError):
        gen_config["axiom"] = 5
        LSystem(gen_config)

def test_invalid_rules_format(gen_config):
    with pytest.raises(TypeError):
        gen_config["rules"] = {
            "key1" : ["value1"],
            "key2" : ["value2"]
        }
        LSystem(gen_config)

def test_invalid_translations_format(gen_config):
    with pytest.raises(TypeError):
        gen_config["translations"] = 13
        LSystem(gen_config)

def test_invalid_length_format(gen_config):
    with pytest.raises(TypeError):
        gen_config["length"] = "banana"
        LSystem(gen_config)

def test_invalid_angle_format(gen_config):
    with pytest.raises(TypeError):
        gen_config["angle"] = "twentyone"
        LSystem(gen_config)

def test_proper_length_casting(gen_config):
    gen_config["length"] = "100"
    my_lsys = LSystem(gen_config)
    assert my_lsys.length == 100

def test_proper_angle_casting(gen_config):
    gen_config["angle"] = "53"
    my_lsys = LSystem(gen_config)
    assert my_lsys.angle == 53

def test_string_processing():
    my_lsys = LSystem(
        {
            "variables" : ["A","B"],
            "constants" : [],
            "axiom" : "A",
            "rules" : {
                "A"  : "AB",
                "B" : "A"
            }
        }
    )
    assert my_lsys.process(4) == "ABAABABA"

def test_empty_variable_list(gen_config):
    with pytest.raises(NoVariablesDefinedError):
        gen_config["variables"] = []
        LSystem(gen_config)

def test_axiom_with_no_variable(gen_config):
    with pytest.raises(FixedAxiomError):
        gen_config["axiom"] = "".join([ch for ch in gen_config["axiom"] if ch not in gen_config["variables"]])
        LSystem(gen_config)

def test_axiom_with_undefined_symbol(gen_config):
    with pytest.raises(AxiomWithUndefinedSymbolErrror):
        gen_config["axiom"] += get_undefined_char(gen_config["variables"] + gen_config["constants"])
        LSystem(gen_config)

def test_variable_with_no_corresponding_rule(gen_config):
    with pytest.raises(RuleVariableMismatchError):
        gen_config["variables"] += get_undefined_char(gen_config["variables"] + gen_config["constants"])
        LSystem(gen_config)

def test_rule_input_undefined_symbol(gen_config):
    with pytest.raises(RuleVariableMismatchError):
        undefined_chr = get_undefined_char(gen_config["variables"] + gen_config["constants"])
        gen_config["rules"][undefined_chr] = gen_config["constants"][0]
        LSystem(gen_config)

def test_rule_output_undefined_symbol(gen_config):
    with pytest.raises(UndefinedSymbolInRuleOutputError):
        key = list(gen_config["rules"].keys())[0]
        gen_config["rules"][key] += get_undefined_char(gen_config["variables"] + gen_config["constants"])
        LSystem(gen_config)

def test_symbol_with_no_corresponding_translation(gen_config):
    with pytest.raises(LSysConfigError):
        gen_config["constants"] += get_undefined_char(gen_config["variables"] + gen_config["constants"])
        LSystem(gen_config)

def test_translation_with_undefined_symbol(gen_config):
    with pytest.raises(LSysConfigError):
        undefined_chr = get_undefined_char(gen_config["variables"] + gen_config["constants"])
        gen_config["translations"][undefined_chr] = "forward"
        LSystem(gen_config)

def test_unsupported_translation(gen_config):
    with pytest.raises(LSysConfigError):
        gen_config["translations"][gen_config["variables"][0]] = "banana"
        LSystem(gen_config)

def test_overlapping_variables_and_constants(gen_config):
    with pytest.raises(LSysConfigError):
        gen_config["constants"] += gen_config["variables"] 
        LSystem(gen_config)