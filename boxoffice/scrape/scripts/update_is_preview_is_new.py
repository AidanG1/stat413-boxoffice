# loop through all values and update the is_preview and is_new based on scraping

from tabnanny import verbose
from boxoffice.db.db import BoxOfficeDay, sqlite_db_connect, Movie
from bs4 import BeautifulSoup, Tag
from boxoffice.scrape.scrape_helpers_daily import (
    get_movie_title_and_slug,
    get_preview,
    get_new,
)

if __name__ == "__main__":
    sqlite_db_connect()
    dates = BoxOfficeDay.select(BoxOfficeDay.date).distinct()
    print("Found", len(dates), "dates")
    for date in dates:
        html_name = f"{date.date}.html"

        with open(f"boxoffice/scrape/daily_html/{html_name}", "r") as f:
            html = f.read()

        soup = BeautifulSoup(html, "html.parser")

        table_id = "box_office_daily_table"

        table = soup.find("table", {"id": table_id})

        if table is None:
            print(f"No table with id {table_id}")
            continue

        tbody = table.find("tbody")

        if tbody is None:
            print(f"No tbody in table with id {table_id}")
            continue

        if type(tbody) != Tag:
            print(f"tbody is not a Tag")
            continue

        rows = tbody.find_all("tr")

        print("Found", len(rows), "rows")

        for row in rows:
            columns = row.find_all("td")

            # the second column contains information about whether the movie is a preview
            is_preview = get_preview(columns[1])

            is_new = get_new(columns[1])

            # now need to find the row in the database and update it
            movie_name_slug = get_movie_title_and_slug(columns[2], verbose=False)

            if movie_name_slug is None:
                print("Could not get movie name and slug")
                continue

            movie_id = Movie.get_or_none(slug=movie_name_slug.slug)

            if movie_id is None:
                print("Could not find movie with slug", movie_name_slug.slug)
                continue

            BoxOfficeDay.update(is_preview=is_preview, is_new=is_new).where(
                BoxOfficeDay.movie == movie_id, BoxOfficeDay.date == date.date
            ).execute()

            if is_preview or is_new:
                print(
                    "Updated",
                    movie_name_slug.name,
                    "is_preview to",
                    is_preview,
                    "is_new to",
                    is_new,
                )

    print("Done")
