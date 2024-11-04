from math import e
from re import M
from boxoffice.colors import bcolors
from boxoffice.db.db import (
    BoxOfficeDay,
    CastOrCrew,
    Distributor,
    Franchise,
    Movie,
    MovieDistributor,
    MovieFranchise,
    Person,
    sqlite_db_connect,
    MovieKeyword,
    Keyword,
    WikipediaDay,
    MovieMetacritic,
)
from pandera.errors import SchemaError
from pandera.typing import DataFrame
from peewee import fn, JOIN
import datetime
import os
import pandas as pd
import pandera as pa
import numpy as np

MOVIES_CSV_BASE_PATH = "boxoffice/db/data"
MOVIES_DB_PATH = f"{MOVIES_CSV_BASE_PATH}/data.sqlite"
MOVIES_CSV_PATH = f"{MOVIES_CSV_BASE_PATH}/movies.csv"
MAX_ITER = 5

# make sure that the movies_csv_path starts from stat413-boxoffice as the parent
while not os.path.exists(MOVIES_DB_PATH):
    MAX_ITER -= 1
    if MAX_ITER == 0:
        print("Could not find the movies database")
        break
    print(f"MOVIES_DB_PATH: {MOVIES_DB_PATH}")
    MOVIES_CSV_BASE_PATH = os.path.join("..", MOVIES_CSV_BASE_PATH)
    MOVIES_DB_PATH = f"{MOVIES_CSV_BASE_PATH}/data.sqlite"
    MOVIES_CSV_PATH = f"{MOVIES_CSV_BASE_PATH}/movies.csv"


class MovieSchema(pa.DataFrameModel):
    id: int = pa.Field(ge=0)
    truncated_title: str = pa.Field()
    slug: str = pa.Field()
    title: str = pa.Field()
    release_year: int = pa.Field(ge=0)
    mpaa_rating: str = pa.Field()
    # mpaa_rating: str = pa.Field(isin=MPAA_RATING)
    running_time: float = pa.Field(nullable=True)  # this can be -1 if the runtime is unknown
    synopsis: str = pa.Field(nullable=True)
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
    poster: str = pa.Field(nullable=True)


class BoxOfficeDaySchema(pa.DataFrameModel):
    id: int = pa.Field(ge=0)
    movie: int = pa.Field(ge=0)
    date: datetime.date = pa.Field()
    revenue: int = pa.Field(ge=0)
    theaters: float = pa.Field(ge=0, nullable=True)
    is_preview: bool = pa.Field(default=False)
    is_new: bool = pa.Field(default=False)
    day_of_week: int = pa.Field()  # 0 is Monday, 6 is Sunday


class WikipediaDaySchema(pa.DataFrameModel):
    id: int = pa.Field(ge=0)
    movie: int = pa.Field(ge=0)
    date: datetime.date = pa.Field()
    views: int = pa.Field(ge=0)


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
    release_day: datetime.date = pa.Field()
    release_day_non_preview: datetime.date = pa.Field()
    largest_theater_count: int = pa.Field(
        ge=0, nullable=True
    )  # this shouldn't be nullable but somehow there is one case where it is
    days_over_1000_theaters: int = pa.Field(ge=0)
    days_over_1000000_revenue: int = pa.Field(ge=0)
    days_over_100000_revenue: int = pa.Field(ge=0)
    preview_sum: float = pa.Field(ge=0, nullable=True)  # some movies don't have previews

    metacritic_score: float = pa.Field(ge=0, nullable=True)
    metacritic_review_count: int = pa.Field(ge=0)
    metacritic_score_calculated: float = pa.Field(ge=0, nullable=True)
    metacritic_monday_before_wide_friday_calculated: float = pa.Field(ge=0, nullable=True)
    metacritic_before_wide_friday_calculated: float = pa.Field(ge=0, nullable=True)
    metacritic_before_first_day_calculated: float = pa.Field(ge=0, nullable=True)


class JoinedMovieSchema(MovieSchemaWithBoxOffice):
    distributor_name: str = pa.Field()
    distributor_slug: str = pa.Field()
    distributor_id: int = pa.Field(ge=0)
    franchise_name: str = pa.Field(nullable=True)
    franchise_slug: str = pa.Field(nullable=True)
    franchise_id: float = pa.Field(
        ge=0, nullable=True
    )  # why is this a float? I don't want it to be but things break otherwise


