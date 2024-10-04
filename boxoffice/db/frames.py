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
)
from pandera.errors import SchemaError
from pandera.typing import DataFrame
from peewee import fn, JOIN
import datetime
import os
import pandas as pd
import pandera as pa

MOVIES_CSV_PATH = "boxoffice/db/data/movies.csv"


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
    release_day: datetime.date = pa.Field()
    release_day_non_preview: datetime.date = pa.Field()
    largest_theater_count: int = pa.Field(
        ge=0, nullable=True
    )  # this shouldn't be nullable but somehow there is one case where it is
    days_over_1000_theaters: int = pa.Field(ge=0)
    days_over_1000000_revenue: int = pa.Field(ge=0)
    days_over_100000_revenue: int = pa.Field(ge=0)
    preview_sum: float = pa.Field(
        ge=0, nullable=True
    )  # some movies don't have previews


class JoinedMovieSchema(MovieSchemaWithBoxOffice):
    distributor_name: str = pa.Field()
    distributor_slug: str = pa.Field()
    distributor_id: int = pa.Field(ge=0)
    franchise_name: str = pa.Field(nullable=True)
    franchise_slug: str = pa.Field(nullable=True)
    franchise_id: float = pa.Field(
        ge=0, nullable=True
    )  # why is this a float? I don't want it to be but things break otherwise


class MovieCompleteSchema(JoinedMovieSchema):
    release_day_of_week: int = pa.Field()  # 0 is Monday, 6 is Sunday
    release_day_of_week_non_preview: int = pa.Field()  # 0 is Monday, 6 is Sunday
    release_month: int = pa.Field()  # 1 is January, 12 is December
    release_day_of_month: int = (
        pa.Field()
    )  # 1 is the first day of the month, 31 is the last day of the month
    opening_weekend_revenue: int = pa.Field(
        ge=0
    )  # this shouldn't be nullable but somehow there is one case where it is
    # largest_weekend_revenue: float = pa.Field(ge=0)
    # largest_weekend_release_week: int = pa.Field(ge=0)
    first_five_days_revenue: float = pa.Field(ge=0)
    first_seven_days_revenue: float = pa.Field(ge=0)
    preview_to_weekend_ratio: float = pa.Field(
        ge=0, nullable=True
    )  # some movies don't have previews
    total_revenue_within_365_days: int = pa.Field(ge=0)
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
        print("Reading from movies.csv")
        df = pd.read_csv(MOVIES_CSV_PATH)

        # convert release_day and release_day_non_preview to datetime
        df["release_day"] = pd.to_datetime(df["release_day"]).dt.date
        df["release_day_non_preview"] = pd.to_datetime(
            df["release_day_non_preview"]
        ).dt.date

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
        )
        .join(BoxOfficeDay, on=(Movie.id == BoxOfficeDay.movie))
        .group_by(Movie.id)
        .join_from(Movie, MovieDistributor)
        .join_from(Movie, MovieFranchise, JOIN.LEFT_OUTER)
        .join_from(MovieDistributor, Distributor)
        .join_from(MovieFranchise, Franchise, JOIN.LEFT_OUTER)
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

    movies_df = DataFrame[JoinedMovieSchema](dicts)

    # within synopsis, replace commas and newlines
    movies_df["synopsis"] = movies_df["synopsis"].str.replace(",", "%2C")
    movies_df["synopsis"] = movies_df["synopsis"].str.replace("\n", "%0A")

    kept_ids = movies_df["id"]

    print(
        f"There are {len(kept_ids)} movies in the movie dataframe, now filtering out the box office days"
    )

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

    print(
        f"Filtered out {prior_len - len(bodf)} box office days, there are now {len(bodf)} box office days"
    )

    # add the columns to the df
    # copy the movies_df but without any typing
    df = movies_df.copy()

    dates = bodf.groupby("movie")["date"]

    df["release_day_of_week"] = df["release_day"].apply(lambda x: x.weekday())

    df["release_day_of_week_non_preview"] = df["release_day_non_preview"].apply(
        lambda x: x.weekday()
    )

    df["release_month"] = df["release_day_non_preview"].apply(lambda x: x.month)

    df["release_day_of_month"] = df["release_day_non_preview"].apply(lambda x: x.day)

    # get the opening weekend revenue for each movie. This is the sum of the first Friday, Saturday, and Sunday plus Thursday if there was a preview. Movies may not open on a Friday, so need to specifically get the first of each of these
    # first_five_of_each_day = []
    # first_each_day = []
    # total_each_day = []
    # is_preview = []
    # for weekday in range(7):
    #     days = (
    #         bodf.where(bodf["day_of_week"] == weekday)
    #         .sort_values("date")
    #         .groupby("movie")
    #     )

    #     first_five_of_each_day.append(days["revenue"].head(5).sum())
    #     first_each_day.append(days["revenue"].head(1).sum())
    #     total_each_day.append(days["revenue"].sum())
    #     is_preview.append(days["is_preview"].head(1).sum())

    first_five_by_weekday = []
    first_by_weekday = []
    total_by_weekday = []
    is_preview_by_weekday = []

    for weekday in range(7):
        days = (
            bodf[bodf["day_of_week"] == weekday]
            .sort_values("date")
            .reset_index(drop=True)
            .groupby("movie")
        )

        first_five_by_weekday.append(
            days.apply(lambda x: x.head(5)["revenue"].sum(), include_groups=False)
        )
        first_by_weekday.append(
            days.apply(lambda x: x.head(1)["revenue"].sum(), include_groups=False)
        )
        total_by_weekday.append(
            days.apply(lambda x: x["revenue"].sum(), include_groups=False)
        )
        is_preview_by_weekday.append(
            days.apply(lambda x: x.head(1)["is_preview"].sum(), include_groups=False)
        )

    # opening weekend revenue is the sum of the first Friday, Saturday, and Sunday plus Thursday if there was a preview
    opening_weekend_revenue = (
        first_by_weekday[4] + first_by_weekday[5] + first_by_weekday[6]
    ).reset_index(drop=True)

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
        bodf.where(bodf["date"] <= bodf["date"] + datetime.timedelta(days=365))
        .groupby("movie")["revenue"]
        .sum()
        .reset_index(drop=True)
    )

    # get the opening weekend to total ratio for each movie
    opening_weekend_to_total_ratio = (
        opening_weekend_revenue / total_revenue_within_365_days
    )
    opening_weekend_to_total_ratio = opening_weekend_to_total_ratio.reset_index(
        drop=True
    )

    # now get the ratios for each day of the week
    first_five_ratios = []

    for i in range(7):
        first_five_ratios.append(
            (first_five_by_weekday[i] / first_five_by_weekday[i - 1]).reset_index(
                drop=True
            )
        )

    # now get the ratios for each day of the week
    ratios = []

    for i in range(7):
        ratios.append(
            (total_by_weekday[i] / total_by_weekday[i - 1]).reset_index(drop=True)
        )

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
