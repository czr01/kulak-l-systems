class DrawingState:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle

    def __repr__(self):
        return f"DrawingState({self.x}, {self.y}, {self.angle}, {self.color})"