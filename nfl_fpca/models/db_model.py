import os
from peewee import *


# DB_PATH = "/home/marvin/Documents/code/nfl-fpca/data/player.db"
DB_PATH = os.getcwd() + "/data/player.db"
db = SqliteDatabase(DB_PATH)


class BaseModel(Model):
    class Meta:
        database = db


class PlayerInfo(BaseModel):
    pid = CharField(primary_key=True, null=False)
    first_name = CharField()
    last_name = CharField()
    position = CharField(null=True)
    position_group = CharField(null=True)

    # Physical
    height = IntegerField()
    weight = IntegerField()

    # Career details
    start_year = IntegerField()
    start_age = IntegerField()
    career_length = IntegerField()
    retired = BooleanField(default=True)

    # Combine measurements
    dash = FloatField(null=True)
    bench = IntegerField(null=True)
    broad = IntegerField(null=True)
    shuttle = FloatField(null=True)
    cone = FloatField(null=True)
    vertical = FloatField(null=True)


class SeasonStats(BaseModel):
    pid = ForeignKeyField(PlayerInfo)
    year = IntegerField(null=False)
    games_played = IntegerField()
    games_started = IntegerField()
    approx_value = IntegerField()

    class Meta:
        primary_key = CompositeKey('pid', 'year')