class MovieWikipediaSchema(JoinedMovieSchema):
    wikipedia_pre_release_cumulative_views: float = pa.Field(
        ge=0
    )  # cumulative views from 60 days before release until 1 day before release
    wikipedia_pre_release_monday_views: float = pa.Field(
        ge=0
    )  # cumulative views from 30 days before release until 4 days before first Friday
    wikipedia_pre_release_week_monday: float = pa.Field(
        ge=0
    )  # cumulative views from 11 days before release until 4 days before first Friday
    wikipedia_pre_release_three_monday: float = pa.Field(
        ge=0
    )  # cumulative views from 7 days before release until 4 days before first Friday
    wikipedia_cumulative_views: float = pa.Field(
        ge=0
    )  # cumulative views from 30 days before release for every day while in theaters


class MovieCompleteSchema(MovieWikipediaSchema):
    release_day_of_week: int = pa.Field()  # 0 is Monday, 6 is Sunday
    release_day_of_week_non_preview: int = pa.Field()  # 0 is Monday, 6 is Sunday
    release_day_first_friday: datetime.date = pa.Field()
    release_month: int = pa.Field()  # 1 is January, 12 is December
    release_day_of_month: int = pa.Field()  # 1 is the first day of the month, 31 is the last day of the month
    opening_weekend_revenue: int = pa.Field(
        ge=0
    )  # this shouldn't be nullable but somehow there is one case where it is
    opening_wide_revenue: float = pa.Field(ge=0)  # this is the revenue for the first weekend in over 1000 theaters
    first_five_days_revenue: float = pa.Field(ge=0)
    first_seven_days_revenue: float = pa.Field(ge=0)
    preview_to_weekend_ratio: float = pa.Field(ge=0, nullable=True)  # some movies don't have previews
    total_revenue_within_365_days: float = pa.Field(
        ge=0
    )  # sometimes this is a float and sometimes it is an int, I don't know why
    opening_weekend_to_total_ratio: float = pa.Field(ge=0)
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
    keywords_space_separated: str = pa.Field()

    # now a bunch of star power metrics
    director_median_box_office: float = pa.Field(ge=0, nullable=True)
    director_mean_box_office: float = pa.Field(ge=0, nullable=True)
    weighted_crew_median_box_office: float = pa.Field(ge=0, nullable=True)
    weighted_crew_mean_box_office: float = pa.Field(ge=0, nullable=True)
    weighted_cast_median_box_office: float = pa.Field(ge=0, nullable=True)
    weighted_cast_mean_box_office: float = pa.Field(ge=0, nullable=True)

    sum_cast_box_office: float = pa.Field(ge=0, nullable=True)
    sum_crew_box_office: float = pa.Field(ge=0, nullable=True)


def get_movie_frame() -> pd.DataFrame | None:
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


def get_movie_frame_full() -> DataFrame[MovieCompleteSchema] | None:
    # first check if it is movies.csv
    if os.path.exists(MOVIES_CSV_PATH):
        # so this exists but may be out of date. If the changes to the frames file are newer than the changes to the movies.csv file, then we need to recalculate
        print(f"movies.csv exists, {os.path.getmtime(MOVIES_CSV_PATH)}, {os.path.getmtime(__file__)}")
        if os.path.getmtime(__file__) > os.path.getmtime(MOVIES_CSV_PATH):
            print("movies.csv is out of date, recalculating")
            return calculate_movie_frame()

        print("Reading from movies.csv")
        df = pd.read_csv(MOVIES_CSV_PATH)

        if "release_day" not in df.columns:
            print("release_day not in columns")
            print(df.columns)
            return None

        # convert release_day and release_day_non_preview to datetime
        df["release_day"] = pd.to_datetime(df["release_day"]).dt.date
        df["release_day_non_preview"] = pd.to_datetime(df["release_day_non_preview"]).dt.date
        df["release_day_first_friday"] = pd.to_datetime(df["release_day_first_friday"]).dt.date

        return DataFrame[MovieCompleteSchema](df)
    else:
        return calculate_movie_frame()


def get_box_office_day_frame_full() -> DataFrame[BoxOfficeDaySchema] | None:
    mf = get_movie_frame_full()

    if mf is None:
        return None

    kept_ids = mf["id"]

    bodf = get_box_office_day_frame()

    if bodf is None:
        return None

    return DataFrame[BoxOfficeDaySchema](bodf[bodf["movie"].isin(kept_ids)])


