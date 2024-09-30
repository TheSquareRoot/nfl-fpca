from collections import defaultdict
import json

from bs4 import BeautifulSoup, Comment


def find_table(soup, tid):
    # Find all comments on the page
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))

    # Search the comments for the table
    for comment in comments:
        if f'id="{tid}"' in comment:
            return BeautifulSoup(comment, 'html.parser')
    return None


def get_career_table(soup):
    """ Finds and returns the table on a player's page which contains his AV for each year."""
    # TODO: speed function up with position based assumptions (i.e. a QB won't have his AV in a defense table)
    titles = ['passing', 'rushing_and_receiving', 'receiving_and_rushing', 'defense', 'kicking', 'punting', 'returns',
              'games_played']  # All possible table names

    # Load each table and if it exists, check if there is an AV column in it
    for title in titles:
        table = soup.find('table', attrs={'id': title})
        if (table is not None) and ('AV' in table.text):
            return table
    return None


def get_position_group(position):
    """ Groups all positions into groups for simpler data handling. """
    with open("position.json", "r") as file:
        pos_dict = json.load(file)

        if position in pos_dict:
            return pos_dict[position]
        else:
            return 'N/A'


def get_position_group_from_history(pos_list, av_list):
    # Dictionary to accumulate AV values for each position
    av_by_position = defaultdict(int)

    # Accumulate AV values for each position
    for pos, av in zip(pos_list, av_list):
        av_by_position[pos] += av

    # Find the position with the maximum cumulative AV
    max_position = max(av_by_position, key=av_by_position.get)

    return max_position


def lbs_to_kgs(weight):
    return round(weight / 2.2046)


def inches_to_cm(height):
    return round(height * 2.54)
