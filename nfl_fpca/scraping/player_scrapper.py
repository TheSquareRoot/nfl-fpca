import re
import requests

from bs4 import BeautifulSoup

from ..config import setup_logging
from ..models.player import Player
from .utils import (find_table,
                    get_career_table,
                    get_position_group,
                    inches_to_cm,
                    lbs_to_kgs
                    )

# Configure module logger from config file
logger = setup_logging(__name__, 'logs/scraping.log')


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
