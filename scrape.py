from bs4 import BeautifulSoup
import datetime
import requests
import os
from db import sqlite_db_connect, sqlite_db as db, Movie, DomesticRelease, BoxOfficeDay, Franchise, Keyword, ProductionCompany, ProductionCountry, CastOrCrew, MovieFranchise, MovieKeyword, MovieProductionCompany, MovieProductionCountry, Language, MovieLanguage
from scrape_helpers_daily import *
from scrape_helpers_detail import *
from scrape_helpers_cast import *
import time

base_url: str = "https://the-numbers.com/box-office-chart/daily/"

daily_html_dir = "daily_html"

detail_html_dir = "detail_html"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

start_date: datetime.date = datetime.date(2024, 9, 1)
end_date: datetime.date = datetime.date(2024, 9, 2)


def daterange(start_date: datetime.date, end_date: datetime.date):
    days = int((end_date - start_date).days)
    for n in range(days):
        yield start_date + datetime.timedelta(n)


if __name__ == "__main__":
    sqlite_db_connect()
    for date in daterange(start_date, end_date):
        start_time = time.time()
        print('Scraping for date:', date)

        response = requests.get(
            f"{base_url}{date.year}/{date.month:02}/{date.day:02}", headers=headers
        )
        # print(response.text)

        with open(f"{daily_html_dir}/{date}.html", "w") as f:
            f.write(response.text)

        soup = BeautifulSoup(response.text, "html.parser")

        table_id = "box_office_daily_table"

        table = soup.find("table", {"id": table_id})

        if table is None:
            print(f"No table with id {table_id}")
            continue

        tbody = table.find("tbody")

        if tbody is None:
            print(f"No tbody in table with id {table_id}")
            continue

        rows = tbody.find_all("tr")

        print('Found', len(rows), 'rows')

        for row in rows:
            columns = row.find_all("td")

            # the third column is the movie title
            movie_name_slug = get_movie_title_and_slug(columns[2])

            if movie_name_slug is None:
                print(f"No movie name and slug")
                continue

            # fourth column is the distributor
            distributor_name_slug = get_distributor(columns[3])

            if distributor_name_slug is None:
                print(f"No distributor name and slug")
                continue

            # fifth column is the gross
            gross = get_gross(columns[4])

            print(gross)

            # eighth column is the theaters
            theaters = get_theaters(columns[7])

            # check if the slug is already in the database
            movie = Movie.get_or_none(slug=movie_name_slug.slug)

            if movie is None:
                print(f"Scraping for {movie_name_slug.name}")

                if os.path.exists(f"{detail_html_dir}/{movie_name_slug.slug}.html"):
                    with open(f"{detail_html_dir}/{movie_name_slug.slug}.html", "r") as f:
                        text = f.read()

                else:
                    r = requests.get(f"https://the-numbers.com/movie/{movie_name_slug.slug}", headers=headers)

                    with open(f"{detail_html_dir}/{movie_name_slug.slug}.html", "w") as f:
                        f.write(r.text)
                    text = r.text

                soup = BeautifulSoup(text, "html.parser")

                main = soup.find("div", {"id": "main"})

                if main is None:
                    print(f"No div with id main")
                    continue

                # check if main is NavigableString and not Tag
                if not isinstance(main, bs4.element.Tag):
                    print(f"main is not a Tag")
                    continue

                h1 = main.find("h1")
                if h1 is None:
                    print(f"No h1 in div with id main")
                    continue

                title = h1.text

                poster_url = get_poster_url(main)

                synopsis = get_synopsis(main)

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

                database_keywords: list[Keyword] = []
                database_languages: list[Language] = []
                database_production_companies: list[ProductionCompany] = []
                database_production_countries: list[ProductionCountry] = []
                db_franchise = None

                for row in rows:
                    columns = row.find_all("td")

                    row_title = columns[0].text

                    # print(row_title)

                    if row_title == 'Domestic Releases:':
                        domestic_releases = get_domestic_releases(columns[1])
                    if row_title == 'MPAA Rating:':
                        mpaa_rating = get_mpaa_rating(columns[1])
                    if row_title == 'Running Time:':
                        running_time = get_running_time(columns[1])
                    if row_title == 'Franchise:':
                        franchise = get_franchise(columns[1])
                        db_franchise = None
                        if franchise is not None:
                            db_franchise = Franchise.get_or_none(slug=franchise.slug)
                            if db_franchise is None:
                                db_franchise = Franchise.create(name=franchise.name, slug=franchise.slug)
                    if row_title == 'Keywords:':
                        keywords = get_keywords(columns[1])

                        database_keywords: list[Keyword] = []

                        for keyword in keywords:
                            db_keyword = Keyword.get_or_none(slug=keyword.slug)
                            if not db_keyword:
                                db_keyword = Keyword.create(name=keyword.name, slug=keyword.slug)
                                database_keywords.append(db_keyword)
                            else:
                                database_keywords.append(db_keyword)
                    if row_title == 'Source:':
                        source = get_link_text(columns[1])
                    if row_title == 'Genre:':
                        genre = get_link_text(columns[1])
                    if row_title == 'Production Method:':
                        production_method = get_link_text(columns[1])
                    if row_title == 'Creative Type:':
                        creative_type = get_link_text(columns[1])
                    if row_title == 'Production/Financing Companies:':
                        production_companies = get_production_companies(columns[1])

                        print(production_companies)

                        database_production_companies: list[ProductionCompany] = []

                        for production_company in production_companies:
                            # check if the production company is already in the database
                            db_production_company = ProductionCompany.get_or_none(slug=production_company.slug)

                            if db_production_company is None:
                                db_production_company = ProductionCompany.create(name=production_company.name, slug=production_company.slug)
                                database_production_companies.append(db_production_company)
                            else:
                                database_production_companies.append(db_production_company)

                    if row_title == 'Production Countries:':
                        production_countries = get_production_countries(columns[1])

                        database_production_countries: list[ProductionCountry] = []

                        for production_country in production_countries:
                            # check if the production country is already in the database
                            db_production_country = ProductionCountry.get_or_none(slug=production_country.slug)

                            if db_production_country is None:
                                db_production_country = ProductionCountry.create(name=production_country.name, slug=production_country.slug)
                                database_production_countries.append(db_production_country)
                            else:
                                database_production_countries.append(db_production_country)

                    if row_title == 'Languages:':
                        languages = get_languages(columns[1])

                        database_languages: list[Language] = []

                        for language in languages:
                            language_name = language[0]
                            language_slug = language[1]

                            # check if the language is already in the database
                            db_language = Language.get_or_none(slug=language_slug)

                            if db_language is None:
                                db_language = Language.create(name=language_name, slug=language_slug)
                                database_languages.append(db_language)
                            else:
                                database_languages.append(db_language)

                # now we make the movie
                movie = Movie.create(
                    truncated_title=movie_name_slug.name,
                    slug=movie_name_slug.slug,
                    title=title,
                    poster=poster_url,
                    synopsis=synopsis,
                    mpaa_rating=MPAA.rating,
                    mpaa_rating_reason=MPAA.reason,
                    running_time=running_time,
                    source=source,
                    genre=genre,
                    production_method=production_method,
                    creative_type=creative_type,
                    distributor=distributor_name_slug.name,
                    distributor_slug=distributor_name_slug.slug,
                )

                if db_franchise is not None:
                    MovieFranchise.create(movie=movie, franchise=db_franchise)

                for language in database_languages:
                    MovieLanguage.create(movie=movie, language=language)

                for production_country in database_production_countries:
                    MovieProductionCountry.create(movie=movie, production_country=production_country)

                for production_company in database_production_companies:
                    MovieProductionCompany.create(movie=movie, production_company=production_company)

                for keyword in database_keywords:
                    MovieKeyword.create(movie=movie, keyword=keyword)

                for release in domestic_releases:
                    DomesticRelease.create(date=release[0], type=release[1], movie=movie)

                BoxOfficeDay.create(
                    date=date,
                    movie=movie,
                    revenue=gross,
                    theaters=theaters
                )

                # now need to get the cast and crew
                cast_and_crew = main.find("div", {"id": "cast-and-crew_mobile"})

                if cast_and_crew is None:
                    print(f"No div with id cast-and-crew_mobile")
                    continue

                if isinstance(cast_and_crew, bs4.element.NavigableString):
                    print(f"cast_and_crew is not a Tag")
                    continue


                get_cast_crew(cast_and_crew, movie)

            else:
                BoxOfficeDay.create(
                    date=date,
                    movie=movie,
                    revenue=gross,
                    theaters=theaters
                )          
        
        print('Time taken:', time.time() - start_time)



