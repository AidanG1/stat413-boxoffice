# scrape the views for the movie trailer

from boxoffice.scrape.requests_session import s
from boxoffice.db.db import MovieTrailerViews, Movie
from typing import TypedDict


class PipedItem(TypedDict):
    url: str
    type: str
    title: str
    thumbnail: str
    uploaderName: str
    uploaderUrl: str
    uploaderAvatar: str
    uploadedDate: str
    shortDescription: str
    duration: int
    views: int
    uploaded: int
    uploaderVerified: bool
    isShort: bool


class PipedResponse(TypedDict):
    items: list[PipedItem]
    nextpage: str
    suggestion: str
    corrected: bool


if __name__ == "__main__":
    # get the relevant movies
    movies = Movie.select().where(Movie.meets_keep_requirements == True)
    movie_trailer_views = MovieTrailerViews.select()

    # filter out the movies that already have trailer views
    movies = [movie for movie in movies if not any([trailer.movie_id == movie.id for trailer in movie_trailer_views])]

    for movie in movies:
        views: list[int] = []
        movie_title = movie.title.replace("&", "and")
        movie_title = movie_title.replace("?", "")
        piped_url = (
            f"https://pipedapi.wireway.ch/search?q={movie_title} {movie.release_year} movie trailer&filter=videos"
        )
        response = s.get(piped_url)

        if response.status_code != 200:
            print(f"Failed to get response for {movie_title} ({movie.release_year}) with url {piped_url}")
            continue

        piped_response = response.json()

        # print(piped_response)

        for item in piped_response["items"]:
            if "trailer" in item["title"].lower():
                views.append(item["views"])

        print(f"Url: {piped_url}")
        print(views)

        # need to get the max, first 3 sum, first 5 sum, and total sum
        MovieTrailerViews.create(
            movie=movie,
            max_trailer_views=max(views),
            top_3_trailer_views=sum(views[:3]),
            top_5_trailer_views=sum(views[:5]),
            total_trailer_views=sum(views),
        )

        # print(f"Added trailer views for {movie.title} ({movie.release_year})")
