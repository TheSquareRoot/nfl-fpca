from peewee import *


DB_PATH = "/home/marvin/Documents/code/nfl-fpca/data/player.db"
db = SqliteDatabase(DB_PATH)


class BaseModel(Model):
    class Meta:
        database = db


class PlayerModel(BaseModel):
    pid = CharField(primary_key=True, null=False)
    firstName = CharField()
    lastName = CharField()
    position = CharField(null=True)

    # Career details
    startYear = IntegerField()
    startAge = IntegerField()
    careerLength = IntegerField()
    retired = BooleanField(default=True)

    # Physical
    height = IntegerField()
    weight = IntegerField()

    # Combine measurements
    dash = FloatField(null=True)
    bench = IntegerField(null=True)
    broad = IntegerField(null=True)
    shuttle = FloatField(null=True)
    cone = FloatField(null=True)
    vertical = FloatField(null=True)


class SeasonStats(BaseModel):
    pid = ForeignKeyField(PlayerModel)
    year = IntegerField(null=False)
    games_played = IntegerField()
    approx_value = IntegerField()

    class Meta:
        primary_key = CompositeKey('pid', 'year')
