from turtle import Turtle
import json

from lsystem import LSystem

class JSONFileRequiredError(ValueError):
    def __init__(self, filename):
        self.filename = filename
        super().__init__(f"'.json' file is required. ('{filename}')")

def main():
    try:
        filename = input("Name of file containing l-system description: ")
        with open(filename,'r') as f:
            if not filename.endswith(".json"):
                raise JSONFileRequiredError(filename)
            data = json.load(f)
        lsystem = LSystem(data)
        iterations = int(input("Number of iterations: "))
        lsys_string = lsystem.process(iterations)
        print(lsys_string)
        turtle = Turtle()
        lsystem.draw(lsys_string, turtle)

    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()