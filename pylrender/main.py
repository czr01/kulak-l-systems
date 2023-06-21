#! /usr/bin/env python3

from turtle import Turtle, Screen
import sys
import json
from lsystem import LSystem

def load_lsystem_data(filename):
    """
    Load L-System data from JSON file.

    :param filename: Filename to load L-System data from.
    :return: Dictionary containing L-System loaded from file. 
    """
    with open(filename,'r') as f:
        if not filename.endswith(".json"):
            raise ValueError(".json file required.")
        return json.load(f)

def export_image(screen, export_filename):
    """
    Export the turtle graphics as an image.

    :param screen: Screen object to save image of.
    :param export_filename: Filname to export image to.
    """
    import io
    from PIL import Image
    screenshot = screen.getcanvas().postscript()
    image = Image.open(io.BytesIO(screenshot.encode('utf-8')))
    image.save(export_filename)

def main():
    """Main function for running the L-system program."""

    # Check for export option
    export_filename = None
    if len(sys.argv) == 3 and sys.argv[1] == '--export':
        export_filename = sys.argv[2]
    elif len(sys.argv) != 1:
        print('Usage: python3 lsystems [--export <filename>]')
        return

    # Load L-System data from file
    filename = input("Name of file containing l-system description: ")
    lsystem_data = load_lsystem_data(filename)
    
    # Get number of iterations
    iterations = int(input("Number of iterations: "))
    
    # Process L-System
    lsystem = LSystem(lsystem_data)
    lsys_string = lsystem.process(iterations)
    
    # Render L-System using Turtle graphics
    turtle = Turtle()
    lsystem.render(lsys_string, turtle)

    # Export image if specified
    if export_filename: export_image(Screen(), export_filename)

if __name__ == "__main__":
    main()