from boxoffice.db.frames import get_movie_frame_full
import datetime
import pandas as pd
import numpy as np

df = get_movie_frame_full()

if df is None:
    print("No data")
    exit()

df = df.dropna(subset=["budget"])
df = df.drop(columns=["opening_weekend_revenue"])
df = df[df["release_day"] >= datetime.date(2015, 9, 1)]
dummies = pd.get_dummies(
    df[["mpaa_rating", "genre", "creative_type", "source", "production_method", "distributor_slug"]], drop_first=True
)
df = pd.concat([df, dummies], axis=1)

# within the dummy columns, rename any with spaces or hyphens to use underscores
df.columns = df.columns.str.replace(" ", "_")
df.columns = df.columns.str.replace("-", "_")
df.columns = df.columns.str.replace("/", "")

df["in_franchise"] = df["franchise_slug"].notnull().astype(int)

# filter for only positive opening_wide_revenue
df = df[df["opening_wide_revenue"] > 0]

# drop preview_sum and preview_to_weekend_ratio
df = df.drop(
    columns=[
        "preview_sum",
        "preview_to_weekend_ratio",
        "first_five_days_revenue",
        "first_seven_days_revenue",
        "total_revenue_within_365_days",
        "opening_weekend_to_total_ratio",
        "fri_sat_ratio_first_five",
        "sat_sun_ratio_first_five",
        "sun_mon_ratio_first_five",
        "mon_tue_ratio_first_five",
        "tue_wed_ratio_first_five",
        "wed_thu_ratio_first_five",
        "thu_fri_ratio_first_five",
        "fri_sat_ratio",
        "sat_sun_ratio",
        "sun_mon_ratio",
        "mon_tue_ratio",
        "tue_wed_ratio",
        "wed_thu_ratio",
        "thu_fri_ratio",
        "total_box_office",
        "largest_theater_count",
        "days_over_1000_theaters",
        "days_over_1000000_revenue",
        "days_over_100000_revenue",
        "wikipedia_cumulative_views",
        "metacritic_score",
        "metacritic_score_calculated",
        "metacritic_before_first_day_calculated",
    ]
)

# fill na values with 0
df = df.fillna(0)

X_train = df[(df["release_day"] < datetime.date(2023, 1, 1))]
X_test = df[df["release_day"] >= datetime.date(2023, 1, 1)]

y_train = X_train["opening_wide_revenue"]
y_test = X_test["opening_wide_revenue"]

X_train = X_train.drop(columns=["opening_wide_revenue"])
X_test = X_test.drop(columns=["opening_wide_revenue"])

# reset index
X_train = X_train.reset_index(drop=True)
X_test = X_test.reset_index(drop=True)
y_train = y_train.reset_index(drop=True)
y_test = y_test.reset_index(drop=True)

X_train_dummies = X_train.select_dtypes(include=[np.number, bool])

# remove franchise id and distributor id and id
X_train_dummies = X_train_dummies.drop(columns=["franchise_id", "distributor_id", "id"])

X_train_dummies = X_train_dummies.fillna(0)

# print the columns that have NaN values
print(X_train_dummies.columns[X_train_dummies.isna().any()])

# Ensure all data is numeric
X_train_dummies = X_train_dummies.astype(float)

# within test, convert bools to ints
X_test_numbers = X_test.select_dtypes(include=[np.number, bool])
X_test_numbers = X_test_numbers.fillna(0)

# Ensure all data is numeric
X_test_numbers = X_test_numbers.astype(float)

X_test = X_test_numbers.combine_first(X_test)
