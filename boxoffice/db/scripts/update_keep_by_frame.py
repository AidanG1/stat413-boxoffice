from boxoffice.db.frames import get_movie_frame_full
from boxoffice.db.db import Movie

if __name__ == "__main__":
    df = get_movie_frame_full()

    if df is None:
        print("no df")
        exit()

    movies = Movie.select()
    print("Setting all movies to False")
    for movie in movies:
        movie.meets_keep_requirements = False
        movie.save()
    print("Done setting all movies to False")

    df_ids = set(df.id)

    for movie in Movie.select():
        if movie.id in df_ids:
            print(movie.id, movie.title)
            movie.meets_keep_requirements = True
            movie.save()
