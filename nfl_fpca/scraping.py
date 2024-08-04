import logging
import requests

from bs4 import BeautifulSoup, Comment

logging.basicConfig(level=logging.DEBUG,
                    filename='logs/scraping.log',
                    encoding='utf-8',
                    filemode='w',
                    format="{asctime} - {levelname} - {message}",
                    style="{",
                    datefmt="%Y-%m-%d %H:%M",
                    )


class Player:
    def __init__(self, pid, first_name, last_name):
        self.pid = pid
        self.first_name = first_name
        self.last_name = last_name

    def __repr__(self):
        return f"Player({self.pid}, {self.first_name}, {self.last_name})"


def request_url(url):
    response = requests.get(url)

    if response.status_code != 200:
        logging.error(f"Request failed with status code {response.status_code}")
        return None

    return response.text


def find_roster_table(comments):
    for comment in comments:
        if 'id="div_roster"' in comment:
            return BeautifulSoup(comment, 'html.parser')
    logging.error(f"No roster table found")
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
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))

    table = find_roster_table(comments)
    if table is None:
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
