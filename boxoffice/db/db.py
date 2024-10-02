from peewee import *
from boxoffice.db.db_path import base_db_path

sqlite_db = SqliteDatabase(
    base_db_path, pragmas={"journal_mode": "wal", "cache_size": -1024 * 64}
)


class BaseModel(Model):
    class Meta:
        database = sqlite_db


class Keyword(BaseModel):
    name = CharField()
    slug = CharField(index=True)

    class Meta:
        constraints = [SQL("UNIQUE (slug)")]


class ProductionCompany(BaseModel):
    slug = CharField()
    name = CharField(index=True)

    class Meta:
        constraints = [SQL("UNIQUE (slug)")]


class Person(BaseModel):
    name = CharField()
    slug = CharField(index=True)

    class Meta:
        constraints = [SQL("UNIQUE (slug)")]


class Distributor(BaseModel):
    name = CharField()
    slug = CharField(index=True)

    class Meta:
        constraints = [SQL("UNIQUE (slug)")]


class ProductionCountry(BaseModel):
    slug = CharField()
    name = CharField(index=True)

    class Meta:
        constraints = [SQL("UNIQUE (slug)")]


class Franchise(BaseModel):
    name = CharField()
    slug = CharField(index=True)

    class Meta:
        constraints = [SQL("UNIQUE (slug)")]


class Language(BaseModel):
    name = CharField()
    slug = CharField(index=True)

    class Meta:
        constraints = [SQL("UNIQUE (slug)")]


class Movie(BaseModel):
    truncated_title = CharField()
    slug = CharField(index=True)
    title = CharField()
    release_year = IntegerField()
    poster = CharField(null=True)  # numbers doesn't have posters for some movies
    synopsis = TextField()
    mpaa_rating = CharField()
    mpaa_rating_reason = CharField(null=True)
    mpaa_rating_date = DateField(null=True)
    running_time = IntegerField(
        null=True
    )  # this is -1 in rare cases where the numbers doesn't have data
    source = CharField()
    genre = CharField()
    production_method = CharField()
    creative_type = CharField()
    budget = IntegerField(null=True)

    class Meta:
        constraints = [SQL("UNIQUE (slug)")]


class CastOrCrew(BaseModel):
    person = ForeignKeyField(Person, backref="people")
    role = CharField()
    is_cast = BooleanField()
    is_lead_ensemble = BooleanField()
    movie = ForeignKeyField(Movie, backref="cast_or_crew")


class MovieFranchise(BaseModel):
    """
    Each movie is in maximum one franchise
    """

    movie = ForeignKeyField(Movie, backref="movie_franchises")
    franchise = ForeignKeyField(Franchise, backref="movie_franchises")


class MovieKeyword(BaseModel):
    movie = ForeignKeyField(Movie, backref="movie_keywords")
    keyword = ForeignKeyField(Keyword, backref="movie_keywords")


class MovieProductionCompany(BaseModel):
    movie = ForeignKeyField(Movie, backref="movie_production_companies")
    production_company = ForeignKeyField(
        ProductionCompany, backref="movie_production_companies"
    )


class MovieProductionCountry(BaseModel):
    movie = ForeignKeyField(Movie, backref="movie_production_countries")
    production_country = ForeignKeyField(
        ProductionCountry, backref="movie_production_countries"
    )


class DomesticRelease(BaseModel):
    date = DateField()
    type = CharField()
    movie = ForeignKeyField(Movie, backref="domestic_releases")


class BoxOfficeDay(BaseModel):
    date = DateField()
    revenue = IntegerField()
    theaters = IntegerField(null=True)
    movie = ForeignKeyField(Movie, backref="box_office_days")

    class Meta:
        constraints = [SQL("UNIQUE (date, movie_id)")]


class MovieLanguage(BaseModel):
    movie = ForeignKeyField(Movie, backref="languages")
    language = ForeignKeyField(Language, backref="movies")


class MovieDistributor(BaseModel):
    movie = ForeignKeyField(Movie, backref="distributors")
    distributor = ForeignKeyField(Distributor, backref="movies")


def sqlite_db_connect():
    tables = [
        Keyword,
        ProductionCompany,
        Person,
        ProductionCountry,
        Franchise,
        Language,
        Movie,
        CastOrCrew,
        MovieFranchise,
        MovieKeyword,
        MovieProductionCompany,
        MovieProductionCountry,
        DomesticRelease,
        BoxOfficeDay,
        MovieLanguage,
        Distributor,
        MovieDistributor,
    ]

    if sqlite_db.connect():
        # check if the tables exist
        if sqlite_db.table_exists(Movie):
            return True

        sqlite_db.create_tables(
            tables,
            safe=True,
        )

    else:
        sqlite_db.init(base_db_path)

        sqlite_db.connect()

        sqlite_db.create_tables(
            tables,
            safe=True,
        )
