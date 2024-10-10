from boxoffice.db.db import Movie
import re, requests
from typing import NamedTuple, TypedDict
from boxoffice.colors import bcolors
from boxoffice.scrape.requests_session import s


class WikipediaInfo(NamedTuple):
    id: int
    key: str


class ScrapeThumbnail(TypedDict):
    mimetype: str
    width: int
    height: int
    duration: int | None
    url: str


class ScrapeResult(TypedDict):
    id: int
    key: str
    title: str
    excerpt: str
    matched_title: str | None
    description: str
    thumbnail: ScrapeThumbnail | None


class ScrapeResults(TypedDict):
    pages: list[ScrapeResult]


LANGUAGE_CODE = "en"

BASE_URL = "https://api.wikimedia.org/core/v1/wikipedia/"
ENDPOINT = "/search/page"


def get_wikipedia_information(
    s: requests.Session, movie_title: str, movie_year: int
) -> ScrapeResult | None:
    movie_title = movie_title.replace("&", "and")
    r = s.get(
        f"{BASE_URL}{LANGUAGE_CODE}{ENDPOINT}?q={movie_title} {movie_year}&limit=10",
    )
    data: ScrapeResults = r.json()
    results = data["pages"]

    if len(results) == 0:
        print(f"No results for {movie_title}")
        raise Exception("No results found")

    # first priority is a match with "title (year film)"
    for res in results:
        if f"{movie_title}" in res["title"] and (
            f"({movie_year} film)" in res["title"]
            or f"({movie_year - 1} film)" in res["title"]
        ):
            return res

    # second priority is description check
    raw = r"(\d{4}).*film"

    for res in results:
        if res["description"] is None:
            continue
        match = re.match(raw, res["description"])
        if match is not None:
            if (
                int(match.group(1)) == movie_year
                or int(match.group(1)) == movie_year - 1
            ):  # sometimes the year is off by one
                return res

    # next check for film) in page key, just pick the first one
    for res in results:
        if "film)" in res["key"]:
            return res
    # then search for the year
    for res in results:
        if str(movie_year) in res["key"]:
            return res
    # then see if there is a result with (film) in the top 10
    for res in results[:10]:
        if "(film)" in res["key"]:
            return res
    # then search for just the title
    for res in results:
        if movie_title in res["key"]:
            return res
    return None


if __name__ == "__main__":
    for movie in Movie.select()[100:120]:
        if movie.wikipedia_key is not None:
            # continue
            pass
        try:
            wikipedia_info = get_wikipedia_information(
                s, movie.title, movie.release_year
            )
            if wikipedia_info is None:
                print(
                    f"{bcolors.WARNING}No results for {movie.title}, {movie.release_year}{bcolors.ENDC}"
                )
                continue
            print(f"{movie.title}, {movie.release_year}: {wikipedia_info['key']}")
            Movie.update(
                wikipedia_key=wikipedia_info["key"], wikipedia_id=wikipedia_info["id"]
            ).where(Movie.id == movie.id).execute()
        except Exception as e:
            print(
                f"{bcolors.FAIL}Error with {movie.title}, {movie.release_year}: {e}{bcolors.ENDC}"
            )
            continue
