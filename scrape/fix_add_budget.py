# I messed up the mpaa rating reason in the database, so go through the movies in detail_html and fix the mpaa rating reason in the database

from bs4 import BeautifulSoup
from ..db.db import sqlite_db_connect, Movie
from scrape_helpers_detail import get_budget
import bs4
import os

if __name__ == "__main__":
    sqlite_db_connect()

    detail_html_dir = "detail_html"

    for filename in os.listdir(detail_html_dir)[:]:
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

        budget = get_budget(main)

        if budget is None:
            print(f"No budget found for {slug}")
            continue

        movie.budget = budget

        print(f"Set budget for {slug} to {budget}")

        movie.save()