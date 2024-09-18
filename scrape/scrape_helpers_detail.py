from scrape_helpers_daily import NameSlug
from typing import NamedTuple
import bs4
import datetime
import re


def get_poster_url(main: bs4.element.Tag) -> str | None:
    poster_div = main.find("div", {"id": "poster"})

    if poster_div is None:
        print("No poster div found")
        return None

    poster_image = poster_div.find("img")

    if poster_image is None:
        print("No poster image found")
        return None

    poster_url = poster_image["src"]

    return poster_url


def get_synopsis(main: bs4.element.Tag) -> str | None:
    mobile_layout = main.find("div", {"id": "mobile_layout"})
    accordion = mobile_layout.find("div", {"id": "accordion"})
    card = accordion.find("div", {"class": "card"})
    summary_mobile = card.find("div", {"id": "summary_mobile"})
    synopsis_div = summary_mobile.find("div", {"class": "card-body"})

    if synopsis_div is None:
        print("No synopsis div found")
        return None

    synopsis = synopsis_div.text.strip()

    # they all start with Synopsis so remove that
    if synopsis.startswith("Synopsis"):
        synopsis = synopsis[8:]

    return synopsis


def get_domestic_releases(column: bs4.element.Tag) -> list[tuple[datetime.date, str]]:
    """
    <td>September 6th, 2024 (Wide) by <a href="/market/distributor/Warner-Bros">Warner Bros.</a><br>September 6th, 2024 (IMAX) by <a href="/market/distributor/Warner-Bros">Warner Bros.</a></td>
    """
    """
    <tr><td><b>Domestic Releases:</b></td>
    <td>2022 (Canceled) by <a href="/market/distributor/STX-Entertainment">STX Entertainment</a><br>March 3rd, 2023 (Wide) by <a href="/market/distributor/Lionsgate">Lionsgate</a></td></tr>
    """

    # need to get the date and the type of release for each of the possible releases, so would want to split by <br> tags and then use a regex
    # get the html as text
    html = str(column)

    # split by <br> tags
    releases = html.split("<br/>")

    database_releases: list[tuple[datetime.date, str]] = []

    # regex to get the date and the distributor
    # September 6th, 2024 (Wide) by <a href="/market/distributor/Warner-Bros">Warner Bros.</a>
    raw = r"(.*) \((.*)\) by <a href=\"/market/distributor/(.*)\">(.*)</a>"

    for release in releases:
        match = re.match(raw, release)

        if match is not None:
            group_1 = match.group(1)

            # check if <td> is at the beginning
            if group_1.startswith("<td>"):
                group_1 = group_1[4:]

            date_string_cleaned = (
                group_1.replace("th,", "")
                .replace("st,", "")
                .replace("nd,", "")
                .replace("rd,", "")
            )

            try:
                date = datetime.datetime.strptime(date_string_cleaned, "%B %d %Y").date()
            except ValueError:
                print("Error parsing date")
                continue
            type = match.group(2)

            database_releases.append((date, type))

    return database_releases


class MPAA(NamedTuple):
    rating: str
    reason: str | None
    rating_date: datetime.date | None


def get_mpaa_rating(column: bs4.element.Tag) -> MPAA | None:
    """
    <td><a href="/market/mpaa-rating/PG-13-(US)">PG-13</a> for violent content, macabre and bloody images, strong language, some suggestive material and brief drug use.<br>(Rating bulletin 2843 (cert #54915), 7/17/2024)</td>
    """
    # want to get the mpaa rating and the reason for the rating
    html = str(column)

    a_tag = column.find("a")

    if a_tag is None:
        return None
    
    mpaa_rating = a_tag.text

    # split by <br> tags
    rating_and_reason = html.split("<br/>")
    rating = rating_and_reason[0]

    # regex to get the rating and the reason
    raw = r'<td><a href="\/market\/mpaa-rating\/(.*)">(.*)<\/a> for (.*)'

    # print(rating_and_reason)

    match = re.match(raw, rating)

    # print(rating)
    # print(raw)
    # print(match)

    if match is not None:
        mpaa_rating_reason = match.group(3)

        if mpaa_rating_reason.endswith("</td>"):
            mpaa_rating_reason = mpaa_rating_reason[:-5]

        # print(mpaa_rating_reason)

        raw = r"\((.*), (.*)\)"

        if len(rating_and_reason) < 2:
            return MPAA(rating=mpaa_rating, reason=mpaa_rating_reason, rating_date=None)

        match = re.match(raw, rating_and_reason[1])

        if match is not None:
            rating_date = datetime.datetime.strptime(match.group(2), "%m/%d/%Y").date()

            return MPAA(rating=mpaa_rating, reason=mpaa_rating_reason, rating_date=rating_date)
        
    return MPAA(rating=mpaa_rating, reason=None, rating_date=None)


def get_running_time(column: bs4.element.Tag) -> int | None:
    """
    <td>144 minutes</td>
    """
    split_text = column.text.split(" ")

    return int(split_text[0])


def get_franchise(column: bs4.element.Tag) -> NameSlug | None:
    """
    <tr><td><b>Franchise:</b></td>
    <td><a href="/movies/franchise/Twister">Twister</a></td></tr>
    """
    franchise = column.find("a")

    if franchise is None:
        return None

    franchise_name = franchise.text
    franchise_slug: str = franchise["href"]

    raw = r"\/movies\/franchise\/(.*)"

    # print(franchise_slug)

    match = re.match(raw, franchise_slug)

    # print(match)

    if match is not None:
        franchise_slug = match.group(1)

        return NameSlug(name=franchise_name, slug=franchise_slug)


