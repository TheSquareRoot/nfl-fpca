from ..config import setup_logging
from ..models.db_model import db, PlayerInfo, SeasonStats
from ..models.player import Player


# Configure module logger from config file
logger = setup_logging(__name__, 'logs/database.log')


@db.connection_context()
def reset():
    try:
        logger.info('Wiping database...')
        db.drop_tables([PlayerInfo, SeasonStats], safe=True)
        db.create_tables([PlayerInfo, SeasonStats])
    except Exception as e:
        logger.exception(e)
    else:
        logger.info('Database wiped!')


@db.connection_context()
def add_players(player_list):
    logger.info(f"Adding {len(player_list)} players to database...")
    for player in player_list:
        # PlayerInfo table
        logger.debug(f"[{player.pid}] - Adding player...")
        try:
            PlayerInfo.create(pid=player.pid,
                              first_name=player.first_name,
                              last_name=player.last_name,
                              position=player.position,
                              position_group=player.position_group,
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
                SeasonStats.create(pid=player.pid,
                                   year=year,
                                   games_played=val['gp'],
                                   games_started=val['gs'],
                                   approx_value=val['av'], )
        except Exception as e:
            logger.exception(e)

    logger.info(f"{len(player_list)} players added to database!")


# ----- QUERIES --------------------------------------------------------------------------------------------------------

@db.connection_context()
def get_all_pids():
    all_pids = set()
    try:
        logger.info('Loading players from database...')
        for player in PlayerInfo.select():
            logger.debug(f"[{player.pid}] - Loading...")
            all_pids.add(player.pid)
    except Exception as e:
        logger.exception(e)
    else:
        logger.info(f"{len(all_pids)} players loaded!")

    return all_pids


@db.connection_context()
def load_player(pid):
    """Requests enrties with pid and creates a player object"""
    # Load info from the db
    player_info = PlayerInfo.get(PlayerInfo.pid == pid)
    season_stats_list = SeasonStats.select().where(SeasonStats.pid == pid).order_by(SeasonStats.year)

    # Create and populate the player object
    player = Player(player_info.pid)
    player.set_from_db(player_info, season_stats_list)

    return player
