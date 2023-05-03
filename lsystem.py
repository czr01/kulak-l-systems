class LSystem:
    def __init__(self, axiom, rules, translations, angle, length):
        self.axiom = axiom
        self.rules = rules
        self.translations = translations
        self.angle = angle
        self.length = length

    def process(self, iterations):
        current = self.axiom
        for _ in range(iterations):
            current = ''.join([self.rules[symbol] if symbol in self.rules else symbol for symbol in current])
        return current

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