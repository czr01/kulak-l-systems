import pytest
import re
import os

from lsystems.lsystem import LSystem

@pytest.fixture
def process_lsystem():
    lsys = LSystem(
        {
            "variables" : ["F"],
            "constants" : ["+"],
            "axiom" : "F",
            "rules" : {
                "F"  : "F+F"
            },
            "translations" : {
                "F" : "draw 10",
                "+" : "angle 90"
            }
        }
    )
    return lsys.process(3)

app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../app/'))
history_file = os.path.join(app_dir, 'history.txt')
print(history_file)
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

# Test Suite

def test_number_of_fields(process_lsystem):
    """
    Test that latest logged L-System entry contains the expected number of fields. 
    """
    with open(history_file,'r') as f:
        number_of_fields = len(f.readlines()[-1].split("\t"))
        assert number_of_fields == 8

def test_valid_entry_format(process_lsystem):
    """
    Test that the latest logged L-System entry is in the expected format.
    """
    with open(history_file,'r') as f:
        latest_entry = f.readlines()[-1]
        assert validify_entry_format(latest_entry)

def test_result_field_match_lsys_string(process_lsystem):
    """
    Test that the logged L-System result matches the expected L-System string.
    """
    with open(history_file,'r') as f:
        logged_result_string = f.readlines()[-1].split("\t")[-1][:-1] 
        assert process_lsystem == logged_result_string

def test_number_of_entries(process_lsystem):
    """
    Test that the history file contains the expected number of entries.
    """
    with open(history_file, 'r') as f:
        number_of_entries_before = len(f.readlines())
    basic_lsys = LSystem({"variables":["F"],"constants":[],"axiom":"F","rules":{"F":"FF"},"translations":{"F":"draw 10"}})
    basic_lsys.process(1)
    basic_lsys.process(1)
    with open(history_file, 'r') as f:
        number_of_entries_after = len(f.readlines()) 
        assert number_of_entries_after == number_of_entries_before + 2