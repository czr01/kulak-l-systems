import tempfile
import json
from copy import deepcopy
import os

import pytest

from pylrender.main import *

def get_lsys_description(
        variables = ["F","G"],
        constants = ["+","X"], 
        axiom = "F", 
        rules = {
            "F"  : "F+FG",
            "G"  : "FX"
        }, 
        translations = {
            "F" : "draw 10",
            "G" : "forward 10",
            "+" : "angle 90",
            "X" : "color red"
        }, 
        width = 5):

    return deepcopy({
        "variables" : variables,
        "constants" : constants,
        "axiom" : axiom,
        "rules" : rules,
        "translations" : translations,
        "width" : width
    })
 
class TestLSystemParser:
    @staticmethod
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
        os.remove(temp_file_path)

    @staticmethod
    def test_missing_required_field(setup_file):
        """
        Test that a missing required field (variables, constants, axiom, rules) raises a KeyError.
        """
        data = get_lsys_description()
        del data["axiom"]
        file = setup_file(data)
        with pytest.raises(KeyError):
            LSysConfigFileParser.parse(file)

    @staticmethod
    @pytest.mark.parametrize("data", [
    get_lsys_description(variables="F"),
    get_lsys_description(constants=[23,1,18]),
    get_lsys_description(axiom=5),
    get_lsys_description(rules="ABA"),
    get_lsys_description({"X" : 50}),
    get_lsys_description(rules={"X" : [["some_string", "ABA"]]}),
    get_lsys_description(rules={"X" : [[25, "ABA", " "]]}),
    get_lsys_description(rules={"X" : ["0.5", 31]}),
    get_lsys_description(translations=13),
    get_lsys_description(width=-5) 
    ])
    def test_invalid_type(setup_file, data):
        file = setup_file(data)
        with pytest.raises(TypeError):
            LSysConfigFileParser.parse(file)

    @staticmethod
    def test_undefined_width(setup_file):
        """
        Test that undefined L-System width value defaults to default_width.
        """
        data = get_lsys_description()
        del data["width"]
        file = setup_file(data)
        lsys = LSysConfigFileParser.parse(file)
        assert lsys.width == LSysConfigFileParser.default_width

    @staticmethod
    def test_empty_variable_list(setup_file):
        """
        Test that empty variable list raises NoVariablesDefinedError. L-System must include variables.
        """
        data = get_lsys_description(variables=[])
        file = setup_file(data)
        with pytest.raises(NoVariablesDefinedError):
            LSysConfigFileParser.parse(file)

    @staticmethod
    def test_axiom_with_no_variable(setup_file):
        """
        Test that axiom with no variables included raises FixedAxiomError. Axiom must be reproducible.
        """
        data = get_lsys_description(variables=["A"], constants=["X"], axiom="X")
        file = setup_file(data)
        with pytest.raises(FixedAxiomError):
            LSysConfigFileParser.parse(file)

    @staticmethod
    def test_axiom_with_undefined_symbol(setup_file):
        """
        Test that axiom with undefined L-System symbol raisees AxiomWithUndefinedSymbolError. All symbols in axiom must be defined in L-System alphabet.
        """
        data = get_lsys_description(variables=["A"], constants=["B"], axiom="X")
        file = setup_file(data)
        with pytest.raises(AxiomWithUndefinedSymbolErrror):
            LSysConfigFileParser.parse(file)

    @staticmethod
    @pytest.mark.parametrize("data", [
        get_lsys_description(variables=["A"], constants=[], axiom="A", rules={}),
        get_lsys_description(variables=["A"], constants=[], axiom="A", rules={"A":"AA","X":"A"})
    ])
    def test_variable_rule_mismatch(setup_file, data):
        file = setup_file(data)
        with pytest.raises(RulesVariablesMismatchError):
            LSysConfigFileParser.parse(file)

    @staticmethod
    def test_rule_output_undefined_symbol(setup_file):
        """
        Test that undefined symbol in rule output raises UndefinedSymbolInRuleOutputError.
        """
        data = get_lsys_description(variables=["A"], constants=[], axiom="A", rules={"A":"AX"})
        file = setup_file(data)
        with pytest.raises(UndefinedSymbolInRuleOutputError):
            LSysConfigFileParser.parse(file)

    @staticmethod
    @pytest.mark.parametrize("data", [
        get_lsys_description(variables=["A"], constants=[], axiom="A", rules={"A":"AA"}, translations={}),
        get_lsys_description(variables=["A"], constants=[], axiom="A", rules={"A":"AA"}, translations={"X" : "forward 50"})
    ])
    def test_translation_alphabet_mismatch(setup_file, data):
        file = setup_file(data)
        with pytest.raises(TranslationAlphabetMismatchError):
            LSysConfigFileParser.parse(file)

    @staticmethod
    @pytest.mark.parametrize("data", [
        get_lsys_description(variables=["A"], constants=[], axiom="A", rules={"A":"AA"}, translations={"A" : "banana"}),
        get_lsys_description(variables=["A"], constants=[], axiom="A", rules={"A":"AA"}, translations={"A" : "angle pineapple"}),
        get_lsys_description(variables=["A"], constants=[], axiom="A", rules={"A":"AA"}, translations={"A" : "draw"}),
        get_lsys_description(variables=["A"], constants=[], axiom="A", rules={"A":"AA"}, translations={"A" : "color 348 -12 25"}),
        get_lsys_description(variables=["A"], constants=[], axiom="A", rules={"A":"AA"}, translations={"A" : "color #GGG"}),
        get_lsys_description(variables=["A"], constants=[], axiom="A", rules={"A":"AA"}, translations={"A" : "color appelblauwzeegroen"})
    ])
    def test_unsupported_translation(setup_file, data):
        file = setup_file(data)
        with pytest.raises(UnsupportedTranslationError):
            LSysConfigFileParser.parse(file)

    @staticmethod
    def test_overlapping_variables_and_constants(setup_file):
        """
        Test that overlapping variables and constants raise VariableConstantOverlapError. Variables and Constants must be disjoint.
        """
        data = get_lsys_description()
        data["constants"] += data["variables"] 
        file = setup_file(data)
        with pytest.raises(VariableConstantOverlapError):
            LSysConfigFileParser.parse(file)

