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
    slug = CharField()

    class Meta:
        constraints = [SQL("UNIQUE (slug)")]


class ProductionCompany(BaseModel):
    slug = CharField()
    name = CharField()

    class Meta:
        constraints = [SQL("UNIQUE (slug)")]


class ProductionCountry(BaseModel):
    slug = CharField()
    name = CharField()

    class Meta:
        constraints = [SQL("UNIQUE (slug)")]


class Franchise(BaseModel):
    name = CharField()
    slug = CharField()

    class Meta:
        constraints = [SQL("UNIQUE (slug)")]


class CastOrCrew(BaseModel):
    name = CharField()
    role = CharField()
    is_cast = BooleanField()
    is_lead_ensemble = BooleanField()


class Movie(BaseModel):
    truncated_title = CharField()
    slug = CharField()
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
    distributor_slug = CharField()
    language = CharField()

    class Meta:
        constraints = [SQL("UNIQUE (slug)")]


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

def sqlite_db_connect():
    if sqlite_db.connect():
        return True
    else:
        sqlite_db.init('boxoffice')

        sqlite_db.create_tables(
            [
                Keyword,
                ProductionCompany,
                ProductionCountry,
                Franchise,
                CastOrCrew,
                Movie,
                MovieFranchise,
                MovieKeyword,
                MovieProductionCompany,
                MovieProductionCountry,
                MovieCastOrCrew,
                DomesticRelease,
                BoxOfficeDay,
            ],
            safe=True,
        )

        sqlite_db.connect()
