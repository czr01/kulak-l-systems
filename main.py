from turtle import Turtle
import sys
import os
import json

from lsystem import LSystem

def main():
    
    filename, iterations = get_input()
    
    lsystem = parse(filename)

    lsys_string = lsystem.process(5)
    print(lsys_string)
    #
    turtle = Turtle()
    lsystem.draw(lsys_string, turtle)

    
def get_input():
    filename = input("Name of file containing l-system: ")
    iterations = int(input("Number of iterations: "))
    return filename, iterations

def parse(filename):
    try:
        with open(filename,'r') as f:
            data = json.load(f)
            return LSystem(data["axiom"], data["rules"], data["translations"], int(data["angle"]), int(data["length"]))

    except FileNotFoundError as fnfe:
        print(fnfe)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()