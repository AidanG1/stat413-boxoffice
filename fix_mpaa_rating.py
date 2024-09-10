# I messed up the mpaa rating reason in the database, so go through the movies in detail_html and fix the mpaa rating reason in the database

from bs4 import BeautifulSoup
from db import sqlite_db_connect, Movie
from scrape_helpers_detail import get_mpaa_rating
import bs4
import os

if __name__ == "__main__":
    sqlite_db_connect()

    detail_html_dir = "detail_html"

    for filename in os.listdir(detail_html_dir)[2000:]:
        slug = filename.split(".")[0]

        movie = Movie.get_or_none(slug=slug)

        if movie is None:
            print(f"Movie with slug {slug} not found")
            continue

        with open(os.path.join(detail_html_dir, filename), "r") as f:
            html = f.read()

        soup = BeautifulSoup(html, "html.parser")

        main = soup.find("div", {"id": "main"})

        if main is None:
            print(f"No div with id main")
            continue

        # check if main is NavigableString and not Tag
        if not isinstance(main, bs4.element.Tag):
            print(f"main is not a Tag")
            continue

        # find a h2 with text "Movie Details"

        movie_details = main.find_all("h2")

        for h2 in movie_details:
            if h2.text == "Movie Details":
                break

        # find the table that follows the h2
        table = h2.find_next("table")

        tbody = table.find("tbody")

        # tbody can be done, in which case the rows are just inside the <table />

        if tbody is None:
            rows = table.find_all("tr")
        else:
            rows = tbody.find_all("tr")

        for row in rows:
            columns = row.find_all("td")

            row_title = columns[0].text

            # print(row_title)
            if row_title == "MPAA Rating:":
                mpaa_rating = get_mpaa_rating(columns[1])

                break
        
        if mpaa_rating is None:
            print(f"No MPAA rating found for {slug}")
            continue

        if mpaa_rating.reason == movie.mpaa_rating_reason:
            print(f"MPAA rating for {slug} is already {mpaa_rating.reason}")
        else:
            print(f"MPAA rating for {slug} is {movie.mpaa_rating_reason}")

            movie.mpaa_rating_reason = mpaa_rating.reason

            movie.save()

            print(f"Updated MPAA rating for {slug} to {mpaa_rating.reason}")