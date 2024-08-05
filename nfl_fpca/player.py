

class Player:
    def __init__(self, pid):
        self.pid = pid
        self.first_name = None
        self.last_name = None
        self.position = None
        self.height = 0
        self.weight = 0

    def __repr__(self):
        return f"Player({self.pid}, {self.first_name}, {self.last_name}, {self.position}, {self.height}, {self.weight})"

    def set_player_info(self, name, position, height, weight):
        self.first_name = name.split(' ')[0]
        self.last_name = name.split(' ')[1]
        self.position = position
        self.height = height
        self.weight = weight
