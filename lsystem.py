import datetime

class LSystem:
    def __init__(self, variables, constants, axiom, rules, translations, angle, length):
        self.variables = variables
        self.constants = constants
        self.axiom = axiom
        self.rules = rules
        self.translations = translations
        self.angle = angle
        self.length = length

    def process(self, iterations):
        current = self.axiom
        for _ in range(iterations):
            current = ''.join([self.rules[symbol] if symbol in self.rules else symbol for symbol in current])
        self.store(iterations, current)
        return current

    def store(self, iterations, string):
        logging_message = f"{datetime.datetime.now()}\t{', '.join(self.variables)}\t{', '.join(self.constants)}\t{self.axiom}\t{', '.join([f'{key} -> {value}' for key, value in self.rules.items()])}\t{', '.join([f'{key} : {value}' for key, value in self.translations.items()])}\t{iterations}\t{string}\n"
        with open("history.txt",'a') as f:
            f.write(logging_message)

    def draw(self, string, turtle):
        for symbol in string:
            if symbol in self.translations:
                operation = self.translations[symbol]
                if operation == "draw":
                    turtle.forward(self.length)                

                elif operation == "forward":
                    turtle.forward(self.length)
                    turtle.draw()

                elif operation == "angle":
                    turtle.right(self.angle)

                elif operation == "-angle":
                    turtle.right(-self.angle)

                elif operation == "nop":
                    pass