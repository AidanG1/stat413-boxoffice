from ctypes import cast
from math import dist
from boxoffice.db.db import (
    MovieDistributor,
    MovieFranchise,
    sqlite_db_connect,
    Movie,
    BoxOfficeDay,
    CastOrCrew,
    Person,
)
from enum import Enum
from pandera.errors import SchemaError
from pandera.typing import DataFrame
import datetime
import pandas as pd
import pandera as pa
from peewee import fn


class CREATIVE_TYPE(str, Enum):
    DRAMATIZATION = "Dramatization"
    MULTIPLE_CREATIVE_TYPES = "Multiple Creative Types"
    SCIENCE_FICTION = "Science Fiction"
    FANTASY = "Fantasy"
    HISTORICAL_FICTION = "Historical Fiction"
    CONTEMPORARY_FICTION = "Contemporary Fiction"
    SUPER_HERO = "Super Hero"
    FACTUAL = "Factual"
    KIDS_FICTION = "Kids Fiction"


class GENRE(str, Enum):
    WESTERN = "Western"
    MULTIPLE_GENRES = "Multiple Genres"
    HORROR = "Horror"
    EDUCATIONAL = "Educational"
    MUSICAL = "Musical"
    DOCUMENTARY = "Documentary"
    BLACK_COMEDY = "Black Comedy"
    ADVENTURE = "Adventure"
    REALITY = "Reality"
    ACTION = "Action"
    THRILLER_SUSPENSE = "Thriller/Suspense"
    ROMANTIC_COMEDY = "Romantic Comedy"
    CONCERT_PERFORMANCE = "Concert/Performance"
    DRAMA = "Drama"
    COMEDY = "Comedy"


class MPAA_RATING(str, Enum):
    NR = "NR"
    PG = "PG"
    OPEN = "Open"
    G = "G"
    M_PG = "M/PG"
    NOT_RATED = "Not Rated"
    GP = "GP"
    NC_17 = "NC-17"
    PG_13 = "PG-13"
    R = "R"
    NOT_YET_RATED = "Not Yet Rated"


class PRODUCTION_METHOD(str, Enum):
    DIGITAL_ANIMATION = "Digital Animation"
    MULTIPLE_PRODUCTION_METHODS = "Multiple Production Methods"
    ANIMATION_LIVE_ACTION = "Animation/Live Action"
    LIVE_ACTION = "Live Action"
    ROTOSCOPING = "Rotoscoping"
    HAND_ANIMATION = "Hand Animation"
    STOP_MOTION_ANIMATION = "Stop-Motion Animation"


class SOURCE(str, Enum):
    BASED_ON_TV = "Based on TV"
    REMAKE = "Remake"
    BASED_ON_COMIC_GRAPHIC_NOVEL = "Based on Comic/Graphic Novel"
    BASED_ON_SHORT_FILM = "Based on Short Film"
    BASED_ON_SONG = "Based on Song"
    COMPILATION = "Compilation"
    ORIGINAL_SCREENPLAY = "Original Screenplay"
    BASED_ON_PLAY = "Based on Play"
    BASED_ON_RADIO = "Based on Radio"
    BASED_ON_TOY = "Based on Toy"
    BASED_ON_RELIGIOUS_TEXT = "Based on Religious Text"
    BASED_ON_MUSICAL_OR_OPERA = "Based on Musical or Opera"
    BASED_ON_THEME_PARK_RIDE = "Based on Theme Park Ride"
    BASED_ON_GAME = "Based on Game"
    BASED_ON_FOLK_TALE_LEGEND_FAIRYTALE = "Based on Folk Tale/Legend/Fairytale"
    BASED_ON_FICTION_BOOK_SHORT_STORY = "Based on Fiction Book/Short Story"
    BASED_ON_FACTUAL_BOOK_ARTICLE = "Based on Factual Book/Article"
    BASED_ON_WEB_SERIES = "Based on Web Series"
    BASED_ON_BALLET = "Based on Ballet"
    SPIN_OFF = "Spin-Off"
    BASED_ON_REAL_LIFE_EVENTS = "Based on Real Life Events"
    BASED_ON_MOVIE = "Based on Movie"
    BASED_ON_MUSICAL_GROUP = "Based on Musical Group"


class MovieSchema(pa.DataFrameModel):
    id: int = pa.Field(ge=0)
    truncated_title: str = pa.Field()
    slug: str = pa.Field()
    title: str = pa.Field()
    release_year: int = pa.Field(ge=0)
    mpaa_rating: str = pa.Field()
    # mpaa_rating: str = pa.Field(isin=MPAA_RATING)
    running_time: float = pa.Field(
        nullable=True
    )  # this can be -1 if the runtime is unknown
    synopsis: str = pa.Field()
    mpaa_rating_reason: str = pa.Field(nullable=True)
    budget: float = pa.Field(ge=0, nullable=True, coerce=True)
    creative_type: str = pa.Field()
    # creative_type: str = pa.Field(isin=CREATIVE_TYPE)
    genre: str = pa.Field()
    # genre: str = pa.Field(isin=GENRE)
    production_method: str = pa.Field()
    # production_method: str = pa.Field(isin=PRODUCTION_METHOD)
    source: str = pa.Field()
    # source: str = pa.Field(isin=SOURCE)


class BoxOfficeDaySchema(pa.DataFrameModel):
    id: int = pa.Field(ge=0)
    movie: int = pa.Field(ge=0)
    date: datetime.date = pa.Field()
    revenue: int = pa.Field(ge=0)
    theaters: float = pa.Field(ge=0, nullable=True)