def calculate_movie_frame() -> DataFrame[MovieCompleteSchema] | None:
    # use a subquery to get release dates for non_preview days
    subquery = (
        BoxOfficeDay.select(
            BoxOfficeDay.movie_id,  # type: ignore
            fn.MIN(BoxOfficeDay.date).alias("release_day_non_preview"),
            fn.MAX(BoxOfficeDay.theaters).alias("largest_theater_count"),
        )
        .where(BoxOfficeDay.is_preview == False)
        .group_by(BoxOfficeDay.movie)
    )
    days_over_1000_theaters_query = (
        BoxOfficeDay.select(
            BoxOfficeDay.movie_id,  # type: ignore
            fn.COUNT(BoxOfficeDay.theaters).alias("days_over_1000_theaters"),
        )
        .where(BoxOfficeDay.theaters >= 1000)  # type: ignore
        .group_by(BoxOfficeDay.movie)
    )

    days_over_1000000_revenue_query = (
        BoxOfficeDay.select(
            BoxOfficeDay.movie_id,  # type: ignore
            fn.COUNT(BoxOfficeDay.revenue).alias("days_over_1000000_revenue"),
        )
        .where(BoxOfficeDay.revenue >= 1000000)  # type: ignore
        .group_by(BoxOfficeDay.movie)
    )

    days_over_100000_revenue_query = (
        BoxOfficeDay.select(
            BoxOfficeDay.movie_id,  # type: ignore
            fn.COUNT(BoxOfficeDay.revenue).alias("days_over_100000_revenue"),
        )
        .where(BoxOfficeDay.revenue >= 100000)  # type: ignore
        .group_by(BoxOfficeDay.movie)
    )

    preview_sum_query = (
        BoxOfficeDay.select(
            BoxOfficeDay.movie_id,  # type: ignore
            fn.SUM(BoxOfficeDay.revenue).alias("preview_sum"),
        )
        .where(BoxOfficeDay.is_preview == True)
        .group_by(BoxOfficeDay.movie)
    )

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
            Movie.poster,
            fn.SUM(BoxOfficeDay.revenue).alias("total_box_office"),
            fn.MIN(BoxOfficeDay.date).alias("release_day"),
            MovieDistributor.distributor.alias("distributor_id"),
            MovieFranchise.franchise.alias("franchise_id"),
            Distributor.name.alias("distributor_name"),
            Distributor.slug.alias("distributor_slug"),
            Franchise.name.alias("franchise_name"),
            Franchise.slug.alias("franchise_slug"),
            subquery.c.release_day_non_preview,
            subquery.c.largest_theater_count,
            days_over_1000_theaters_query.c.days_over_1000_theaters,
            days_over_1000000_revenue_query.c.days_over_1000000_revenue,
            days_over_100000_revenue_query.c.days_over_100000_revenue,
            preview_sum_query.c.preview_sum,
            MovieMetacritic.metacritic_score,
            MovieMetacritic.metacritic_review_count,
            MovieMetacritic.metacritic_score_calculated,
            MovieMetacritic.metacritic_monday_before_wide_friday_calculated,
            MovieMetacritic.metacritic_before_wide_friday_calculated,
            MovieMetacritic.metacritic_before_first_day_calculated,
        )
        .join(BoxOfficeDay, on=(Movie.id == BoxOfficeDay.movie))
        .group_by(Movie.id)
        .join_from(Movie, MovieDistributor)
        .join_from(Movie, MovieFranchise, JOIN.LEFT_OUTER)
        .join_from(MovieDistributor, Distributor)
        .join_from(MovieFranchise, Franchise, JOIN.LEFT_OUTER)
        .join_from(Movie, MovieMetacritic)
        .join(subquery, on=(Movie.id == subquery.c.movie_id))
        .join(
            days_over_1000_theaters_query,
            on=(Movie.id == days_over_1000_theaters_query.c.movie_id),
        )
        .join(
            days_over_1000000_revenue_query,
            on=(Movie.id == days_over_1000000_revenue_query.c.movie_id),
        )
        .join(
            days_over_100000_revenue_query,
            on=(Movie.id == days_over_100000_revenue_query.c.movie_id),
        )
        .join(
            preview_sum_query,
            JOIN.LEFT_OUTER,
            on=(Movie.id == preview_sum_query.c.movie_id),
        )
    )

    dicts = movies.dicts()

    # print the beginning of dicts
    print(dicts)

    # make sure the release_day_non_preview is a date
    for entry in dicts:
        entry["release_day_non_preview"] = datetime.datetime.strptime(
            entry["release_day_non_preview"], "%Y-%m-%d"
        ).date()
        entry["release_day_first_friday"] = entry["release_day_non_preview"] + datetime.timedelta(
            days=(4 - entry["release_day_non_preview"].weekday())
        )

    movies_df = DataFrame[JoinedMovieSchema](dicts)

    # within synopsis, replace commas and newlines
    movies_df["synopsis"] = movies_df["synopsis"].str.replace(",", "%2C")
    movies_df["synopsis"] = movies_df["synopsis"].str.replace("\n", "%0A")

    kept_ids = movies_df["id"]

    print(f"There are {len(kept_ids)} movies in the movie dataframe, now filtering out the box office days")

    # now filter out re-releases. A movie is a re-release if the year of its release_day is not the same as its release_year
    prior_len = len(movies_df)
    # make sure release_day is a date
    movies_df["release_day"] = pd.to_datetime(movies_df["release_day"])
    movies_df["release_day_non_preview"] = pd.to_datetime(movies_df["release_day_non_preview"])
    movies_df["release_day_first_friday"] = pd.to_datetime(movies_df["release_day_first_friday"])
    movies_df = movies_df[movies_df["release_day"].dt.year == movies_df["release_year"]]
    print(f"Filtered out {prior_len - len(movies_df)} re-releases, there are now {len(movies_df)} movies")

    # need to calculate the release day of the week
    bodf = get_box_office_day_frame()

    if bodf is None:
        return None

    # now filter out the box office days for movies that are not in the movie dataframe
    prior_len = len(bodf)
    bodf = bodf[bodf["movie"].isin(kept_ids)]

    # bodf = bodf.sort_values("date").sort_values("movie")
    bodf.reset_index(drop=True, inplace=True)
    # bodf = bodf.sort_values("date").sort_values("movie")

    # drop movies that weren't released on every day
    movies_to_drop = []
    for movie, group in bodf.groupby("movie")["day_of_week"]:
        if len(group.unique()) != 7:
            movies_to_drop.append(movie)

    prior_movies_len = len(movies_df)
    movies_df = movies_df[~movies_df["id"].isin(movies_to_drop)]
    print(
        f"Filtered out {prior_movies_len - len(movies_df)} movies that weren't released on every day of the week, there are now {len(movies_df)} movies"
    )
    bodf = bodf[bodf["movie"].isin(movies_df["id"])]

    print(f"Filtered out {prior_len - len(bodf)} box office days, there are now {len(bodf)} box office days")

    # add the columns to the df
    # copy the movies_df but without any typing
    df = movies_df.copy()

    dates = bodf.groupby("movie")["date"]

    df["release_day_of_week"] = df["release_day"].apply(lambda x: x.weekday())

    df["release_day_of_week_non_preview"] = df["release_day_non_preview"].apply(lambda x: x.weekday())

    df["release_month"] = df["release_day_non_preview"].apply(lambda x: x.month)

    df["release_day_of_month"] = df["release_day_non_preview"].apply(lambda x: x.day)

    # get the opening weekend revenue for each movie. This is the sum of the first Friday, Saturday, and Sunday plus Thursday if there was a preview. Movies may not open on a Friday, so need to specifically get the first of each of these

    first_five_by_weekday = []
    first_by_weekday = []
    total_by_weekday = []
    is_preview_by_weekday = []

    for weekday in range(7):
        cond1 = bodf["day_of_week"] == weekday
        cond2 = bodf["is_preview"] == False

        days = bodf[cond1 & cond2].sort_values("date").reset_index(drop=True).groupby("movie")

        first_five_by_weekday.append(days.apply(lambda x: x.head(5)["revenue"].sum(), include_groups=False))
        first_by_weekday.append(days.apply(lambda x: x.head(1)["revenue"].sum(), include_groups=False))
        total_by_weekday.append(days.apply(lambda x: x["revenue"].sum(), include_groups=False))
        is_preview_by_weekday.append(days.apply(lambda x: x.head(1)["is_preview"].sum(), include_groups=False))

    # opening weekend revenue is the sum of the first Friday, Saturday, and Sunday plus Thursday if there was a preview
    opening_weekend_revenue = (first_by_weekday[4] + first_by_weekday[5] + first_by_weekday[6]).reset_index(drop=True)

    # replace NaNs with 0
    opening_weekend_revenue = opening_weekend_revenue.fillna(0)

    df = df.reset_index(drop=True).sort_index()

    first_five_days = (
        bodf.where(bodf["is_preview"] == False)
        .sort_values("date")
        .groupby("movie")
        .apply(lambda x: x.head(5)["revenue"].sum(), include_groups=False)
        .reset_index(drop=True)
    )
    # get the first seven days of revenue for each movie
    first_seven_days = (
        bodf.where(bodf["is_preview"] == False)
        .sort_values("date")
        .groupby("movie")
        .apply(lambda x: x.head(7)["revenue"].sum(), include_groups=False)
        .reset_index(drop=True)
    )

    # get the total revenue within 365 days of release for each movie
    total_revenue_within_365_days = (
        bodf.where((bodf["date"] <= bodf["date"] + datetime.timedelta(days=365)) & (bodf["is_preview"] == False))
        .groupby("movie")["revenue"]
        .sum()
        .reset_index(drop=True)
    )

    # get the opening weekend to total ratio for each movie
    opening_weekend_to_total_ratio = opening_weekend_revenue / total_revenue_within_365_days
    opening_weekend_to_total_ratio = opening_weekend_to_total_ratio.reset_index(drop=True)

    # now get the ratios for each day of the week
    first_five_ratios = []

    for i in range(7):
        first_five_ratios.append((first_five_by_weekday[i] / first_five_by_weekday[i - 1]).reset_index(drop=True))

    # now get the ratios for each day of the week
    ratios = []

    for i in range(7):
        ratios.append((total_by_weekday[i] / total_by_weekday[i - 1]).reset_index(drop=True))

    # now want to do wide weekend revenue, normally wide would be considered 1000 theaters, but leaving some wiggle room
    for movie in df["id"]:
        fridays = bodf[(bodf["movie"] == movie) & (bodf["day_of_week"] == 4) & (bodf["theaters"] >= 750)].sort_values(
            "date"
        )

        saturdays = bodf[
            (bodf["movie"] == movie) & (bodf["day_of_week"] == 5) & (bodf["theaters"] >= 750)
        ].sort_values("date")

        sundays = bodf[(bodf["movie"] == movie) & (bodf["day_of_week"] == 6) & (bodf["theaters"] >= 750)].sort_values(
            "date"
        )

        if not fridays.empty and not saturdays.empty and not sundays.empty:
            first_friday = fridays.head(1)
            first_saturday = saturdays.head(1)
            first_sunday = sundays.head(1)

            # make sure the dates are all one apart
            if (
                first_friday["date"].values[0]
                == first_saturday["date"].values[0] - datetime.timedelta(days=1)
                == first_sunday["date"].values[0] - datetime.timedelta(days=2)
            ):
                weekend_revenue = (
                    first_friday["revenue"].values[0]
                    + first_saturday["revenue"].values[0]
                    + first_sunday["revenue"].values[0]
                )

                df.loc[df["id"] == movie, "opening_wide_revenue"] = weekend_revenue
            else:
                print(f"Dates are not one apart for movie {movie}, skipping wide weekend revenue")
                df.loc[df["id"] == movie, "opening_wide_revenue"] = 0
        else:
            print(f"Could not find wide weekend revenue for movie {movie}")
            df.loc[df["id"] == movie, "opening_wide_revenue"] = 0

    # now we are done
    df["opening_weekend_revenue"] = opening_weekend_revenue.fillna(0)
    df["first_five_days_revenue"] = first_five_days
    df["first_seven_days_revenue"] = first_seven_days
    df["total_revenue_within_365_days"] = total_revenue_within_365_days
    df["opening_weekend_to_total_ratio"] = opening_weekend_to_total_ratio
    df["preview_to_weekend_ratio"] = df["preview_sum"] / opening_weekend_revenue
    df["fri_sat_ratio_first_five"] = first_five_ratios[5]
    df["sat_sun_ratio_first_five"] = first_five_ratios[6]
    df["sun_mon_ratio_first_five"] = first_five_ratios[0]
    df["mon_tue_ratio_first_five"] = first_five_ratios[1]
    df["tue_wed_ratio_first_five"] = first_five_ratios[2]
    df["wed_thu_ratio_first_five"] = first_five_ratios[3]
    df["thu_fri_ratio_first_five"] = first_five_ratios[4]
    df["fri_sat_ratio"] = ratios[5]
    df["sat_sun_ratio"] = ratios[6]
    df["sun_mon_ratio"] = ratios[0]
    df["mon_tue_ratio"] = ratios[1]
    df["tue_wed_ratio"] = ratios[2]
    df["wed_thu_ratio"] = ratios[3]
    df["thu_fri_ratio"] = ratios[4]

    # get the keywords for each movie
    movie_ids = df["id"]

    movie_keywords = (
        MovieKeyword.select(MovieKeyword.movie, Keyword.name).join_from(MovieKeyword, Keyword)
        # .where(MovieKeyword.movie_id << movie_ids)
    )

    # print information about the keywords
    print(f"Found {len(movie_keywords)} keywords")

    movie_keywords_df = pd.DataFrame(movie_keywords.dicts())

    # group by movie and join the keywords
    keywords = (
        movie_keywords_df.sort_values("name")
        .groupby("movie")["name"]
        .apply(lambda x: " ".join(x), include_groups=False)
    )

    df["keywords_space_separated"] = keywords.reset_index(drop=True)

    # now calculate the star power metrics
    # get the cast and crew
    cast_crew = get_cast_crew_frame()

    if cast_crew is None:
        print(bcolors.FAIL + "Failed to get cast and crew" + bcolors.ENDC)
        return None

    # add a column to the cast_crew dataframe that is a list of 365 day revenue for each movie, \frac{1}{0.25x+1} scale by for credit order and cast order
    scaled_person_revenue: list[None | list[float]] = [None] * len(cast_crew["person"].unique())

    # sort the movies by release date
    df = df.sort_values("release_day_non_preview").reset_index(drop=True)

    # initialize the fields
    df["director_median_box_office"] = np.zeros(len(df))
    df["director_mean_box_office"] = np.zeros(len(df))
    df["weighted_crew_median_box_office"] = np.zeros(len(df))
    df["weighted_crew_mean_box_office"] = np.zeros(len(df))
    df["weighted_cast_median_box_office"] = np.zeros(len(df))
    df["weighted_cast_mean_box_office"] = np.zeros(len(df))
    df["sum_cast_box_office"] = np.zeros(len(df))
    df["sum_crew_box_office"] = np.zeros(len(df))

    # iterate through the movies and calculate the 365 day revenue for each movie
    for i, row in df.iterrows():
        current_movie_revenue = row["total_revenue_within_365_days"]
        movie_cast = cast_crew[cast_crew["movie"] == row["id"]]

        # director_median_box_office: float = pa.Field(ge=0)
        # director_mean_box_office: float = pa.Field(ge=0)
        # weighted_crew_median_box_office: float = pa.Field(ge=0)
        # weighted_crew_mean_box_office: float = pa.Field(ge=0)
        # weighted_cast_median_box_office: float = pa.Field(ge=0)
        # weighted_cast_mean_box_office: float = pa.Field(ge=0)

        # need to update the previous fields
        # get the director
        cond_false = movie_cast["is_cast"] == False
        cond_director = movie_cast["role"] == "Director"
        cond_true = movie_cast["is_cast"] == True

        director_ids = movie_cast[cond_director & cond_false]["person"].tolist()
        director_ids.reverse()

        # get the crew
        crew_ids = movie_cast[cond_false]["person"].tolist()
        crew_ids.reverse()

        # get the cast
        cast_ids = movie_cast[cond_true]["person"].tolist()
        cast_ids.reverse()

        if len(director_ids) > 0:
            # need to get the values from person_revenue
            director_revenues = []
            for director_id in director_ids:
                spr = scaled_person_revenue[director_id]
                if spr is not None:
                    director_revenues.extend(spr)

            df.at[i, "director_median_box_office"] = np.median(director_revenues)
            df.at[i, "director_mean_box_office"] = np.mean(director_revenues)
        else:
            df.at[i, "director_median_box_office"] = 0
            df.at[i, "director_mean_box_office"] = 0

        if len(crew_ids) > 0:
            crew_revenues = []
            for crew_id in crew_ids:
                spr = scaled_person_revenue[crew_id]
                if spr is not None:
                    crew_revenues.extend(spr)

            df.at[i, "weighted_crew_median_box_office"] = np.median(crew_revenues)
            df.at[i, "weighted_crew_mean_box_office"] = np.mean(crew_revenues)
        else:
            df.at[i, "weighted_crew_median_box_office"] = 0
            df.at[i, "weighted_crew_mean_box_office"] = 0

        if len(cast_ids) > 0:
            cast_revenues = []
            for cast_id in cast_ids:
                spr = scaled_person_revenue[cast_id]
                if spr is not None:
                    cast_revenues.extend(spr)

            df.at[i, "weighted_cast_median_box_office"] = np.median(cast_revenues)
            df.at[i, "weighted_cast_mean_box_office"] = np.mean(cast_revenues)
        else:
            df.at[i, "weighted_cast_median_box_office"] = 0
            df.at[i, "weighted_cast_mean_box_office"] = 0

        df.at[i, "sum_cast_box_office"] = sum(cast_revenues)
        df.at[i, "sum_crew_box_office"] = sum(crew_revenues)

        # now update the scaled_person_revenue
        for i, person_id in enumerate(cast_ids):
            scaled_revenue = current_movie_revenue / (0.25 * i + 1)
            spr = scaled_person_revenue[person_id]
            if spr is None:
                scaled_person_revenue[person_id] = [scaled_revenue]
            else:
                scaled_person_revenue[person_id].append(scaled_revenue)

        for i, person_id in enumerate(crew_ids):
            scaled_revenue = current_movie_revenue / (0.25 * i + 1)
            spr = scaled_person_revenue[person_id]
            if spr is None:
                scaled_person_revenue[person_id] = [scaled_revenue]
            else:
                scaled_person_revenue[person_id].append(scaled_revenue)

        for i, person_id in enumerate(director_ids):
            spr = scaled_person_revenue[person_id]
            if spr is None:
                scaled_person_revenue[person_id] = [current_movie_revenue]
            else:
                scaled_person_revenue[person_id].append(current_movie_revenue)

    # fill in the NaNs with 0
    df["director_median_box_office"] = df["director_median_box_office"].fillna(0)
    df["director_mean_box_office"] = df["director_mean_box_office"].fillna(0)
    df["weighted_crew_median_box_office"] = df["weighted_crew_median_box_office"].fillna(0)
    df["weighted_crew_mean_box_office"] = df["weighted_crew_mean_box_office"].fillna(0)
    df["weighted_cast_median_box_office"] = df["weighted_cast_median_box_office"].fillna(0)
    df["weighted_cast_mean_box_office"] = df["weighted_cast_mean_box_office"].fillna(0)
    df["sum_cast_box_office"] = df["sum_cast_box_office"].fillna(0)
    df["sum_crew_box_office"] = df["sum_crew_box_office"].fillna(0)

    # now do wikipedia stuff
    wikipedia_days = WikipediaDay.select()

    wikipedia_df = DataFrame(wikipedia_days.dicts())

    # need to join with the movies dataframe to get release day information
    wikipedia_df = wikipedia_df.merge(
        df[["release_day", "release_day_non_preview", "release_day_first_friday", "id"]],
        left_on="movie",
        right_on="id",
    )

    wikipedia_df.reset_index(drop=True, inplace=True)

    # print the columns
    print(f"Columns in wikipedia_df: {wikipedia_df.columns}")

    # get the cumulative views for each movie
    cumulative_views = wikipedia_df.groupby("movie")["views"].sum()

    wikipedia_pre_release_cumulative_views = (
        wikipedia_df.where((wikipedia_df["date"] < wikipedia_df["release_day_non_preview"]))
        .groupby("movie")["views"]
        .sum()
    )

    cond1 = wikipedia_df["date"] >= wikipedia_df["release_day_first_friday"] - datetime.timedelta(days=30)
    cond2 = wikipedia_df["date"] <= wikipedia_df["release_day_first_friday"] - datetime.timedelta(days=4)

    wikipedia_pre_release_monday_views = wikipedia_df.where(cond1 & cond2).groupby("movie")["views"].sum()

    cond1 = wikipedia_df["date"] >= wikipedia_df["release_day_first_friday"] - datetime.timedelta(days=11)
    cond2 = wikipedia_df["date"] <= wikipedia_df["release_day_first_friday"] - datetime.timedelta(days=4)

    wikipedia_pre_release_week_monday = wikipedia_df.where(cond1 & cond2).groupby("movie")["views"].sum()

    cond1 = wikipedia_df["date"] >= wikipedia_df["release_day_first_friday"] - datetime.timedelta(days=7)
    cond2 = wikipedia_df["date"] <= wikipedia_df["release_day_first_friday"] - datetime.timedelta(days=4)

    wikipedia_pre_release_three_monday = wikipedia_df.where(cond1 & cond2).groupby("movie")["views"].sum()

    # print all of the lengths
    print(
        f"cumulative_views: {len(cumulative_views)}, wikipedia_pre_release_cumulative_views: {len(wikipedia_pre_release_cumulative_views)}, wikipedia_pre_release_monday_views: {len(wikipedia_pre_release_monday_views)}, wikipedia_pre_release_week_monday: {len(wikipedia_pre_release_week_monday)}, wikipedia_pre_release_three_monday: {len(wikipedia_pre_release_three_monday)}, cumulative index: {len(cumulative_views.index)}"
    )

    # join the columns together so that minimum length is used
    merged_accumulated = pd.DataFrame(
        {
            "movie_id": wikipedia_pre_release_three_monday.index,
            "wikipedia_pre_release_three_monday": wikipedia_pre_release_three_monday,
        }
    )

    # join the columns together so that minimum length is used
    merged_accumulated = merged_accumulated.merge(
        pd.DataFrame(
            {
                "movie_2": cumulative_views.index,
                "wikipedia_pre_release_week_monday": wikipedia_pre_release_week_monday,
                "wikipedia_pre_release_monday_views": wikipedia_pre_release_monday_views,
                "wikipedia_pre_release_cumulative_views": wikipedia_pre_release_cumulative_views,
                "wikipedia_cumulative_views": cumulative_views,
            }
        ),
        left_on="movie_id",
        right_on="movie_2",
    )

    print(f"Columns in merged_accumulated: {merged_accumulated.columns}")

    # now merge the wikipedia dataframe with the movies dataframe, setting to 0 if there are no wikipedia views
    df = df.merge(
        merged_accumulated[
            [
                "movie_id",
                "wikipedia_pre_release_cumulative_views",
                "wikipedia_pre_release_monday_views",
                "wikipedia_pre_release_week_monday",
                "wikipedia_pre_release_three_monday",
                "wikipedia_cumulative_views",
            ]
        ],
        how="left",
        left_on="id",
        right_on="movie_id",
    )

    # fill in the NaNs with 0
    df["wikipedia_pre_release_cumulative_views"] = df["wikipedia_pre_release_cumulative_views"].fillna(0)
    df["wikipedia_pre_release_monday_views"] = df["wikipedia_pre_release_monday_views"].fillna(0)
    df["wikipedia_pre_release_week_monday"] = df["wikipedia_pre_release_week_monday"].fillna(0)
    df["wikipedia_pre_release_three_monday"] = df["wikipedia_pre_release_three_monday"].fillna(0)
    df["wikipedia_cumulative_views"] = df["wikipedia_cumulative_views"].fillna(0)

    # make sure release_day is a date
    df["release_day"] = pd.to_datetime(df["release_day"]).dt.date
    df["release_day_non_preview"] = pd.to_datetime(df["release_day_non_preview"]).dt.date
    df["release_day_first_friday"] = pd.to_datetime(df["release_day_first_friday"]).dt.date

    # remove the movie_id column
    df.drop(columns=["movie_id"], inplace=True)

    df.to_csv(MOVIES_CSV_PATH, index=False)

    return DataFrame[MovieCompleteSchema](df)


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


def get_wikipedia_day_frame() -> DataFrame[WikipediaDaySchema] | None:
    wikipedia_days = WikipediaDay.select()

    try:
        dicts = list(wikipedia_days.dicts())

        df = DataFrame[WikipediaDaySchema](dicts)

        return df

    except SchemaError as e:
        print(e)
        return None


if __name__ == "__main__":
    sqlite_db_connect()

    print("Movies")

    calc = calculate_movie_frame()

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