def get_keywords(column: bs4.element.Tag) -> list[NameSlug]:
    """
    <tr><td><b>Keywords:</b></td>
    <td><a href="/movies/keywords/Disrupted-by-2023-WGA-and-SAG-Strikes">Disrupted by 2023 WGA &amp; SAG Strikes</a>, <a href="/movies/keywords/Action-Thriller">Action Thriller</a>, <a href="/movies/keywords/Weather">Extreme Weather</a>, <a href="/movies/keywords/Delayed-Sequel">Delayed Sequel</a>, <a href="/movies/keywords/Sequels-Without-Their-Original-Stars">Sequels Without Their Original Stars</a></td></tr>
    """
    keywords = column.find_all("a")

    keyword_list: list[NameSlug] = []

    for keyword in keywords:
        keyword_name = keyword.text
        keyword_slug = keyword["href"]

        raw = r"\/movies\/keywords\/(.*)"

        match = re.match(raw, keyword_slug)

        # print(keyword_slug)

        # print(match)

        if match is not None:
            keyword_slug = match.group(1)

            keyword_list.append(NameSlug(name=keyword_name, slug=keyword_slug))

    return keyword_list


def get_link_text(column: bs4.element.Tag) -> str:
    """
    <tr><td><b>Source:</b></td><td><a href="/market/source/Original-Screenplay">Original Screenplay</a></td></tr>
    <tr><td><b>Genre:</b></td><td><a href="/market/genre/Horror">Horror</a></td></tr>
    <td><a href="/market/creative-type/Science-Fiction">Science Fiction</a></td>
    <td><a href="/market/production-method/Live-Action">Live Action</a></td>
    """
    return column.find("a").text


def get_production_companies(column: bs4.element.Tag) -> list[NameSlug]:
    """
    <td><a href="/movies/production-company/Plan-B-Entertainment">Plan B Entertainment</a>, <a href="/movies/production-company/Tim-Burton">Tim Burton</a>, <a href="/movies/production-company/Warner-Bros">Warner Bros.</a>, <a href="/movies/production-company/Domain-Entertainment">Domain Entertainment</a>, <a href="/movies/production-company/Tommy-Harper">Tommy Harper</a>, <a href="/movies/production-company/Marc-Toberoff">Marc Toberoff</a></td>
    """
    production_companies = column.find_all("a")

    # print(production_companies)

    production_company_list: list[NameSlug] = []

    for production_company in production_companies:
        production_company_name = production_company.text
        production_company_slug = production_company["href"]

        raw = r"/movies/production-company/(.*)"

        match = re.match(raw, production_company_slug)

        if match is not None:
            production_company_slug = match.group(1)

        production_company_list.append(
            NameSlug(name=production_company_name, slug=production_company_slug)
        )

    return production_company_list


def get_production_countries(column: bs4.element.Tag) -> list[NameSlug]:
    """
    <td><a href="/New-Zealand/movies">New Zealand</a>, <a href="/United-States/movies">United States</a></td>
    """
    countries = column.find_all("a")

    country_list: list[NameSlug] = []

    for country in countries:
        country_name = country.text
        country_slug = country["href"]

        raw = r"/(.*)/movies"

        match = re.match(raw, country_slug)

        if match is not None:
            country_slug = match.group(1)

        country_list.append(NameSlug(name=country_name, slug=country_slug))

    return country_list


def get_languages(column: bs4.element.Tag) -> list[NameSlug]:
    """
    <td><a href="/language/English/movies">English</a>, <a href="/language/Korean/movies">Korean</a></td>
    """
    languages = column.find_all("a")

    language_list: list[NameSlug] = []

    for language in languages:
        language_name = language.text
        language_slug = language["href"]

        raw = r"/language/(.*)/movies"

        match = re.match(raw, language_slug)

        if match is not None:
            language_slug = match.group(1)

        language_list.append(NameSlug(name=language_name, slug=language_slug))

    return language_list

def get_budget(main: bs4.element.Tag) -> int | None:
    mobile_layout = main.find("div", {"id": "mobile_layout"})
    accordion = mobile_layout.find("div", {"id": "accordion"})
    card = accordion.find("div", {"class": "card"})
    summary_mobile = card.find("div", {"id": "summary_mobile"})
    card_body_div = summary_mobile.find("div", {"class": "card-body"})

    if card_body_div is None:
        print("No card body div found")
        return None
    """
    <tr><td><b>Production&nbsp;Budget:</b></td><td>$135,000,000 (worldwide box office is 4.2 times production budget)</td></tr>
    """

    tables = card_body_div.find_all("table")

    metrics_table = tables[1]

    if metrics_table is None:
        print("No metrics table found")
        return None
    
    rows = metrics_table.find_all("tr")

    # print(rows)

    for row in rows:
        columns = row.find_all("td")

        if columns[0].text == "Production Budget:":
            budget = columns[1].text

            raw = r"\$(.*) \(worldwide box office is (.*) times production budget\)"

            match = re.match(raw, budget)

            if match is not None:
                return int(match.group(1).replace(",", ""))
            
    return None