class TestLSystem:
    @staticmethod
    def test_string_processing():
        """
        Test that L-System processes L-Systems and applies L-System rules correctly.
        """
        my_lsys = LSystem(variables=["A","B"], constants=[], axiom="A", rules={"A":"AB","B":"A"})
        assert my_lsys.process(4) == "ABAABABA"

    @staticmethod
    def test_invalid_process_iterations():
        """
        Test that calling .process() method without passing proper iterations argument raises ValueError.
        Iterations must be a positive integer != 0.
        """
        lsys = LSystem(variables=["A","B"], constants=[], axiom="A", rules={"A":"AB","B":"A"})
        with pytest.raises(ValueError):
            lsys.process(-19)

    @staticmethod
    def test_render_with_invalid_turtle():
        """
        Test that calling .render() method on L-System without passing proper Turtle() object as argument raises ValueError.
        """
        lsys = LSystem(variables=["A","B"], constants=[], axiom="A", rules={"A":"AB","B":"A"}, translations={"A":"draw 10", "B":"forward 10"})
        iterated_string = lsys.process(2)
        with pytest.raises(ValueError):
            lsys.render(iterated_string, "not_real_turtle")

    # Tests below include the Turtle graphics module, which rely on a graphical user interface
    # and thus won't work with CI pipeline test environment. Instead the turtle argument will me
    # mocked. This only works because validity of turtle parameter is last condition to be checked.

    @staticmethod
    def test_render_with_invalid_instructions_string():  
        """
        Test that calling .render() method on L-System without passing valid iterated string as argument raises ValueError.
        Iterated string must be interpretable by L-System defined translations and so must be subset of L-System alphabet.
        """
        lsys = LSystem(variables=["A","B"], constants=[], axiom="A", rules={"A":"AB","B":"A"}, translations={"A":"draw 10", "B":"forward 10"})
        with pytest.raises(ValueError):
            lsys.render("Q", "Turtle()")
    
    @staticmethod
    def test_render_non_drawable_system_translations():
        """
        Test that calling .render method on L-System with no translations defined raises AttributeError.
        """
        lsys = LSystem(variables=["A","B"], constants=[], axiom="A", rules={"A":"AB","B":"A"})
        iterated_string = lsys.process(2)
        with pytest.raises(AttributeError):
            lsys.render(iterated_string, "Turtle()")