import numpy as np


# TODO: Look into dataclasses


class Player:
    def __init__(self, pid):
        self.pid = pid
        # Player info
        self.first_name = None
        self.last_name = None
        self.position = None
        self.position_group = None
        self.height = 0
        self.weight = 0

        # Career info
        self.start_year = 0
        self.start_age = 0
        self.last_year = 0
        self.stats = dict()

        # Combine results
        self.dash = 0.0
        self.bench = 0
        self.broad = 0
        self.shuttle = 0.0
        self.cone = 0.0
        self.vertical = 0.0

    def __repr__(self):
        return f"Player({self.pid}, {self.first_name}, {self.last_name}, {self.position}, {self.height}, {self.weight})"

    # ----- PROPERTIES -------------------------------------------------------------------------------------------------

    @property
    def career_length(self):
        return self.last_year - self.start_year + 1

    @property
    def retired(self):
        return self.start_year != 2023

    # ----- SETTER METHODS ---------------------------------------------------------------------------------------------

    def set_player_info(self, name, position, position_group, height, weight):
        self.first_name = name.split(' ')[0]
        self.last_name = name.split(' ')[1]
        self.position = position
        self.position_group = position_group
        self.height = height
        self.weight = weight

    def set_career_info(self, start_year, start_age, last_year, stats):
        self.start_year = start_year
        self.start_age = start_age
        self.last_year = last_year
        self.stats = stats

    def set_combine_results(self, dash, bench, broad, shuttle, cone, vertical):
        self.dash = dash
        self.bench = bench
        self.broad = broad
        self.shuttle = shuttle
        self.cone = cone
        self.vertical = vertical

    def set_from_db(self, player_info, season_stats_list):
        """Sets attributes from database query objects"""
        # Set attributes from PlayerInfo object
        self.first_name = player_info.first_name
        self.last_name = player_info.last_name
        self.position = player_info.position
        self.height = player_info.height
        self.weight = player_info.weight

        self.start_year = player_info.start_year
        self.start_age = player_info.start_age

        self.dash = player_info.dash
        self.bench = player_info.bench
        self.broad = player_info.broad
        self.shuttle = player_info.shuttle
        self.cone = player_info.cone
        self.vertical = player_info.vertical

        # Set stats from SeasonStats objects
        self.stats = {}
        for stat in season_stats_list:
            self.stats[stat.year] = {
                'gp': stat.games_played,
                'av': stat.approx_value
            }

    def get_stats_array(self, *args):
        # TODO: Input handling
        stats = dict()
        for arg in args:
            stats[arg] = np.array([year[arg] for year in self.stats.values()])
        time = np.array([year for year in self.stats.keys()])

        return stats, time

    def adjust_for_injuries(self, threshold=3):
        # TODO: For some positions like QB, it should reall look at games started
        # Get season stats arrays
        stats, time = self.get_stats_array('gp')

        # A season is filtered out if the number of games played is below the threshold AND there are seasons with more
        # games played in the following years. This is to avoid filtering out the decline in games played at the end of
        # players' careers
        for (i, val) in enumerate(stats['gp'][:-1]):
            if (val <= threshold) and (val <= np.max(stats['gp'][i:-1])):
                del self.stats[time[i]]
