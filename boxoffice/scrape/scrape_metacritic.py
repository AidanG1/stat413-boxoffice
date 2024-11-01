from boxoffice.colors import bcolors
from boxoffice.db.db import BoxOfficeDay, Movie, MovieMetacritic
from boxoffice.scrape.requests_session import s
from bs4 import BeautifulSoup
from typing import TypedDict
import datetime, re


class MetacriticCriticScoreSummary(TypedDict):
    score: int
    url: str


class MetacriticReviewedProduct(TypedDict):
    id: int
    type: str
    title: str
    url: str
    criticScoreSummary: MetacriticCriticScoreSummary


class MetacriticItem(TypedDict):
    quote: str
    score: int
    url: str
    date: str
    author: str
    authorSlug: str
    image: str | None
    publicationName: str
    publicationSlug: str
    reviewedProduct: MetacriticReviewedProduct


class MetacriticData(TypedDict):
    id: int
    totalResults: int
    items: list[MetacriticItem]


class MetacriticLink(TypedDict):
    href: str


class MetacriticFilterSortOption(TypedDict):
    label: str
    value: str
    href: str


class MetacriticLinks(TypedDict):
    self: MetacriticLink
    next: MetacriticLink
    first: MetacriticLink
    last: MetacriticLink
    filterOptions: list[MetacriticFilterSortOption]
    sortOptions: list[MetacriticFilterSortOption]


class MetacriticMeta(TypedDict):
    componentName: str
    componentDisplayName: str
    componentType: str


class MetacriticResults(TypedDict):
    data: MetacriticData
    links: MetacriticLinks
    meta: MetacriticMeta


def get_api_data_method_1(slug1: str, slug2: str) -> tuple[MetacriticResults, str]:
    # first need to see if slug2 exists on metacritic, if yes that is the correct slug, otherwise use slug 1
    url = f"https://www.metacritic.com/movie/{slug2}/critic-reviews/"

    r = s.get(url)

    if r.status_code == 200:
        correct_slug = slug2
    else:
        correct_slug = slug1
        r = s.get(f"https://www.metacritic.com/movie/{slug1}/critic-reviews/")

    soup = BeautifulSoup(r.text, "html.parser")

    # get the body
    body = soup.find("body")
    # get the first script tag in the body
    script = body.find("script")

    # target url: https://internal-prod.apigee.fandom.net/v1/xapi/reviews/metacritic/critic/movies/little-women-2019/web?apiKey=1MOZgmNFxvmljaQR1X9KAij9Mo4xAY3u&offset=0&limit=100&filterBySentiment=all&sort=publication&componentName=critic-reviews&componentDisplayName=critic%20Reviews&componentType=ReviewList

    # get the contents of the script tag
    script_contents = script.string

    # if type(script_contents) != type(''):
    #     print(f"Script contents is not a string for {movie}")
    #     # print(script_contents)
    #     print(type(script_contents))
    #     continue

    # write script contents to a file
    with open(f"boxoffice/scrape/metacritic/{correct_slug}.txt", "w") as f:
        f.write(script_contents)

    # find the url that starts with https://internal-prod.apigee.fandom.net/v1/xapi/reviews/metacritic/critic/movies/
    # raw_search = r'https://internal-prod.apigee.fandom.net/v1/xapi/reviews/metacritic/critic/movies/.*/web\?apiKey=.*&offset=0&limit=50&filterBySentiment=all&sort=.*&componentName=critic-reviews&componentDisplayName=critic%20Reviews&componentType=ReviewList'
    # https:\u002F\u002Finternal-prod.apigee.fandom.net\u002Fv1\u002Fxapi\u002Freviews\u002Fmetacritic\u002Fcritic\u002Fmovies\u002Fdeadpool-wolverine\u002Fweb?apiKey=1MOZgmNFxvmljaQR1X9KAij9Mo4xAY3u&offset=0&limit=50&filterBySentiment=all&sort=score&componentName=critic-reviews&componentDisplayName=critic%20Reviews&componentType=ReviewList
    # https:\u002F\u002Finternal-prod.apigee.fandom.net\u002Fv1\u002Fxapi\u002Freviews\u002Fmetacritic\u002Fcritic\u002Fmovies\u002Fdeadpool-wolverine\u002Fweb?apiKey=1MOZgmNFxvmljaQR1X9KAij9Mo4xAY3u&offset=0&limit=50&filterBySentiment=all&sort=publication&componentName=critic-reviews&componentDisplayName=critic%20Reviews&componentType=ReviewList
    # search = raw_search.replace('/', r'\\u002F')
    # url = re.search(search, script_contents).group()

    api_key = re.search(r"apiKey=(.*?)&", script_contents).group(1)

    metacritic_url = f"https://internal-prod.apigee.fandom.net/v1/xapi/reviews/metacritic/critic/movies/{correct_slug}/web?apiKey={api_key}&offset=0&limit=100&filterBySentiment=all&sort=publication&componentName=critic-reviews&componentDisplayName=critic%20Reviews&componentType=ReviewList"
    print(metacritic_url)

    # get the json data from the url
    r = s.get(metacritic_url)

    # write the json data to a file
    with open(f"boxoffice/scrape/metacritic/{correct_slug}.json", "w") as f:
        f.write(r.text)

    r_json = r.json()

    return r_json, correct_slug


