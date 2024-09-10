from typing import NamedTuple
import bs4
import re

class NameSlug(NamedTuple):
    name: str
    slug: str

def get_movie_title_and_slug(third_column: bs4.element.Tag) -> NameSlug | None:
    third_column_bold = third_column.find("b")
    if third_column_bold is not None:
        movie_truncated_title: str = third_column_bold.text

        a_tag = third_column_bold.find("a")
        if a_tag is None:
            return None
        href = a_tag["href"]

        # /movie/Beetlejuice-Beetlejuice-(2024)#tab=box-office
        raw = r"/movie/(.*)#tab=box-office"

        match = re.match(raw, href)

        if match is not None:
            slug: str = match.group(1)
            print(slug)

            return NameSlug(name=movie_truncated_title, slug=slug)
        
def get_distributor(column: bs4.element.Tag) -> NameSlug | None:
    distributor = column.text

    raw = r"/market/distributor/(.*)"

    distributor_a = column.find("a")

    if distributor_a is None:
        return None

    distributor_slug = distributor_a["href"]

    match = re.match(raw, distributor_slug)

    if match is not None:
        distributor_slug = match.group(1)

        return NameSlug(name=distributor, slug=distributor_slug)
    
def get_gross(column: bs4.element.Tag) -> int:
    # $41,804,322
    return int(column.text.replace("$", "").replace(",", ""))

def get_theaters(column: bs4.element.Tag) -> int:
    try: # sometimes there is an empty theater count
        return int(column.text.replace(",", ""))
    except ValueError:
        return -1
