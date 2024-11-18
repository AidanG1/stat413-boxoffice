from boxoffice.db.db import Movie, BoxOfficeDay, WikipediaDay
import requests, datetime
from typing import TypedDict
from boxoffice.scrape.requests_session import s
from boxoffice.colors import bcolors


# core goal is to scrape the wikipedia page views 60 days before release and every day that the movie is out
class WikipediaPageView(TypedDict):
    project: str
    article: str
    granularity: str
    timestamp: str
    access: str
    agent: str
    views: int


class WikipediaPageViews(TypedDict):
    items: list[WikipediaPageView]


# example url: https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/Joker:_Folie_%C3%A0_Deux/daily/20240901/20241008


def convert_date_to_string(date: datetime.date):
    return date.strftime("%Y%m%d00")


def get_wikipedia_url(wikipedia_key: str, start_date: datetime.date, end_date: datetime.date):
    start_date_str = convert_date_to_string(start_date)
    end_date_str = convert_date_to_string(end_date)

    return f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/{wikipedia_key}/daily/{start_date_str}/{end_date_str}"


def get_start_date_end_date(movie: Movie) -> tuple[datetime.date, datetime.date]:
    max_wikipedia_days = 365 + 60
    box_office_days = BoxOfficeDay.select().where(BoxOfficeDay.movie == movie).order_by(BoxOfficeDay.date.asc())

    # get the start date
    start_date = box_office_days[0].date - datetime.timedelta(days=60)

    # get the end date
    end_date = box_office_days[-1].date

    if (end_date - start_date).days > max_wikipedia_days:
        end_date = start_date + datetime.timedelta(days=max_wikipedia_days)

    return start_date, end_date


def request_wikipedia_page_views(url: str, title: str) -> list[WikipediaPageView]:
    # get the response
    response = s.get(url)

    # get the json
    data: WikipediaPageViews = response.json()

    if "items" not in data:
        # print in red, no items for the movie
        print(f"{bcolors.FAIL}no items for {title}{bcolors.ENDC} with url {url}")
        if response.status_code == 429:
            print(response.text)
            print(response.status_code)
            print(response.headers)
            exit()
        return

    # get the items
    items = data["items"]

    return items


def get_wikipedia_items(movie: Movie) -> list[WikipediaPageView]:
    # get the start date and end date
    start_date, end_date = get_start_date_end_date(movie)

    # get the wikipedia key
    wikipedia_key: str = str(movie.wikipedia_key)

    if wikipedia_key is None:
        print(f"no wikipedia key for {movie.title}")
        return None

    url = get_wikipedia_url(wikipedia_key, start_date, end_date)

    # get the items
    items = request_wikipedia_page_views(url, movie.title)

    return items


def create_wikipedia_items(movie: Movie, items: list[WikipediaPageView]):
    wikipedia_days: list[WikipediaDay] = []

    for item in items:
        date = datetime.datetime.strptime(item["timestamp"], "%Y%m%d00")
        date = datetime.date(date.year, date.month, date.day)
        views = item["views"]

        # create the wikipedia day
        wikipedia_day = WikipediaDay.create(
            date=date,
            views=views,
            movie=movie,
        )

        wikipedia_days.append(wikipedia_day)

    # verify that the date and movie are unique together
    wikipedia_days = list(set(wikipedia_days))

    # save the wikipedia days
    for wikipedia_day in wikipedia_days:
        wikipedia_day.save()

    print(f"created {len(wikipedia_days)} wikipedia days for {movie.title}")

    return wikipedia_days


def get_wikipedia_page_views(movie: Movie, existing_check: bool = True):
    # get the existing wikipedia days
    if existing_check:
        existing_wikipedia_days = WikipediaDay.select().where(WikipediaDay.movie == movie)

        if existing_wikipedia_days.count() > 0:
            print(f"already have wikipedia days for {movie.title}")
            return

    # get the items
    items = get_wikipedia_items(movie)

    if items is None:
        print(f"no items for {movie.title}")
        return

    # create the wikipedia items
    wikipedia_days = create_wikipedia_items(movie, items)

    return wikipedia_days


if __name__ == "__main__":
    movies = Movie.select().where(Movie.wikipedia_key.is_null(False))
    for movie in movies:
        get_wikipedia_page_views(movie)
