from turtle import Turtle, Screen
import sys
import json
import io
from PIL import Image

from lsystem import LSystem

class JSONFileRequiredError(ValueError):
    def __init__(self, filename):
        self.filename = filename
        super().__init__(f"'.json' file is required. ('{filename}')")

def main():
    try:
        if len(sys.argv) == 1:
            export_filename = None
        elif len(sys.argv) == 3 and sys.argv[1] == '--export':
            export_filename = sys.argv[2]
        else:
            print('Usage: python3 <python-main-file.py> [--export <filename>]')
        
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
        turtle.width(3)
        screen = Screen()
        lsystem.render(lsys_string, turtle)
        if export_filename:
            screenshot = screen.getcanvas().postscript()
            image = Image.open(io.BytesIO(screenshot.encode('utf-8')))
            image.save(export_filename)

    except KeyError as e:
        print(e)

if __name__ == "__main__":
    main()