import logging

from rich.logging import RichHandler

import nfl_fpca.db_model as db_model


# Logger configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Handlers
file_handler = logging.FileHandler('logs/database.log', mode='w')
console_handler = RichHandler()

# Set logging levels
file_handler.setLevel(logging.DEBUG)
console_handler.setLevel(logging.INFO)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Formatter
file_formatter = logging.Formatter("{asctime} - {name} - {levelname} - {message}",
                                   style="{",
                                   datefmt="%H:%M",
                                   )

console_formatter = logging.Formatter("{levelname} - {message}",
                                      style="{",
                                      datefmt="%H:%M",
                                      )

file_handler.setFormatter(file_formatter)
console_handler.setFormatter(console_formatter)


@db_model.db.connection_context()
def add_players(player_list):
    logger.info(f"Adding {len(player_list)} players to database...")
    for player in player_list:
        # PlayerInfo table
        logger.debug(f"[{player.pid}] - Adding player...")
        try:
            db_model.PlayerInfo.create(pid=player.pid,
                                       first_name=player.first_name,
                                       last_name=player.last_name,
                                       position=player.position,
                                       height=player.height,
                                       weight=player.weight,
                                       start_year=player.start_year,
                                       start_age=player.start_age,
                                       career_length=player.career_length,
                                       retired=player.retired,
                                       dash=player.dash,
                                       bench=player.bench,
                                       broad=player.broad,
                                       shuttle=player.shuttle,
                                       cone=player.cone,
                                       vertical=player.vertical, )

            # SeasonStats table
            for year, val in player.stats.items():
                db_model.SeasonStats.create(pid=player.pid,
                                            year=year,
                                            games_played=val['gp'],
                                            approx_value=val['av'], )
        except Exception as e:
            logger.exception(e)

    logger.info(f"{len(player_list)} players added to database!")