class CastOrCrewSchema(pa.DataFrameModel):
    id: int = pa.Field(ge=0)
    person: int = pa.Field(ge=0)
    person_name: str = pa.Field()
    person_slug: str = pa.Field()
    role: str = pa.Field()
    is_cast: bool = pa.Field()
    is_lead_ensemble: bool = pa.Field()
    movie: int = pa.Field(ge=0)
    movie_title: str = pa.Field()


class MovieCompleteSchema(pa.DataFrameModel):
    id: int = pa.Field(ge=0)
    truncated_title: str = pa.Field()
    slug: str = pa.Field()
    title: str = pa.Field()
    release_year: int = pa.Field(ge=0)
    mpaa_rating: str = pa.Field()
    running_time: float = pa.Field(
        nullable=True
    )  # this can be -1 if the runtime is unknown
    synopsis: str = pa.Field()
    mpaa_rating_reason: str = pa.Field(nullable=True)
    budget: float = pa.Field(ge=0, nullable=True, coerce=True)
    creative_type: str = pa.Field()
    genre: str = pa.Field()
    production_method: str = pa.Field()
    source: str = pa.Field()
    total_box_office: float = pa.Field(ge=0)
    franchise_name: str = pa.Field(nullable=True)
    franchise_slug: str = pa.Field(nullable=True)
    franchise_id: int = pa.Field(ge=0, nullable=True)
    distributor_name: str = pa.Field()
    distributor_slug: str = pa.Field()
    distributor_id: int = pa.Field(ge=0)


def get_movie_frame_no_validation() -> pd.DataFrame | None:
    movies = Movie.select()

    try:
        df = pd.DataFrame(movies.dicts())

        return df

    except SchemaError as e:
        print(e)
        return None


def get_movie_frame() -> DataFrame[MovieCompleteSchema] | None:
    movies = (
        Movie.select(
            Movie.id,
            Movie.truncated_title,
            Movie.slug,
            Movie.title,
            Movie.release_year,
            Movie.mpaa_rating,
            Movie.running_time,
            Movie.synopsis,
            Movie.mpaa_rating_reason,
            Movie.budget,
            Movie.creative_type,
            Movie.genre,
            Movie.production_method,
            Movie.source,
            fn.SUM(BoxOfficeDay.revenue).alias("total_box_office"),
            MovieDistributor.distributor.name.alias("distributor_name"),
            MovieDistributor.distributor.slug.alias("distributor_slug"),
            MovieDistributor.distributor.id.alias("distributor_id"),
        )
        .join(BoxOfficeDay, on=(Movie.id == BoxOfficeDay.movie))
        .group_by(Movie.id)
        .join_from(Movie, MovieDistributor)
    )

    franchises = MovieFranchise.select(
        MovieFranchise.movie,
        MovieFranchise.franchise,
        MovieFranchise.franchise.name.alias("franchise_name"),
        MovieFranchise.franchise.slug.alias("franchise_slug"),
    )

    distributors = MovieDistributor.select(
        MovieDistributor.movie,
        MovieDistributor.distributor,
        MovieDistributor.distributor.name.alias("distributor_name"),
        MovieDistributor.distributor.slug.alias("distributor_slug"),
    )

    # need to join the franchises and distributors
    movies = movies.join_from(Movie, franchises, join_type="LEFT OUTER")

    movies = movies.join_from(Movie, distributors, join_type="LEFT OUTER")

    try:
        dicts = movies.dicts()

        print(dicts)

        return DataFrame[MovieCompleteSchema](dicts)

    except SchemaError as e:
        print(e)
        return None


def get_movie_frame_c() -> pd.DataFrame | None:
    # eventually this will clean the data too
    frame = get_movie_frame()

    box_office_day_frame = get_box_office_day_frame()

    if frame is None or box_office_day_frame is None:
        return None

    # do the join with the box office table to get the sum of the revenue
    sums = box_office_day_frame.groupby("movie")["revenue"].sum()

    frame["total_box_office"] = frame["id"].map(sums)

    return frame


def get_box_office_day_frame() -> DataFrame[BoxOfficeDaySchema] | None:
    box_office_days = BoxOfficeDay.select()

    try:
        dicts = box_office_days.dicts()
        df = DataFrame[BoxOfficeDaySchema](dicts)

        return df

    except SchemaError as e:
        print(e)
        return None


def get_cast_crew_frame() -> DataFrame[CastOrCrewSchema] | None:
    cast_crew = (
        CastOrCrew.select(
            CastOrCrew.id,
            CastOrCrew.person,
            CastOrCrew.role,
            CastOrCrew.is_cast,
            CastOrCrew.is_lead_ensemble,
            CastOrCrew.movie,
            Person.name.alias("person_name"),
            Person.slug.alias("person_slug"),
            Movie.title.alias("movie_title"),
        )
        .join_from(CastOrCrew, Person)
        .join_from(CastOrCrew, Movie)
    )

    try:
        dicts = cast_crew.dicts()
        df = DataFrame[CastOrCrewSchema](dicts)

        return df

    except SchemaError as e:
        print(e)
        return None


if __name__ == "__main__":
    sqlite_db_connect()

    print("Movies")

    df = get_movie_frame()

    if df is not None:
        print(df.head())

    print("Box Office Days")

    bodf = get_box_office_day_frame()

    if bodf is not None:
        print(bodf.head())

    print("Cast and Crew")

    ccf = get_cast_crew_frame()

    if ccf is not None:
        print(ccf.head())
