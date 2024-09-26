from boxoffice.db.db import sqlite_db_connect, Movie, BoxOfficeDay
from enum import Enum
from pandera.errors import SchemaError
from pandera.typing import DataFrame
import datetime
import pandas as pd
import pandera as pa


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
    mpaa_rating: str = pa.Field(isin=MPAA_RATING)
    running_time: float = pa.Field(
        nullable=True
    )  # this can be -1 if the runtime is unknown
    synopsis: str = pa.Field()
    mpaa_rating_reason: str = pa.Field(nullable=True)
    budget: float = pa.Field(ge=0, nullable=True, coerce=True)
    creative_type: str = pa.Field(isin=CREATIVE_TYPE)
    genre: str = pa.Field(isin=GENRE)
    production_method: str = pa.Field(isin=PRODUCTION_METHOD)
    source: str = pa.Field(isin=SOURCE)


class BoxOfficeDaySchema(pa.DataFrameModel):
    id: int = pa.Field(ge=0)
    movie: int = pa.Field(ge=0)
    date: datetime.date = pa.Field()
    revenue: int = pa.Field(ge=0)
    theaters: float = pa.Field(ge=0, nullable=True)


def get_movie_frame_nv() -> pd.DataFrame | None:
    movies = Movie.select()

    try:
        df = pd.DataFrame(movies.dicts())

        return df

    except SchemaError as e:
        print(e)
        return None


def get_movie_frame_validated() -> DataFrame[MovieSchema] | None:
    df = get_movie_frame_nv()

    if df is None:
        return None

    try:
        return DataFrame[MovieSchema](df)

    except SchemaError as e:
        print(e)
        return None


def get_movie_frame() -> pd.DataFrame | None:
    # eventually this will clean the data too
    return get_movie_frame_nv()


def get_box_office_day_frame() -> DataFrame[BoxOfficeDaySchema] | None:
    box_office_days = BoxOfficeDay.select()

    try:
        df = DataFrame[BoxOfficeDaySchema](box_office_days.dicts())

        return df

    except SchemaError as e:
        print(e)
        return None


if __name__ == "__main__":
    sqlite_db_connect()

    df = get_movie_frame()

    if df is not None:
        print(df.head())

    bodf = get_box_office_day_frame()

    if bodf is not None:
        print(bodf.head())
