import requests
import time

import nfl_fpca.database.db_handling as db_handling

from .config import setup_progress_bar
from .scraping.team_scrapper import fetch_and_scrape_player_ids
from .scraping.player_scrapper import fetch_and_scrape_player_page


def run_scraping_pipeline(start, end, team, wipe=False):

    cooldown = 2.1
    pid_set = set()

    progress = setup_progress_bar()

    # Wipe the database if necessary, otherwise load existing players so they are not scraped again
    if wipe:
        db_handling.reset()
    else:
        pid_set = pid_set | db_handling.get_all_pids()

    with progress:
        team_task = progress.add_task('Scraping teams...', total=(end - start + 1))

        for year in range(start, end+1):
            time.sleep(cooldown)
            player_list = []

            temp_set = fetch_and_scrape_player_ids(team, year, pid_set)

            player_task = progress.add_task('Scraping players...', total=len(temp_set))
            pid_set = pid_set | temp_set

            for pid in temp_set:
                time.sleep(cooldown)
                try:
                    player = fetch_and_scrape_player_page(pid)
                except requests.exceptions.ConnectionError as e:
                    print(e)
                else:
                    if player.start_year >= 1960:
                        player_list.append(player)

                progress.advance(player_task)

            progress.remove_task(player_task)
            progress.advance(team_task)

            db_handling.add_players(player_list)
