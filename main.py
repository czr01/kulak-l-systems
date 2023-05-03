from turtle import Turtle
import sys
import os
import json

def main():
    filename, iterations = get_input()
    lsystem = parse(filename)
    lsys_string = process_lsystem(lsystem, iterations)
    print(lsys_string)
    turtle = Turtle()

    draw_lsystem(lsystem, lsys_string, turtle)

def get_input():
    filename = input("Name of file containing l-system: ")
    iterations = int(input("Number of iterations: "))
    return filename, iterations

def parse(filename):
    try:
        with open(filename,'r') as f:
            data = json.load(f)
            return data

    except FileNotFoundError as fnfe:
        print(fnfe)
    except Exception as e:
        print(e)

def process_lsystem(lsystem, iterations):
    current = lsystem["axiom"]
    for _ in range(iterations):
        # current = ''.join([lsystem["rules"][symbol] if symbol in lsystem["rules"] else symbol for symbol in current])
        next = ""
        for symbol in current:
            if symbol in lsystem["rules"]:
                next += lsystem["rules"][symbol]
            else:
                next += symbol
        current = next
    return current

def draw_lsystem(lsystem, lsys_string, turtle):
    angle = int(lsystem["angle"])
    length = int(lsystem["length"])

    for symbol in lsys_string:
        if symbol in lsystem["translations"]:
            operation = lsystem["translations"][symbol]
            if operation == "draw":
                turtle.forward(length)                

            elif operation == "forward":
                turtle.forward(length)
                turtle.draw()

            elif operation == "angle":
                turtle.right(angle)

            elif operation == "-angle":
                turtle.right(-angle)

            elif operation == "nop":
                pass

if __name__ == "__main__":
    main()