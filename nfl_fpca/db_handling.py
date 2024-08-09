import nfl_fpca.db_model as db_model


@db_model.db.connection_context()
def populate_database(player_list):
    # Wipe the database
    db_model.db.drop_tables([db_model.PlayerInfo, db_model.SeasonStats], safe=True)
    db_model.db.create_tables([db_model.PlayerInfo, db_model.SeasonStats])

    for player in player_list:
        # PlayerInfo table
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
