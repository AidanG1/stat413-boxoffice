# deadpool is movie id 1, make a graph of all of its box office days

import matplotlib.pyplot as plt
import seaborn as sns
from boxoffice.db.frames import get_box_office_day_frame

bodf = get_box_office_day_frame()

if bodf is not None:
    deadpool_df = bodf[bodf["movie"] == 1]

    deadpool_df = deadpool_df.sort_values("date")

    plt.figure(figsize=(12, 6))

    sns.lineplot(x="date", y="revenue", data=deadpool_df)

    plt.title("Deadpool Box Office Revenue by Day")

    plt.ylabel("Revenue")

    plt.xlabel("Date")

    print(deadpool_df)

    # make y axis values correct
    plt.ticklabel_format(style="plain", axis="y")

    plt.show()
