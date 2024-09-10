from peewee import *

base_db_path: str = "data.db"

sqlite_db = SqliteDatabase(
    base_db_path, pragmas={"journal_mode": "wal", "cache_size": -1024 * 64}
)


class BaseModel(Model):
    class Meta:
        database = sqlite_db


class Keyword(BaseModel):
    name = CharField()


class ProductionCompany(BaseModel):
    name = CharField()


class ProductionCountry(BaseModel):
    name = CharField()


class Franchise(BaseModel):
    name = CharField()
    description = TextField()


class Language(BaseModel):
    name = CharField()


class CastOrCrew(BaseModel):
    name = CharField()
    role = CharField()
    is_cast = BooleanField()
    is_lead_ensemble = BooleanField()


class Movie(BaseModel):
    title = CharField()
    poster = CharField()
    synopsis = TextField()
    mpaa_rating = CharField()
    mpaa_rating_reason = CharField()
    running_time = IntegerField()
    source = CharField()
    genre = CharField()
    production_method = CharField()
    creative_type = CharField()
    distributor = CharField()


class MovieFranchise(BaseModel):
    movie = ForeignKeyField(Movie, backref="franchises")
    franchise = ForeignKeyField(Franchise, backref="movies")


class MovieKeyword(BaseModel):
    movie = ForeignKeyField(Movie, backref="keywords")
    keyword = ForeignKeyField(Keyword, backref="movies")


class MovieProductionCompany(BaseModel):
    movie = ForeignKeyField(Movie, backref="production_companies")
    production_company = ForeignKeyField(ProductionCompany, backref="movies")


class MovieProductionCountry(BaseModel):
    movie = ForeignKeyField(Movie, backref="production_countries")
    production_country = ForeignKeyField(ProductionCountry, backref="movies")


class MovieLanguage(BaseModel):
    movie = ForeignKeyField(Movie, backref="languages")
    language = ForeignKeyField(Language, backref="movies")


class MovieCastOrCrew(BaseModel):
    movie = ForeignKeyField(Movie, backref="cast_or_crew")
    cast_or_crew = ForeignKeyField(CastOrCrew, backref="movies")


class DomesticRelease(BaseModel):
    date = DateField()
    type = CharField()
    movie = ForeignKeyField(Movie, backref="domestic_releases")


class BoxOfficeDay(BaseModel):
    date = DateField()
    revenue = IntegerField()
    theaters = IntegerField()
    movie = ForeignKeyField(Movie, backref="box_office_days")
