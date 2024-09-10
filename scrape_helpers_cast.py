import bs4
from db import CastOrCrew, Movie, Person
import re

def get_cast_crew(cast_and_crew: bs4.element.Tag, movie: Movie):
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
    card_body = cast_and_crew.find("div", {"class": "card-body"})

    cast_new_divs = card_body.find_all("div", {"class": "cast_new"})

    # print(cast_new_divs)

    for cast_new_div in cast_new_divs:
        h1 = cast_new_div.find("h1")

        if h1 is not None:
            if h1.text == "Leading Cast" or h1.text == "Supporting Cast" or h1.text == "Cameos" or h1.text == "Production and Technical Credits":
                table = cast_new_div.find("table")

                rows = table.find_all("tr")

                for row in rows:
                    columns = row.find_all("td")

                    name = columns[0].find("a").text
                    name_slug = columns[0].find("a")["href"]
                    # <a href="/person/1356330401-Cailee-Spaeny">Cailee Spaeny</a>
                    raw = r"/person/(.*)-(.*)"

                    match = re.match(raw, name_slug)

                    if match is not None:
                        name_slug = match.group(1)

                    db_person = Person.get_or_none(slug=name_slug)

                    if db_person is None:
                        db_person = Person.create(name=name, slug=name_slug)

                    role = columns[1].text

                    CastOrCrew.create(
                        person=db_person,
                        role=role,
                        is_cast=True if h1.text != "Production and Technical Credits" else False,
                        is_lead_ensemble=True if h1.text == "Leading Cast" else False,
                        movie=movie,
                    )
