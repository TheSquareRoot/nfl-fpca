

class Player:
    def __init__(self, pid):
        self.pid = pid
        # Player info
        self.first_name = None
        self.last_name = None
        self.position = None
        self.height = 0
        self.weight = 0

        # Career info
        self.start_year = 0
        self.start_age = 0
        self.career_length = 0
        self.retired = False
        self.approx_value = dict()
        self.games_played = dict()

        # Combine results
        self.dash = 0.0
        self.bench = 0
        self.broad = 0
        self.shuttle = 0.0
        self.cone = 0.0
        self.vertical = 0.0

    def __repr__(self):
        return f"Player({self.pid}, {self.first_name}, {self.last_name}, {self.position}, {self.height}, {self.weight})"

    def set_player_info(self, name, position, height, weight):
        self.first_name = name.split(' ')[0]
        self.last_name = name.split(' ')[1]
        self.position = position
        self.height = height
        self.weight = weight

    def set_career_info(self, start_year, start_age, career_length, retired, approx_value, games_played):
        self.start_year = start_year
        self.start_age = start_age
        self.career_length = career_length
        self.retired = retired
        self.approx_value = approx_value
        self.games_played = games_played

    def set_combine_results(self, dash, bench, broad, shuttle, cone, vertical):
        self.dash = dash
        self.bench = bench
        self.broad = broad
        self.shuttle = shuttle
        self.cone = cone
        self.vertical = vertical
