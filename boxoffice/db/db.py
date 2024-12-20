from peewee import *
from boxoffice.db.db_path import base_db_path

sqlite_db = SqliteDatabase(base_db_path, pragmas={"journal_mode": "wal", "cache_size": -1024 * 64})


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
    id = IntegerField(primary_key=True)
    truncated_title = CharField()
    slug = CharField(index=True)
    title = CharField()
    release_year = IntegerField()
    poster = CharField(null=True)  # numbers doesn't have posters for some movies
    synopsis = TextField()
    mpaa_rating = CharField()
    mpaa_rating_reason = CharField(null=True)
    mpaa_rating_date = DateField(null=True)
    running_time = IntegerField(null=True)  # this is -1 in rare cases where the numbers doesn't have data
    source = CharField()
    genre = CharField()
    production_method = CharField()
    creative_type = CharField()
    budget = IntegerField(null=True)
    wikipedia_key = CharField(null=True)
    wikipedia_id = IntegerField(null=True)
    meets_keep_requirements = BooleanField(default=False)

    class Meta:
        constraints = [SQL("UNIQUE (slug)")]


class CastOrCrew(BaseModel):
    id = IntegerField(primary_key=True)
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
    production_company = ForeignKeyField(ProductionCompany, backref="movie_production_companies")


class MovieProductionCountry(BaseModel):
    movie = ForeignKeyField(Movie, backref="movie_production_countries")
    production_country = ForeignKeyField(ProductionCountry, backref="movie_production_countries")


class DomesticRelease(BaseModel):
    date = DateField()
    type = CharField()
    movie = ForeignKeyField(Movie, backref="domestic_releases")


class BoxOfficeDay(BaseModel):
    date = DateField()
    revenue = IntegerField()
    theaters = IntegerField(null=True)
    movie = ForeignKeyField(Movie, backref="box_office_days")
    is_preview = BooleanField(default=False)
    is_new = BooleanField(default=False)

    class Meta:
        constraints = [SQL("UNIQUE (date, movie_id)")]


class WikipediaDay(BaseModel):
    date = DateField()
    views = IntegerField()
    movie = ForeignKeyField(Movie, backref="wikipedia_days")

    class Meta:
        constraints = [SQL("UNIQUE (date, movie_id)")]


class MovieLanguage(BaseModel):
    movie = ForeignKeyField(Movie, backref="languages")
    language = ForeignKeyField(Language, backref="movies")


class MovieDistributor(BaseModel):
    movie = ForeignKeyField(Movie, backref="distributors")
    distributor = ForeignKeyField(Distributor, backref="movies")


class MovieMetacritic(BaseModel):
    movie = ForeignKeyField(Movie, backref="metacritic", unique=True)  # movies can only have one metacritic entry
    metacritic_slug = CharField()
    metacritic_score = IntegerField(null=True)
    metacritic_review_count = IntegerField()
    metacritic_score_calculated = IntegerField(null=True)
    metacritic_monday_before_wide_friday_calculated = IntegerField(null=True)
    metacritic_before_wide_friday_calculated = IntegerField(null=True)
    metacritic_before_first_day_calculated = IntegerField(null=True)


class MovieTrailerViews(BaseModel):
    movie = ForeignKeyField(Movie, backref="trailer_views", unique=True)  # movies can only have one metacritic entry
    max_trailer_views = IntegerField(null=True)
    top_3_trailer_views = IntegerField(null=True)  # only for results that say trailer in the name
    top_5_trailer_views = IntegerField(null=True)  # only for results that say trailer in the name
    total_trailer_views = IntegerField(null=True)  # only for results that say trailer in the name


# class TMDbMovie(BaseModel):
#     movie = ForeignKeyField(Movie, backref="tmdb", unique=True)  # movies can only have one TMDb entry
#     tmdb_id = IntegerField()
#     imdb_id = CharField(null=True)
#     backdrop_path = CharField(null=True)
#     belongs_to_collection = ForeignKeyField("TMDbCollection", backref="movies", null=True)
#     budget = IntegerField(null=True)
#     homepage = CharField(null=True)
#     original_language = CharField()
#     original_title = CharField()
#     poster_path = CharField(null=True)
#     release_date = DateField()
#     revenue = IntegerField(null=True)
#     runtime = IntegerField(null=True)
#     status = CharField()
#     tagline = CharField(null=True)
#     title = CharField()


# class TMDbCollection(BaseModel):
#     tmdb_id = IntegerField(primary_key=True)
#     name = CharField()
#     poster_path = CharField(null=True)
#     backdrop_path = CharField(null=True)


# class TMDbGenre(BaseModel):
#     tmdb_id = IntegerField(primary_key=True)
#     name = CharField()


# class TMDbProductionCompany(BaseModel):
#     tmdb_id = IntegerField(primary_key=True)
#     name = CharField()
#     logo_path = CharField(null=True)


# class TMDbProductionCountry(BaseModel):
#     tmdb_id = IntegerField(primary_key=True)
#     name = CharField()
#     iso_3166_1 = CharField()


# class TMDbSpokenLanguage(BaseModel):
#     tmdb_id = IntegerField(primary_key=True)
#     name = CharField()
#     iso_639_1 = CharField()
#     english_name = CharField()


# class TMDbMovieGenre(BaseModel):
#     movie = ForeignKeyField(TMDbMovie, backref="genres")
#     genre = ForeignKeyField(TMDbGenre, backref="movies")


# class TMDbMovieProductionCompany(BaseModel):
#     movie = ForeignKeyField(TMDbMovie, backref="production_companies")
#     production_company = ForeignKeyField(TMDbProductionCompany, backref="movies")


# class TMDbMovieProductionCountry(BaseModel):
#     movie = ForeignKeyField(TMDbMovie, backref="production_countries")
#     production_country = ForeignKeyField(TMDbProductionCountry, backref="movies")


# class TMDbMovieSpokenLanguage(BaseModel):
#     movie = ForeignKeyField(TMDbMovie, backref="spoken_languages")
#     spoken_language = ForeignKeyField(TMDbSpokenLanguage, backref="movies")


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
        WikipediaDay,
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