def get_api_data_method_2(slug1: str, slug2: str) -> tuple[MetacriticResults, str]:
    api_key = "1MOZgmNFxvmljaQR1X9KAij9Mo4xAY3u"

    metacritic_url = f"https://internal-prod.apigee.fandom.net/v1/xapi/reviews/metacritic/critic/movies/{slug2}/web?apiKey={api_key}&offset=0&limit=100&filterBySentiment=all&sort=publication&componentName=critic-reviews&componentDisplayName=critic%20Reviews&componentType=ReviewList"

    # get the json data from the url
    r = s.get(metacritic_url)

    if r.status_code == 200:
        correct_slug = slug2
    else:
        correct_slug = slug1
        metacritic_url = f"https://internal-prod.apigee.fandom.net/v1/xapi/reviews/metacritic/critic/movies/{slug1}/web?apiKey={api_key}&offset=0&limit=100&filterBySentiment=all&sort=publication&componentName=critic-reviews&componentDisplayName=critic%20Reviews&componentType=ReviewList"
        r = s.get(metacritic_url)

    print(metacritic_url)

    # write the json data to a file
    with open(f"boxoffice/scrape/metacritic/{correct_slug}.json", "w") as f:
        f.write(r.text)

    r_json = r.json()

    return r_json, correct_slug


movie_title_manual_corrections = {
    "Horizon: An American Saga Chapter 1": "Horizon: An American Saga - Chapter 1",
    "The Hunger Games: The Ballad of Songbirds & Snakes": "The Hunger Games: The Ballad of Songbirds and Snakes",
    "TAYLOR SWIFT | THE ERAS TOUR": "Taylor Swift: The Eras Tour",
    "Mission: Impossible Dead Reckoning Part One": "Mission: Impossible – Dead Reckoning",
    "Mission: Impossible—Rogue Nation": "Mission: Impossible - Rogue Nation",
    "Shaun the Sheep": "Shaun the Sheep Movie",
    "Steve Jobs: The Man in the Machine": "Steve Jobs: Man in the Machine",
    "Star Wars Ep. VII: The Force Awakens": "Star Wars: Episode VII - The Force Awakens",
    "The Conjuring 2: The Enfield Poltergeist": "The Conjuring 2",
    "Tyler Perry’s Boo! A Madea Halloween": "Boo! A Madea Halloween",
    "John Wick: Chapter Two": "John Wick: Chapter 2",
    "Power Rangers": "Saban's Power Rangers",
    "The Boondock Saints 2: All Saints Day": "The Boondock Saints II: All Saints Day",
}


