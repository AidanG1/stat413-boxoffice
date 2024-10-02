from os import name
from boxoffice.db.db import (
    Distributor,
    Franchise,
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
    is_preview: bool = pa.Field(default=False)
    is_new: bool = pa.Field(default=False)
    day_of_week: int = pa.Field()  # 0 is Monday, 6 is Sunday


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


class MovieSchemaWithBoxOffice(MovieSchema):
    total_box_office: int = pa.Field(ge=0)


class JoinedMovieSchema(MovieSchemaWithBoxOffice):
    distributor_name: str = pa.Field()
    distributor_slug: str = pa.Field()
    distributor_id: int = pa.Field(ge=0)
    franchise_name: str = pa.Field(nullable=True)
    franchise_slug: str = pa.Field(nullable=True)
    franchise_id: int = pa.Field(ge=0)


class MovieCompleteSchema(JoinedMovieSchema):
    release_day_of_week: int = pa.Field()  # 0 is Monday, 6 is Sunday
    release_day_of_week_non_preview: int = pa.Field()  # 0 is Monday, 6 is Sunday
    release_month: int = pa.Field()  # 1 is January, 12 is December
    release_day_of_month: int = (
        pa.Field()
    )  # 1 is the first day of the month, 31 is the last day of the month
    release_day: datetime.date = pa.Field()
    opening_weekend_revenue: float = pa.Field(ge=0)
    # largest_weekend_revenue: float = pa.Field(ge=0)
    # largest_weekend_release_week: int = pa.Field(ge=0)
    largest_theater_count: float = pa.Field(ge=0)
    days_over_1000_theaters: float = pa.Field(ge=0)
    days_over_1000000_revenue: float = pa.Field(ge=0)
    first_five_days_revenue: float = pa.Field(ge=0)
    first_seven_days_revenue: float = pa.Field(ge=0)
    thursday_preview_revenue: float = pa.Field(ge=0)
    thursday_preview_to_weekend_ratio: float = pa.Field(ge=0)
    total_revenue_within_365_days: float = pa.Field(ge=0)
    opening_weekend_to_total_ratio: float = pa.Field(ge=0)
    preview_sum: float = pa.Field(ge=0)
    fri_sat_ratio_first_five: float = pa.Field(ge=0)
    sat_sun_ratio_first_five: float = pa.Field(ge=0)
    sun_mon_ratio_first_five: float = pa.Field(ge=0)
    mon_tue_ratio_first_five: float = pa.Field(ge=0)
    tue_wed_ratio_first_five: float = pa.Field(ge=0)
    wed_thu_ratio_first_five: float = pa.Field(ge=0)
    thu_fri_ratio_first_five: float = pa.Field(ge=0)
    fri_sat_ratio: float = pa.Field(ge=0)
    sat_sun_ratio: float = pa.Field(ge=0)
    sun_mon_ratio: float = pa.Field(ge=0)
    mon_tue_ratio: float = pa.Field(ge=0)
    tue_wed_ratio: float = pa.Field(ge=0)
    wed_thu_ratio: float = pa.Field(ge=0)
    thu_fri_ratio: float = pa.Field(ge=0)


def get_movie_frame_no_validation() -> pd.DataFrame | None:
    movies = Movie.select()

    try:
        df = pd.DataFrame(movies.dicts())

        return df

    except SchemaError as e:
        print(e)
        return None


def get_box_office_day_frame() -> DataFrame[BoxOfficeDaySchema] | None:
    box_office_days = BoxOfficeDay.select()

    try:
        dicts = list(box_office_days.dicts())

        # Calculate the day of the week and add it to each dictionary
        for entry in dicts:
            date = entry.get("date")  # Assuming 'date' is the field name
            if date:
                entry["day_of_week"] = date.weekday()

        df = DataFrame[BoxOfficeDaySchema](dicts)

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
            MovieDistributor.distributor.alias("distributor_id"),
            MovieFranchise.franchise.alias("franchise_id"),
            Distributor.name.alias("distributor_name"),
            Distributor.slug.alias("distributor_slug"),
            Franchise.name.alias("franchise_name"),
            Franchise.slug.alias("franchise_slug"),
        )
        .join(BoxOfficeDay, on=(Movie.id == BoxOfficeDay.movie))
        .group_by(Movie.id)
        .join_from(Movie, MovieDistributor)
        .join_from(Movie, MovieFranchise)
        .join_from(MovieDistributor, Distributor)
        .join_from(MovieFranchise, Franchise)
    )

    dicts = movies.dicts()

    # print the beginning of dicts
    print(dicts)

    movies_df = DataFrame[JoinedMovieSchema](dicts)

    # filter out movies with a sum under 1000000
    prior_len = len(movies_df)
    movies_df = movies_df[movies_df["total_box_office"] >= 1000000]
    print(f"Filtered out {prior_len - len(movies_df)} movies")

    # need to calculate the release day of the week
    bodf = get_box_office_day_frame()

    if bodf is None:
        return None

    grouped = bodf.groupby("movie")

    # get the first box office day for each movie
    first_days: pd.Series[datetime.date] = grouped["date"].min()

    print(type(first_days))

    print(len(first_days))

    # get the type of the elements in the series
    print(type(first_days[0]))

    # get the first day of the week for each movie
    first_days = first_days.dt.dayofweek

    # get the first day of the week for each movie that is not a preview
    non_preview_days = bodf[bodf["is_preview"] == False].groupby("movie")["date"].min()

    non_preview_days = non_preview_days.dt.dayofweek

    # get the first day of the month for each movie
    first_days_month = grouped["date"].min()

    first_days_month = first_days_month.dt.month

    # get the first day of the month for each movie
    first_days_day = grouped["date"].min()

    first_days_day = first_days_day.dt.day

    # get the release day of the week for each movie
    release_day_of_week = grouped["date"].min()

    # get the opening weekend revenue for each movie. This is the sum of the first Friday, Saturday, and Sunday plus Thursday if there was a preview. Movies may not open on a Friday, so need to specifically get the first of each of these
    all_days = [bodf[bodf["date"].dt.dayofweek == i] for i in range(7)]
    first_five_of_each_day = [
        day.groupby("movie").head(5)["revenue"].sum() for day in all_days
    ]
    first_each_day = [day.groupby("movie").head(1)["revenue"].sum() for day in all_days]

    # opening weekend revenue is the sum of the first Friday, Saturday, and Sunday plus Thursday if there was a preview
    opening_weekend_revenue = (
        first_each_day[4] + first_each_day[5] + first_each_day[6] + first_each_day[3]
        if bodf["is_preview"]
        else 0
    )

    # get the first five days of revenue for each movie
    first_five_days = grouped.head(5)["revenue"].sum()

    # get the first seven days of revenue for each movie
    first_seven_days = grouped.head(7)["revenue"].sum()

    # get the total revenue within 365 days of release for each movie
    total_revenue_within_365_days = (
        grouped["revenue"]
        .where(bodf["date"] <= bodf["date"] + datetime.timedelta(days=365))
        .sum()
    )

    # get the opening weekend to total ratio for each movie
    opening_weekend_to_total_ratio = (
        opening_weekend_revenue / total_revenue_within_365_days
    )

    # get the largest theater count for each movie
    largest_theater_count = grouped["theaters"].max()

    # get the days over 1000 theaters for each movie
    days_over_1000_theaters = (
        grouped["theaters"].where(bodf["theaters"] >= 1000).count()
    )

    # get the days over 1000000 revenue for each movie
    days_over_1000000_revenue = (
        grouped["revenue"].where(bodf["revenue"] >= 1000000).count()
    )

    # get the sum of all days that are previews for each movie
    preview_sum = grouped["revenue"].where(bodf["is_preview"]).sum()

    # now get the ratios for each day of the week
    first_five_ratios = []

    for i in range(7):
        first_five_ratios.append(
            first_five_of_each_day[i].sum() / first_five_of_each_day[i - 1].sum()
        )

    # now get the ratios for each day of the week
    ratios = []

    for i in range(7):
        ratios.append(first_each_day[i].sum() / first_each_day[i - 1].sum())

    # now we are done

    try:
        dicts = movies.dicts()

        print(dicts)

        df = pd.DataFrame(dicts)

        df["release_day_of_week"] = release_day_of_week
        df["release_day_of_week_non_preview"] = non_preview_days
        df["release_month"] = first_days_month
        df["release_day_of_month"] = first_days_day
        df["release_day"] = first_days
        df["opening_weekend_revenue"] = opening_weekend_revenue
        df["largest_theater_count"] = largest_theater_count
        df["days_over_1000_theaters"] = days_over_1000_theaters
        df["days_over_1000000_revenue"] = days_over_1000000_revenue
        df["first_five_days_revenue"] = first_five_days
        df["first_seven_days_revenue"] = first_seven_days
        df["total_revenue_within_365_days"] = total_revenue_within_365_days
        df["opening_weekend_to_total_ratio"] = opening_weekend_to_total_ratio
        df["preview_sum"] = preview_sum
        df["fri_sat_ratio_first_five"] = first_five_ratios[4]
        df["sat_sun_ratio_first_five"] = first_five_ratios[5]
        df["sun_mon_ratio_first_five"] = first_five_ratios[6]
        df["mon_tue_ratio_first_five"] = first_five_ratios[0]
        df["tue_wed_ratio_first_five"] = first_five_ratios[1]
        df["wed_thu_ratio_first_five"] = first_five_ratios[2]
        df["thu_fri_ratio_first_five"] = first_five_ratios[3]
        df["fri_sat_ratio"] = ratios[4]
        df["sat_sun_ratio"] = ratios[5]
        df["sun_mon_ratio"] = ratios[6]
        df["mon_tue_ratio"] = ratios[0]
        df["tue_wed_ratio"] = ratios[1]
        df["wed_thu_ratio"] = ratios[2]
        df["thu_fri_ratio"] = ratios[3]

        # rename the distributor and franchise columns
        df = df.rename(
            columns={
                "distributor.name": "distributor_name",
                "distributor.slug": "distributor_slug",
                "distributor.id": "distributor_id",
                "franchise.name": "franchise_name",
                "franchise.slug": "franchise_slug",
                "franchise.id": "franchise_id",
            }
        )

        return DataFrame[MovieCompleteSchema](df)

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
        # deadpool_id = 1
        deadpool = df[df["id"] == 1]

        print(deadpool)

    print("Box Office Days")

    bodf = get_box_office_day_frame()

    if bodf is not None:
        print(bodf.head())

    print("Cast and Crew")

    ccf = get_cast_crew_frame()

    if ccf is not None:
        print(ccf.head())
