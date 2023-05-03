from turtle import Turtle
import sys
import os
import json

from lsystem import LSystem
from exceptions import *

def main():  
    filename, iterations = get_input()
    
    lsystem = parse(filename)

    lsys_string = lsystem.process(5)
    print(lsys_string)

    turtle = Turtle()
    lsystem.draw(lsys_string, turtle)
    
def get_input():
    try:
        filename = input("Name of file containing l-system: ")
        if not os.path.exists(filename): 
            raise FileNotFoundError(f"No such file: {filename}")
        if not filename.endswith(".json"): 
            raise JSONFileRequiredError("Input file must be '.json'")

        iterations = int(input("Number of iterations: "))
        if iterations < 0:
            raise NegativeIterationsError("Number of iterations can't be negative")
        
        return filename, iterations
    
    except (FileNotFoundError, JSONFileRequiredError, NegativeIterationsError, ValueError) as e:
        print(e)
        sys.exit(1)

def parse(filename):
    try:
        with open(filename,'r') as f:
            data = json.load(f)
            return LSystem(data["axiom"], data["rules"], data["translations"], int(data["angle"]), int(data["length"]))
        
    except json.decoder.JSONDecodeError as jde:
        print(f"Invalid JSON. {jde}")
        sys.exit(1)

if __name__ == "__main__":
    main()