if __name__ == "__main__":
    metacritic_movies = MovieMetacritic.select()
    metacritic_movie_ids = [mcm.movie for mcm in metacritic_movies]
    movies: list[Movie] = Movie.select().where(Movie.id.not_in(metacritic_movie_ids))
    for movie in movies[1000:2000]:
        # if release year is before 2004, skip
        if movie.release_year < 2004:
            print(f"{bcolors.OKCYAN}Skipping {movie.title} ({movie.release_year}) due to release year{bcolors.ENDC}")
            continue

        movie_title = movie.title
        if movie_title in movie_title_manual_corrections:
            print(f"Correcting {movie_title} to {movie_title_manual_corrections[movie_title]}")
            movie_title = movie_title_manual_corrections[movie_title]

        movie_title = movie_title.lower()

        # if there are any non-ascii characters in parentheses, remove them
        if "(" in movie_title and ")" in movie_title:
            match = re.search(r"\((.*?)\)", movie_title)
            if match is not None:
                if not all(ord(char) < 128 for char in match.group(1)):
                    movie_title = movie_title.replace(f" ({match.group(1)})", "")

        # generate the metacritic slug
        slug1 = (
            movie_title.replace(":", "")
            .replace("'", "")
            .replace(",", "")
            .replace("/", "")
            .replace(".", "")
            .replace("?", "")
            .replace("$", "")
            # .replace("!", "")
            .replace("& ", "")
            .replace("&", "")
            .replace("’", "")
            .replace("(", "")
            .replace(")", "")
            .replace(" ", "-")
            .replace("ì", "i")
            .replace("é", "e")
            .replace("è", "e")
            .replace("á", "a")
            .replace("ó", "o")
            .replace("ú", "u")
            .replace("ñ", "n")
            .replace("ç", "c")
            .replace("â", "a")
            .replace("ô", "o")
            .replace("û", "u")
            .replace("ä", "a")
            .replace("ö", "o")
            .replace("ü", "u")
            .replace("ë", "e")
            .replace("ï", "i")
            .replace("á", "a")
            .replace("í", "i")
            .replace("ó", "o")
        )
        slug2 = slug1 + "-" + str(movie.release_year)
        print(f"Scraping Metacritic for {movie.title} ({movie.release_year})")

        # Scrape Metacritic, using the information we just got
        metacritic_scores = []
        metacritic_monday_before_wide_friday_calculateds = []
        metacritic_before_wide_friday_calculateds = []
        metacritic_before_first_day_calculateds = []

        first_day = None
        monday_before_wide_release = None
        wide_friday = None

        # need to get the values for first day, before wide release, and monday before wide release
        box_office_days = BoxOfficeDay.select().where(BoxOfficeDay.movie == movie.id).order_by(BoxOfficeDay.date)

        first_day = box_office_days[0].date

        for box_office_day in box_office_days:
            if (
                box_office_day.date.weekday() == 4
                and box_office_day.theaters is not None
                and box_office_day.theaters > 1000
            ):
                wide_friday = box_office_day.date
                break

        if wide_friday is None:
            wide_friday = first_day
        monday_before_wide_release = wide_friday - datetime.timedelta(days=3)

        # get the json data
        data, correct_slug = get_api_data_method_2(slug1, slug2)

        if "data" not in data:
            print(f"{bcolors.FAIL}No data found for {movie.title} ({movie.release_year}){bcolors.ENDC}")
            continue

        reviews = data["data"]["items"]

        publication_fail_printed = False

        for review in reviews:
            # get the score
            score = review["score"]
            # get the publication date
            publication_date = review["date"]  # 2024-07-28
            if publication_date is None:
                if not publication_fail_printed:
                    print(
                        f"{bcolors.WARNING}Reviews with no publication date found for {movie.title} ({movie.release_year}){bcolors.ENDC}"
                    )
                    publication_fail_printed = True
                continue
            parsed_date = datetime.datetime.strptime(publication_date, "%Y-%m-%d").date()

            # always add to metacritic_scores
            metacritic_scores.append(score)

            # if the publication date is before the first day
            if parsed_date < first_day:
                metacritic_before_first_day_calculateds.append(score)

            # if the publication date is before the wide friday
            if parsed_date < wide_friday:
                metacritic_before_wide_friday_calculateds.append(score)

            # if the publication date is before the monday before the wide friday
            if parsed_date < monday_before_wide_release:
                metacritic_monday_before_wide_friday_calculateds.append(score)

        # calculate the average scores
        if len(metacritic_scores) > 0:
            metacritic_score = sum([int(score) for score in metacritic_scores]) / len(metacritic_scores)
        else:
            metacritic_score = None
        if len(metacritic_before_first_day_calculateds) > 0:
            metacritic_before_first_day_calculated = sum(
                [int(score) for score in metacritic_before_first_day_calculateds]
            ) / len(metacritic_before_first_day_calculateds)
        else:
            metacritic_before_first_day_calculated = None
        if len(metacritic_monday_before_wide_friday_calculateds) > 0:
            metacritic_monday_before_wide_friday_calculated = sum(
                [int(score) for score in metacritic_monday_before_wide_friday_calculateds]
            ) / len(metacritic_monday_before_wide_friday_calculateds)
        else:
            metacritic_monday_before_wide_friday_calculated = None
        if len(metacritic_before_wide_friday_calculateds) > 0:
            metacritic_before_wide_friday_calculated = sum(
                [int(score) for score in metacritic_before_wide_friday_calculateds]
            ) / len(metacritic_before_wide_friday_calculateds)
        else:
            metacritic_before_wide_friday_calculated = None

        metacritic_score_official = None
        if len(reviews) > 0:
            metacritic_score_official = reviews[0]["reviewedProduct"]["criticScoreSummary"]["score"]
        metacritic_review_count = data["data"]["totalResults"]

        # Save to MovieMetacritic
        MovieMetacritic.create(
            movie=movie,
            metacritic_slug=correct_slug,
            metacritic_score=metacritic_score_official,
            metacritic_review_count=metacritic_review_count,
            metacritic_score_calculated=metacritic_score,
            metacritic_before_first_day_calculated=metacritic_before_first_day_calculated,
            metacritic_monday_before_wide_friday_calculated=metacritic_monday_before_wide_friday_calculated,
            metacritic_before_wide_friday_calculated=metacritic_before_wide_friday_calculated,
        )
