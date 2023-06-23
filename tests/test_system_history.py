import pytest
import re

from PyLRender.pylrender import *

date_format = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}"
var_format = r"[^,]{1}|(([^,]{1}, )+[^,]{1})"
const_format = r"[^,]{1}|(([^,]{1}, )+[^,]{1})|"
axiom_format = r"[^,]+"
rules_format = r"[^,] -> [^,]+|(([^,] -> [^,]+, )+(\w -> [^,]+))"
translations_format = r"[^,] : [^,]+|(([^,] : [^,]+, )+([^,] : [^,]+))"
iterations_format = r"-?\d+"
output_format = r"[^,]+"

def validify_entry_format(entry):
    valid_format = re.compile(f"({date_format})\t({var_format})\t({const_format})\t({axiom_format})\t({rules_format})\t({translations_format})\t({iterations_format})\t({output_format})\n")
    return bool(valid_format.fullmatch(entry))

@pytest.fixture
def setup():
    lsys = LSystem(variables = ["F"], constants = ["+"], axiom = "F", rules = {"F" : "F+F"}, translations = {"F" : "draw 10", "+" : "angle 90"}) 
    with open(HISTORY_PATH, 'r') as f:
        lsys_hist = f.readlines()

    return lsys, lsys_hist

def test_number_of_fields(setup):
    """
    Test that latest logged L-System entry contains the expected number of fields. 
    """
    lsys, lsys_hist = setup
    lsys.process(1)
    number_of_fields = len(lsys_hist[-1].split("\t"))
    assert number_of_fields == 8

def test_valid_entry_format(setup):
    """
    Test that the latest logged L-System entry is in the expected format.
    """
    lsys, lsys_hist = setup
    lsys.process(1)
    latest_entry = lsys_hist[-1]
    assert validify_entry_format(latest_entry)

def test_result_field_match_lsys_string(setup):
    """
    Test that the logged L-System result matches the expected L-System string.
    """
    lsys, lsys_hist = setup
    result_string = lsys.process(1)
    logged_result_string = lsys_hist[-1].split("\t")[-1][:-1] 
    assert result_string == logged_result_string

def test_number_of_entries(setup):
    """
    Test that the history file contains the expected number of entries.
    """
    lsys, lsys_hist = setup
    number_of_entries_before = len(lsys_hist)
    lsys.process(1)
    lsys.process(1)
    with open(HISTORY_PATH, 'r') as f:
        number_of_entries_after = len(f.readlines()) 
    assert number_of_entries_after == number_of_entries_before + 2