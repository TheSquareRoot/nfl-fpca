import logging
import re
import requests

from bs4 import BeautifulSoup, Comment

from nfl_fpca.player import Player


logging.basicConfig(level=logging.DEBUG,
                    filename='logs/scraping.log',
                    encoding='utf-8',
                    filemode='w',
                    format="{asctime} - {levelname} - {message}",
                    style="{",
                    datefmt="%Y-%m-%d %H:%M",
                    )


# TODO: Set error log to exception to get traceback
# TODO: Set custom logger


def request_url(url):
    response = requests.get(url)

    if response.status_code != 200:
        logging.error(f"Request failed with status code {response.status_code}")
        return None

    return response.text


def find_table(soup, tid):
    # Find all comments on the page
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))

    # Search the comments for the table
    for comment in comments:
        if f'id="{tid}"' in comment:
            return BeautifulSoup(comment, 'html.parser')
    return None


def fetch_and_scrape_player_ids(url, pid_set):
    """Wrapper for scrape_player_ids that handles the page request from a URL"""
    # Request URL and parse the content
    page = request_url(url)
    if page is None:
        return pid_set

    return scrape_player_ids(page, pid_set)


def scrape_player_ids(page, pid_set):
    """Parse player IDs from the roster table of a team page"""
    # Parse html file
    soup = BeautifulSoup(page, 'html.parser')

    # The roster table is in a comment, so it needs to be extracted first to be searched
    table = find_table(soup, "div_roster")
    if table is None:
        logging.error(f'No roster table found')
        return pid_set

    # Get player IDs from the table, store them in a temporary set
    players = table.tbody.find_all('tr')
    temp_set = set()

    for player in players:
        try:
            if player.td['data-append-csv'] not in pid_set:
                temp_set.add(player.td['data-append-csv'])
        except KeyError:
            logging.info(f"{player.td['csk']} does not have a page.")

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
    else:
        logging.info(f"[{player.pid}] - No position found")
        pos = 'N/A'

    # Physicals
    phys = header.find_all(string=height_re)
    if phys:
        height = int(height_re.search(phys[0].text).group(1))
        weight = int(weight_re.search(phys[0].text).group(1))
    else:
        logging.info(f"[{player.pid}] - No physicals found")
        height = 0
        weight = 0

    # Update player info
    player.set_player_info(name, pos, height, weight)


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


def scrape_career_table(table, player):
    lines = table.tbody.find_all('tr', attrs={'class': 'full_table'})

    games_played = dict()
    approx_value = dict()

    # Get approximate value and games played for each year
    for line in lines:
        year = int(line['id'].split('.')[1])
        gp = int(line.find('td', attrs={'data-stat': 'g'}).text or 0)
        av = int(line.find('td', attrs={'data-stat': 'av'}).text or 0)

        games_played[year] = gp
        approx_value[year] = av

    # Get other information
    start_year = int(lines[0]['id'].split('.')[1])
    last_year = int(lines[-1]['id'].split('.')[1])

    career_length = last_year - start_year + 1
    retired = (last_year != 2023)

    start_age = int(lines[0].find('td', attrs={'data-stat': 'age'}).text)

    player.set_career_info(start_year, start_age, career_length, retired, approx_value, games_played)


def scrape_combine_table(table, player):
    # TODO: Error handling
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

    if player.height == 0: player.height = height
    if player.weight == 0: player.weight = weight
    if player.position == 'N/A': player.position = pos

    player.set_combine_results(dash, bench, broad, shuttle, cone, vertical)


def fetch_and_scrape_player_page(pid):
    # Create player page URL from player ID
    url = f"https://www.pro-football-reference.com/players/{pid[0]}/{pid}.htm"

    # Request page
    page = request_url(url)

    if page is None:
        return None

    return scrape_player_page(page, pid)


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
        logging.info(f"[{pid}] - No player header")

    if career_table is not None:
        logging.debug(f"[{pid}] - Career info found in {career_table['id']}")
        scrape_career_table(career_table, player)
    else:
        logging.info(f"[{pid}] - No career table")

    if combine_table is not None:
        scrape_combine_table(combine_table, player)
    else:
        logging.info(f"[{pid}] - No combine table")

    return player
