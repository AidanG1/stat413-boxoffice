from boxoffice.db.frames import get_movie_frame_full
import matplotlib.pyplot as plt
import seaborn as sns

df = get_movie_frame_full()

if df is not None:
    # goal is to make a scatter plot of the weighted_cast_median_box_office against total_revenue_within_365_days
    print(df.columns)

    sns.scatterplot(x="weighted_cast_median_box_office", y="total_revenue_within_365_days", data=df)

    sns.scatterplot(x="weighted_cast_mean_box_office", y="total_revenue_within_365_days", data=df, c="green")

    # get the correlation
    corr = df["weighted_cast_median_box_office"].corr(df["total_revenue_within_365_days"])
    corr_mean = df["weighted_cast_mean_box_office"].corr(df["total_revenue_within_365_days"])
    corr_crew = df["weighted_crew_median_box_office"].corr(df["total_revenue_within_365_days"])
    corr_crew_mean = df["weighted_crew_mean_box_office"].corr(df["total_revenue_within_365_days"])
    corr_director = df["director_median_box_office"].corr(df["total_revenue_within_365_days"])
    corr_director_mean = df["director_mean_box_office"].corr(df["total_revenue_within_365_days"])

    print(
        f"Correlation cast median: {corr}, Correlation cast mean: {corr_mean}, Correlation crew median: {corr_crew}, Correlation crew mean: {corr_crew_mean}, Correlation director median: {corr_director}, Correlation director mean: {corr_director_mean}"
    )

    plt.show()
