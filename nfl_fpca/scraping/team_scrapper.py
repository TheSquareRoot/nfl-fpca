import requests

from bs4 import BeautifulSoup

from ..config import setup_logging
from .utils import find_table

# Configure module logger from config file
logger = setup_logging(__name__, 'logs/scraping.log')


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
