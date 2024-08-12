import re
import requests

from bs4 import BeautifulSoup, Comment

from nfl_fpca.config import setup_logging
from nfl_fpca.player import Player


# Configure module logger from config file
logger = setup_logging(__name__, 'logs/scraping.log')


# TODO: Set error log to exception to get traceback
# TODO: MAJOR - NEED BETTER EXCEPTION HANDLING (return None is NOT enough)

# ----- UTILITY FUNCTIONS ----------------------------------------------------------------------------------------------

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
    return position


def lbs_to_kgs(weight):
    return round(weight / 2.2046)


def inches_to_cm(height):
    return round(height * 2.54)


# ----- WRAPPERS -------------------------------------------------------------------------------------------------------

def fetch_and_scrape_player_ids(team, year, pid_set):
    """Wrapper for scrape_player_ids that handles the page request from a URL"""
    # Create team page URL
    url = f"https://www.pro-football-reference.com/teams/{team}/{year}_roster.htm"

    # Request URL and parse the content
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"[{team.upper()}] - Fetching {year} roster page failed with code {e.response.status_code}")
        return set()
    else:
        logger.debug(f"[{team.upper()}] - Requested {url} successfully")
        logger.info(f"[{team.upper()}] - Scraping {year} roster...")
        return scrape_player_ids(response.text, pid_set)


def fetch_and_scrape_player_page(pid):
    # Create player page URL from player ID
    url = f"https://www.pro-football-reference.com/players/{pid[0].upper()}/{pid}.htm"

    # Request page
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"[{pid}] - Requesting player page failed with code {e.response.status_code}")
        raise
    else:
        logger.debug(f"[{pid}] - Requested {url} successfully.")
        logger.info(f"[{pid}] - Scraping...")
        return scrape_player_page(response.text, pid)


# ----- SCRAPERS -------------------------------------------------------------------------------------------------------

def scrape_player_ids(page, pid_set):
    """Parse player IDs from the roster table of a team page"""
    # Parse html file
    soup = BeautifulSoup(page, 'html.parser')

    # The roster table is in a comment, so it needs to be extracted first to be searched
    table = find_table(soup, "div_roster")
    if table is None:
        logger.error(f'No roster table found')
        return pid_set

    # Get player IDs from the table, store them in a temporary set
    players = table.tbody.find_all('tr')
    temp_set = set()

    for player in players:
        try:
            if player.td['data-append-csv'] not in pid_set:
                temp_set.add(player.td['data-append-csv'])
        except KeyError:
            logger.info(f"{player.td['csk']} does not have a page.")

    return temp_set


def scrape_player_header(header, player):
    # Compile regular expressions
    position_re = re.compile(r":\s([\w-]+)")
    height_re = re.compile(r"(\d{3})cm")
    weight_re = re.compile(r"(\d{2,3})kg")

    # Name
    name = header.h1.span.text

    # Position
    pos_txt = header.find(string="Position")
    if pos_txt is not None:
        pos = position_re.search(pos_txt.parent.parent.text).group(1)
        pos_group = get_position_group(pos)
    else:
        logger.debug(f"[{player.pid}] - No position found")
        pos = 'N/A'
        pos_group = 'N/A'

    # Physicals
    phys = header.find_all(string=height_re)
    if phys:
        height = int(height_re.search(phys[0].text).group(1))
        weight = int(weight_re.search(phys[0].text).group(1))
    else:
        logger.info(f"[{player.pid}] - No physicals found")
        height = 0
        weight = 0

    # Update player info
    player.set_player_info(name, pos, pos_group, height, weight)


def scrape_career_table(table, player):
    lines = table.tbody.find_all('tr', attrs={'class': 'full_table'})

    stats = dict()

    # Get approximate value and games played for each year
    for line in lines:
        year = int(line['id'].split('.')[1])
        gp = int(line.find('td', attrs={'data-stat': 'g'}).text or 0)
        gs = int(line.find('td', attrs={'data-stat': 'gs'}).text or 0)
        av = int(line.find('td', attrs={'data-stat': 'av'}).text or 0)

        stats[year] = {'gp': gp, 'gs': gs, 'av': av}

    # Get other information
    start_year = int(lines[0]['id'].split('.')[1])
    last_year = int(lines[-1]['id'].split('.')[1])
    start_age = int(lines[0].find('td', attrs={'data-stat': 'age'}).text)

    player.set_career_info(start_year, start_age, last_year, stats)


def scrape_combine_table(table, player):
    # TODO: Error handling
    # TODO: Get combine year
    combine_data = table.tbody.tr

    # Get combine results
    dash = float(combine_data.find('td', attrs={'data-stat': 'forty_yd'}).text or 0.0)
    bench = int(combine_data.find('td', attrs={'data-stat': 'bench_reps'}).text or 0)
    broad = int(combine_data.find('td', attrs={'data-stat': 'broad_jump'}).text or 0)
    shuttle = float(combine_data.find('td', attrs={'data-stat': 'shuttle'}).text or 0.0)
    cone = float(combine_data.find('td', attrs={'data-stat': 'cone'}).text or 0.0)
    vertical = float(combine_data.find('td', attrs={'data-stat': 'vertical'}).text or 0.0)

    # If player infos are missing, get them from the combine table
    height = int(combine_data.find('td', attrs={'data-stat': 'height'}).text or 0)
    weight = int(combine_data.find('td', attrs={'data-stat': 'weight'}).text or 0)
    pos = combine_data.find('td', attrs={'data-stat': 'pos'}).text

    if player.height == 0: player.height = inches_to_cm(height)
    if player.weight == 0: player.weight = lbs_to_kgs(weight)
    if player.position == 'N/A': player.position = pos
    if player.position_group == 'N/A': player.position_group = get_position_group(pos)

    player.set_combine_results(dash, bench, broad, shuttle, cone, vertical)


def scrape_player_page(page, pid):
    # Parse HTML file
    soup = BeautifulSoup(page, 'html.parser')

    # Scrape the page
    player = Player(pid)

    header = soup.find('div', attrs={'id': 'meta'})
    career_table = get_career_table(soup)
    combine_table = find_table(soup, "combine")

    if header is not None:
        scrape_player_header(header, player)
    else:
        logger.debug(f"[{pid}] - No player header")

    if career_table is not None:
        logger.debug(f"[{pid}] - Career info found in {career_table['id']}")
        scrape_career_table(career_table, player)
    else:
        logger.debug(f"[{pid}] - No career table")

    if combine_table is not None:
        scrape_combine_table(combine_table, player)
    else:
        logger.debug(f"[{pid}] - No combine table")

    return player
