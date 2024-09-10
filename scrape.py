from bs4 import BeautifulSoup
import datetime
import re
import requests
from db import sqlite_db_connect, sqlite_db as db, Movie, DomesticRelease, BoxOfficeDay, Franchise, Keyword, ProductionCompany, ProductionCountry, CastOrCrew, MovieFranchise, MovieKeyword, MovieProductionCompany, MovieProductionCountry, Language, MovieLanguage

base_url: str = "https://the-numbers.com/box-office-chart/daily/"

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
        response = requests.get(
            f"{base_url}{date.year}/{date.month:02}/{date.day:02}", headers=headers
        )
        # print(response.text)

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

        for row in rows:
            columns = row.find_all("td")
            break

        # the third column is the movie title
        third_column_bold = columns[2].find("b")
        if third_column_bold is not None:
            movie_truncated_title: str = third_column_bold.text
            href = third_column_bold.find("a")["href"]

            # /movie/Beetlejuice-Beetlejuice-(2024)#tab=box-office
            raw = r"/movie/(.*)#tab=box-office"

            match = re.match(raw, href)

            if match is not None:
                slug: str = match.group(1)
                print(slug)

        # fourth column is the distributor
        fourth_column = columns[3]
        distributor = fourth_column.text

        raw = r"/market/distributor/(.*)"

        distributor_slug = fourth_column.find("a")["href"]

        match = re.match(raw, distributor_slug)

        if match is not None:
            distributor_slug = match.group(1)

        # fifth column is the gross
        fifth_column = columns[4]

        # $41,804,322
        gross = int(fifth_column.text[1:].replace(",", ""))

        # eighth column is the theaters
        theaters = int(columns[7].text.replace(",", ""))

        # check if the slug is already in the database
        movie = Movie.get_or_none(slug=slug)

        if movie is None:
            r = requests.get(f"https://the-numbers.com/movie/{slug}", headers=headers)

            soup = BeautifulSoup(r.text, "html.parser")

            main = soup.find("div", {"id": "main"})

            if main is None:
                print(f"No div with id main")
                continue

            h1 = main.find("h1")
            if h1 is None:
                print(f"No h1 in div with id main")
                continue

            title = h1.text

            poster_div = main.find("div", {"id": "poster"})

            poster_image = poster_div.find("img")

            poster_url = poster_image["src"]

            summary_mobile = main.find("div", {"id": "summary_mobile"})

            card_body = summary_mobile.find("div", {"class": "card-body"})

            synopsis = card_body.find("p").text

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

            first_row = rows[0]

            second_column = first_row.find_all("td")[1]

            """
            <td>September 6th, 2024 (Wide) by <a href="/market/distributor/Warner-Bros">Warner Bros.</a><br>September 6th, 2024 (IMAX) by <a href="/market/distributor/Warner-Bros">Warner Bros.</a></td>
            """
            # need to get the date and the type of release for each of the possible releases, so would want to split by <br> tags and then use a regex   
            # get the html as text
            html = str(second_column)

            # split by <br> tags
            releases = html.split("<br/>")

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

                    date_string_cleaned = group_1.replace('th', '').replace('st', '').replace('nd', '').replace('rd', '')

                    date = datetime.datetime.strptime(date_string_cleaned, "%B %d, %Y").date()
                    type = match.group(2)

                    DomesticRelease.create(date=date, type=type, movie=movie)

            third_row = rows[2]

            second_column = third_row.find_all("td")[1]

            """
            <td><a href="/market/mpaa-rating/PG-13-(US)">PG-13</a> for violent content, macabre and bloody images, strong language, some suggestive material and brief drug use.<br>(Rating bulletin 2843 (cert #54915), 7/17/2024)</td>
            """
            # want to get the mpaa rating and the reason for the rating
            html = str(second_column)

            # split by <br> tags
            rating_and_reason = html.split("<br>")
            rating = rating_and_reason[0]

            # regex to get the rating and the reason
            raw = r"<a href=\"/market/mpaa-rating/(.*)\">(.*)</a> for (.*)"

            match = re.match(raw, rating)

            if match is not None:
                mpaa_rating = match.group(2)
                mpaa_rating_reason = match.group(3)


            fourth_row = rows[3]

            """
            <td>144 minutes</td>
            """
            
            running_time = int(fourth_row.find_all("td")[1].text.split(" ")[0])

            fifth_row = rows[4]

            """
            <td><a href="/movies/franchise/Beetlejuice">Beetlejuice</a></td>
            """
            # want to get the franchise
            second_column = fifth_row.find_all("td")[1]

            franchise = second_column.find("a").text

            franchise_slug = second_column.find("a")["href"]

            raw = r"/movies/franchise/(.*)"

            match = re.match(raw, franchise_slug)

            if match is not None:
                franchise_slug = match.group(1)


            # check if the franchise is already in the database
            franchise = Franchise.get_or_none(slug=franchise_slug)

            if franchise is None:
                franchise = Franchise.create(name=franchise, slug=franchise_slug)

            eighth_row = rows[7]

            second_column = eighth_row.find_all("td")[1]

            """
            <td><a href="/movies/keywords/Horror-Comedy">Horror Comedy</a>, <a href="/movies/keywords/Delayed-Sequel">Delayed Sequel</a>, <a href="/movies/keywords/Sequels-Without-Their-Original-Stars">Sequels Without Their Original Stars</a></td>
            """

            # want to get the keywords and their slugs
            keywords = second_column.find_all("a")

            for keyword in keywords:
                keyword_name = keyword.text
                keyword_slug = keyword["href"]

                raw = r"/movies/keywords/(.*)"

                match = re.match(raw, keyword_slug)

                if match is not None:
                    keyword_slug = match.group(1)

                # check if the keyword is already in the database
                keyword = Keyword.get_or_none(slug=keyword_slug)

                if keyword is None:
                    keyword = Keyword.create(name=keyword_name, slug=keyword_slug)

                MovieKeyword.create(movie=movie, keyword=keyword)

            ninth_row = rows[8]
            """
            <tr><td><b>Source:</b></td><td><a href="/market/source/Original-Screenplay">Original Screenplay</a></td></tr>
            """
            # want to get the source
            second_column = ninth_row.find_all("td")[1]

            source = second_column.find("a").text

            tenth_row = rows[9]

            """
            <td><a href="/market/genre/Comedy">Comedy</a></td>
            """
            # want to get the genre
            genre = tenth_row.find_all("td")[1].find("a").text

            eleventh_row = rows[10]
            """
            <td><a href="/market/production-method/Live-Action">Live Action</a></td>
            """
            # want to get the production method
            production_method = eleventh_row.find_all("td")[1].find("a").text

            twelfth_row = rows[11]
            """
            <td><a href="/market/creative-type/Science-Fiction">Science Fiction</a></td>
            """
            # want to get the creative type
            creative_type = twelfth_row.find_all("td")[1].find("a").text

            thirteenth_row = rows[12]
            """
            <td><a href="/movies/production-company/Plan-B-Entertainment">Plan B Entertainment</a>, <a href="/movies/production-company/Tim-Burton">Tim Burton</a>, <a href="/movies/production-company/Warner-Bros">Warner Bros.</a>, <a href="/movies/production-company/Domain-Entertainment">Domain Entertainment</a>, <a href="/movies/production-company/Tommy-Harper">Tommy Harper</a>, <a href="/movies/production-company/Marc-Toberoff">Marc Toberoff</a></td>
            """
            # want to get the production companies
            second_column = thirteenth_row.find_all("td")[1]

            production_companies = second_column.find_all("a")

            for production_company in production_companies:
                production_company_name = production_company.text
                production_company_slug = production_company["href"]

                raw = r"/movies/production-company/(.*)"

                match = re.match(raw, production_company_slug)

                if match is not None:
                    production_company_slug = match.group(1)

                # check if the production company is already in the database
                production_company = ProductionCompany.get_or_none(slug=production_company_slug)

                if production_company is None:
                    production_company = ProductionCompany.create(name=production_company_name, slug=production_company_slug)

                MovieProductionCompany.create(movie=movie, production_company=production_company)

            fourteenth_row = rows[13]

            """
            <td><a href="/New-Zealand/movies">New Zealand</a>, <a href="/United-States/movies">United States</a></td>
            """

            # want to get the production countries
            second_column = fourteenth_row.find_all("td")[1]

            production_countries = second_column.find_all("a")

            for production_country in production_countries:
                production_country_name = production_country.text
                production_country_slug = production_country["href"]

                raw = r"/(.*)/movies"

                match = re.match(raw, production_country_slug)

                if match is not None:
                    production_country_slug = match.group(1)

                # check if the production country is already in the database
                production_country = ProductionCountry.get_or_none(slug=production_country_slug)

                if production_country is None:
                    production_country = ProductionCountry.create(name=production_country_name, slug=production_country_slug)

                MovieProductionCountry.create(movie=movie, production_country=production_country)

            fifteenth_row = rows[14]
            """
            <td><a href="/language/English/movies">English</a>, <a href="/language/Korean/movies">Korean</a></td>
            """

            # want to get the languages
            second_column = fifteenth_row.find_all("td")[1]

            languages = second_column.find_all("a")

            for language in languages:
                language_name = language.text
                language_slug = language["href"]

                raw = r"/language/(.*)/movies"

                match = re.match(raw, language_slug)

                if match is not None:
                    language_slug = match.group(1)

                # check if the language is already in the database
                language = Language.get_or_none(slug=language_slug)

                if language is None:
                    language = Language.create(name=language_name, slug=language_slug)

                MovieLanguage.create(movie=movie, language=language)

            # now we make the movie
            movie = Movie.create(
                truncated_title=movie_truncated_title,
                slug=slug,
                title=title,
                poster=poster_url,
                synopsis=synopsis,
                mpaa_rating=mpaa_rating,
                mpaa_rating_reason=mpaa_rating_reason,
                running_time=running_time,
                source=source,
                genre=genre,
                production_method=production_method,
                creative_type=creative_type,
                distributor=distributor,
                distributor_slug=distributor_slug
            )

            MovieFranchise.create(movie=movie, franchise=franchise)

            BoxOfficeDay.create(
                date=date,
                movie=movie,
                gross=gross,
                theaters=theaters
            )

            # now need to get the cast and crew
            cast_and_crew = main.find("div", {"id": "cast-and-crew_mobile"})

            if cast_and_crew is not None:
                """
                <div class="card-body">
 		<div class="cast_new">
<h1>Leading Cast</h1>
<div class="table-responsive"><table class="table table-sm">
<tbody><tr>
<td width="50%" align="right"><b><a href="/person/770401-Will-Smith">Will Smith</a></b></td>
<td width="50%" align="left">Mike Lowrey</td>
</tr>
<tr>
<td width="50%" align="right"><b><a href="/person/82960401-Martin-Lawrence">Martin Lawrence</a></b></td>
<td width="50%" align="left">Marcus Burnett</td>
</tr>
</tbody></table></div>
</div>
<div class="cast_new">
<h1>Supporting Cast</h1>
<div class="table-responsive"><table class="table table-sm">
<tbody><tr>
<td width="50%" align="right"><b><a href="/person/68420401-Vanessa-Hudgens">Vanessa Hudgens</a></b></td>
<td width="50%" align="left">Kelly</td>
</tr>
<tr>
<td width="50%" align="right"><b><a href="/person/88410401-Alexander-Ludwig">Alexander Ludwig</a></b></td>
<td width="50%" align="left">Dorn</td>
</tr>
<tr>
<td width="50%" align="right"><b><a rel="nofollow" href="/person/1577000401-Paola-NuA-ez">Paola Nuñez</a></b></td>
<td width="50%" align="left">Captain Rita Secada</td>
</tr>
<tr>
<td width="50%" align="right"><b><a href="/person/35560401-Eric-Dane">Eric Dane</a></b></td>
<td width="50%" align="left">James McGrath</td>
</tr>
<tr>
<td width="50%" align="right"><b><a href="/person/59060401-Ioan-Gruffudd">Ioan Gruffudd</a></b></td>
<td width="50%" align="left">Lockwood</td>
</tr>
<tr>
<td width="50%" align="right"><b><a href="/person/1546240401-Jacob-Scipio">Jacob Scipio</a></b></td>
<td width="50%" align="left">Armando Aretas</td>
</tr>
<tr>
<td width="50%" align="right"><b><a rel="nofollow" href="/person/1537540401-Melanie-Liburd">Melanie Liburd</a></b></td>
<td width="50%" align="left">Christine</td>
</tr>
<tr>
<td width="50%" align="right"><b><a href="/person/134220401-Tasha-Smith">Tasha Smith</a></b></td>
<td width="50%" align="left">Theresa Burnett</td>
</tr>
<tr>
<td width="50%" align="right"><b><a href="/person/1215860401-Tiffany-Haddish">Tiffany Haddish</a></b></td>
<td width="50%" align="left">Tabitha</td>
</tr>
<tr>
<td width="50%" align="right"><b><a href="/person/110550401-Joe-Pantoliano">Joe Pantoliano</a></b></td>
<td width="50%" align="left">Captain Conrad Howard</td>
</tr>
<tr>
<td class="end_above_the_line" width="50%" align="right"><a href="/person/462110401-Rhea-Seehorn">Rhea Seehorn</a></td>
<td class="end_above_the_line" width="50%" align="left">US Marshall Agent Judy Howard</td>
</tr>
<tr>
<td width="50%" align="right"><a href="/person/1356530401-D-J-Khaled">D.J. Khaled</a></td>
<td width="50%" align="left">Manny the Butcher</td>
</tr>
<tr>
<td width="50%" align="right"><a rel="nofollow" href="/person/126430401-John-Salley">John Salley</a></td>
<td width="50%" align="left">Fletcher</td>
</tr>
<tr>
<td width="50%" align="right"><a rel="nofollow" href="/person/2170570401-Joyner-Lucas">Joyner Lucas</a></td>
<td width="50%" align="left">Gang Leader</td>
</tr>
<tr>
<td width="50%" align="right"><a rel="nofollow" href="/person/2170580401-Quinn-Hemphill">Quinn Hemphill</a></td>
<td width="50%" align="left">Callie Howard</td>
</tr>
<tr>
<td width="50%" align="right"><a rel="nofollow" href="/person/2170590401-Dennis-Greene">Dennis Greene</a></td>
<td width="50%" align="left">Reggie McDonald</td>
</tr>
</tbody></table></div>
</div>
<div class="cast_new">
<h1>Cameos</h1>
<div class="table-responsive"><table class="table table-sm">
<tbody><tr>
<td width="50%" align="right"><a rel="nofollow" href="/person/2170600401-Lionel-Messi">Lionel Messi</a></td>
<td width="50%" align="left">Himself</td>
</tr>
</tbody></table></div>
</div>
<p>For a description of the different acting role types we use to categorize acting perfomances, see our <a href="/glossary#acting_roles">Glossary</a>.
</p><div class="cast_new">
<h1>Production and Technical Credits</h1>
<div class="table-responsive"><table class="table table-sm">
<tbody><tr>
<td width="50%" align="right"><b><a href="/person/1177920401-Adil-El-Arbi">Adil El Arbi</a></b></td>
<td width="50%" align"left"="">Director</td>
</tr><tr>
<td width="50%" align="right"><b><a href="/person/1177930401-Bilall-Fallah">Bilall Fallah</a></b></td>
<td width="50%" align"left"="">Director</td>
</tr><tr>
<td width="50%" align="right"><b><a rel="nofollow" href="/person/962490401-Chris-Bremner">Chris Bremner</a></b></td>
<td width="50%" align"left"="">Screenwriter</td>
</tr><tr>
<td width="50%" align="right"><b><a href="/person/203650401-Jerry-Bruckheimer">Jerry Bruckheimer</a></b></td>
<td width="50%" align"left"="">Producer</td>
</tr><tr>
<td width="50%" align="right"><b><a href="/person/770401-Will-Smith">Will Smith</a></b></td>
<td width="50%" align"left"="">Producer</td>
</tr><tr>
<td width="50%" align="right"><b><a href="/person/203630401-Chad-Oman">Chad Oman</a></b></td>
<td width="50%" align"left"="">Producer</td>
</tr><tr>
<td width="50%" align="right"><b><a href="/person/1445600401-Doug-Belgrad">Doug Belgrad</a></b></td>
<td width="50%" align"left"="">Producer</td>
</tr><tr>
<td width="50%" align="right"><b><a href="/person/208510401-Barry-Waldman">Barry Waldman</a></b></td>
<td width="50%" align"left"="">Executive Producer</td>
</tr><tr>
<td width="50%" align="right"><b><a href="/person/203620401-Mike-Stenson">Mike Stenson</a></b></td>
<td width="50%" align"left"="">Executive Producer</td>
</tr><tr>
<td width="50%" align="right"><b><a href="/person/205800401-James-Lassiter">James Lassiter</a></b></td>
<td width="50%" align"left"="">Executive Producer</td>
</tr><tr>
<td width="50%" align="right"><b><a href="/person/227920401-Jonathan-Mone">Jonathan Mone</a></b></td>
<td width="50%" align"left"="">Executive Producer</td>
</tr><tr>
<td width="50%" align="right"><b><a rel="nofollow" href="/person/962490401-Chris-Bremner">Chris Bremner</a></b></td>
<td width="50%" align"left"="">Executive Producer</td>
</tr><tr>
<td width="50%" align="right"><b><a href="/person/82960401-Martin-Lawrence">Martin Lawrence</a></b></td>
<td width="50%" align"left"="">Executive Producer</td>
</tr><tr>
<td width="50%" align="right"><b><a href="/person/83410401-Dan-Lebental">Dan Lebental</a></b></td>
<td width="50%" align"left"="">Editor</td>
</tr><tr>
<td width="50%" align="right"><b><a rel="nofollow" href="/person/2170610401-Asaf-Eisenberg">Asaf Eisenberg</a></b></td>
<td width="50%" align"left"="">Editor</td>
</tr><tr>
<td width="50%" align="right"><b><a href="/person/194040401-Lorne-Balfe">Lorne Balfe</a></b></td>
<td width="50%" align"left"="">Composer</td>
</tr><tr>
<td width="50%" align="right"><b><a rel="nofollow" href="/person/1301710401-Robrecht-Heyvaert">Robrecht Heyvaert</a></b></td>
<td width="50%" align"left"="">Cinematographer</td>
</tr><tr>
<td class="end_above_the_line" width="50%" align="right"><a href="/person/272820401-Gabe-Hilfer">Gabe Hilfer</a></td>
<td class="end_above_the_line" width="50%" align"left"="">Music Supervisor</td>
</tr></tbody></table></div>
</div>
<p>The bold credits above the line are the "above-the-line" credits, the other the "below-the-line" credits.
 	</p></div>
                """
                if cast_and_crew is None:
                    print(f"No div with id cast-and-crew_mobile")
                    continue


                cast_new_divs = cast_and_crew.find_all("div", {"class": "cast_new"})

                for cast_new_div in cast_new_divs:
                    h1 = cast_new_div.find("h1")

                    if h1 is not None:
                        if h1.text == "Leading Cast":
                            table = cast_new_div.find("table")

                            tbody = table.find("tbody")

                            rows = tbody.find_all("tr")

                            for row in rows:
                                columns = row.find_all("td")

                                name = columns[0].find("a").text
                                role = columns[1].text

                                CastOrCrew.create(name=name, role=role, is_cast=True, is_lead_ensemble=True, movie=movie)

                        if h1.text == "Supporting Cast":
                            table = cast_new_div.find("table")

                            tbody = table.find("tbody")

                            rows = tbody.find_all("tr")

                            for row in rows:
                                columns = row.find_all("td")

                                name = columns[0].find("a").text
                                role = columns[1].text

                                CastOrCrew.create(name=name, role=role, is_cast=True, is_lead_ensemble=False, movie=movie)

                        if h1.text == "Cameos":
                            table = cast_new_div.find("table")

                            tbody = table.find("tbody")

                            rows = tbody.find_all("tr")

                            for row in rows:
                                columns = row.find_all("td")

                                name = columns[0].find("a").text
                                role = columns[1].text

                                CastOrCrew.create(name=name, role=role, is_cast=False, is_lead_ensemble=False, movie=movie)

                        if h1.text == "Production and Technical Credits":
                            table = cast_new_div.find("table")

                            tbody = table.find("tbody")

                            rows = tbody.find_all("tr")

                            for row in rows:
                                columns = row.find_all("td")

                                name = columns[0].find("a").text
                                role = columns[1].text

                                CastOrCrew.create(name=name, role=role, is_cast=False, is_lead_ensemble=False, movie=movie)



        else:
            BoxOfficeDay.create(
                date=date,
                movie=movie,
                gross=gross,
                theaters=theaters
            )           



