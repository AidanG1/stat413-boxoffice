from boxoffice.db.db import sqlite_db_connect, Movie
from boxoffice.scrape.scrape_helpers_detail import get_synopsis
from bs4 import BeautifulSoup
import os

detail_html_dir = "boxoffice/scrape/detail_html"

if __name__ == "__main__":
    sqlite_db_connect()
    movies = Movie.select()

    for movie in movies:
        if os.path.exists(f"{detail_html_dir}/{movie.slug}.html"):
            with open(f"{detail_html_dir}/{movie.slug}.html", "r") as f:
                text = f.read()

        soup = BeautifulSoup(text, "html.parser")

        main = soup.find("div", {"id": "main"})

        if main is None:
            print(f"No div with id main")
            continue

        synopsis = get_synopsis(main)

        if synopsis is None:
            print(f"Could not get synopsis")
            continue

        old_length = len(movie.synopsis)

        movie.synopsis = synopsis

        print(
            f"Updated synopsis for {movie.title} from {old_length} to {len(synopsis)}"
        )

        movie.save()
