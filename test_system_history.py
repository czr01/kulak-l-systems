import pytest
import re

from lsystem import LSystem

@pytest.fixture
def general_lsys():
    my_lsys = LSystem(
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
    return my_lsys

history_file = "history.txt"

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

def test_number_of_fields(general_lsys):
    general_lsys.process(3)
    with open(history_file,'r') as f:
        number_of_fields = len(f.readlines()[-1].split("\t"))
        assert number_of_fields == 8

def test_valid_entry_format(general_lsys):
    general_lsys.process(3)
    with open(history_file,'r') as f:
        latest_entry = f.readlines()[-1]
        assert validify_entry_format(latest_entry)

def test_string_field_match_lsys_string(general_lsys):
    result_string = general_lsys.process(3)
    with open(history_file,'r') as f:
        logged_result_string = f.readlines()[-1].split("\t")[-1][:-1] 
        assert result_string == logged_result_string

def test_number_of_entries(general_lsys):
    with open(history_file, 'r') as f:
        number_of_entries_before = len(f.readlines())
    general_lsys.process(3)
    general_lsys.process(3)
    with open(history_file, 'r') as f:
        number_of_entries_after = len(f.readlines()) 
        assert number_of_entries_after == number_of_entries_before + 2