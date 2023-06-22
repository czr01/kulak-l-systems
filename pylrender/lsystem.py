import datetime
import random
import os
from turtle import Turtle

from drawingstate import DrawingState
from utils import *

"""
    A class representing an L-System.
"""

app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../app'))
history_file_path = os.path.join(app_dir, 'history.txt')

class LSystem:
    def __init__(self, variables, constants, axiom, rules, translations=None, width=None):
        """
        Initializes a new L-System object with the given data.

        :param data: Description of L-System (dict)
        """

        self.variables = variables
        self.constants = constants
        self.alphabet = set(variables).union(set(constants))
        self.axiom = axiom
        self.rules = rules
        self.translations = translations
        self.width = width
        self.stack = []

    def process(self, iterations):
        """
        Applies reproduction rules to axiom a given amount of times.

        :param iterations: Number of iteratations to perform (int)
        :return current: Iterated L-System string
        """

        if not is_pos_int(iterations):
            raise ValueError("Unvalid number of iterations.")

        current = self.axiom
        for _ in range(int(iterations)):
            next = ""
            for symbol in current:
                if symbol in self.rules:
                    expansion = self.rules[symbol]
                    if isinstance(expansion, str):
                        next += expansion
                    elif isinstance(expansion, list):
                        weights, outcomes = zip(*expansion)
                        next += random.choices(outcomes, weights=[float(w) for w in weights], k=1)[0]
                else:
                    next += symbol
            current = next
        self.__log(iterations, current)
        return current

    def __log(self, iterations, string):
        """
        Logs processed (drawable) L-Systems to a history.txt file.
        """
        if self.translations != None:
            logging_message = f"{datetime.datetime.now()}\t{', '.join(self.variables)}\t{', '.join(self.constants)}\t{self.axiom}\t{', '.join([f'{key} -> {value}' for key, value in self.rules.items()])}\t{', '.join([f'{key} : {value}' for key, value in self.translations.items()])}\t{iterations}\t{string}\n"
            with open(history_file_path,'a') as f:
                f.write(logging_message)
        #else: Alternate logging message

    def render(self, string, turtle):
        """
        Renders L-System using turtle graphics.

        :param string: Interpretable L-System instructions string
        :param turtle: Turtle object to draw with.
        """
        if self.translations == None:
            raise AttributeError("L-System is not drawable. Define 'translations' in configuration file.")
        
        if not set(string).issubset(self.alphabet):
            raise ValueError(f"Non-interpretable L-System instructions string '{string}'.")
        
        if not isinstance(turtle, Turtle):
            raise ValueError(f"Unable to draw L-Sytem using {type(turtle)}. Expected Turtle object.")
        
        turtle.width(int(self.width))
        turtle.showturtle()
        for symbol in string:
            operation = self.translations[symbol]
            if " " in operation:
                parameter = operation.split(" ", 1)[1]
                operation =  operation.split(" ")[0]
            method = getattr(self, operation)
            method(turtle, parameter)  
        turtle.hideturtle()
    
    def draw(self, turtle, length):
        """
        Draws a line with given length.

        :param turtle: Turtle object to draw with
        :param length: Distance to move the turtle forward (float)
        """
        turtle.forward(float(length))

    def forward(self, turtle, length):
        """
        Moves turtle forward by given length without drawing a line.

        :param turtle: Turtle object to draw with
        :param length: Distance to move the turtle forward (float)
        """
        turtle.penup()
        turtle.forward(float(length))
        turtle.pendown()

    def angle(self, turtle, angle):
        """
        Rotates the turtle by a given angle to the left.
        
        :param turtle: Turtle object to rotate
        :param angle: Angle to rotate the turtle by (float)
        """
        turtle.left(float(angle))

    def color(self, turtle, color):
        """
        Sets the pen color of the turtle to given color.

        :param turtle: Turtle object to set pen color for
        """
        if " " in color:
            turtle.pencolor(*[int(x)/255 for x in color.split(" ")])
        else:
            turtle.pencolor(color)

    def push(self, turtle, _):
        """
        Pushes drawing state on stack.

        :param turtle: Turtle object to get drawing state from.
        """
        self.stack.append(DrawingState(x=turtle.xcor(), y=turtle.ycor(), angle=turtle.heading(), color=turtle.pencolor()))

    def pop(self, turtle, _):
        """
        Pops drawing state from stack.

        :param turtle: Turtle object to set drawing state to.
        """
        drawing_state = self.stack.pop()
        turtle.penup()
        turtle.setpos(drawing_state.x, drawing_state.y)
        turtle.setheading(drawing_state.angle)
        turtle.pencolor(drawing_state.color)
        turtle.pendown()

    def nop(*args):
        """
        Do nothing.
        """
        pass