from db_path import base_db_path
from db import sqlite_db_connect, Movie

sqlite_db_connect()

unique_values = {
    "creative_type": set(),
    "genre": set(),
    "mpaa_rating": set(),
    "production_method": set(),
    "source": set(),
}

for movie in Movie.select():
    unique_values["creative_type"].add(movie.creative_type)
    unique_values["genre"].add(movie.genre)
    unique_values["mpaa_rating"].add(movie.mpaa_rating)
    unique_values["production_method"].add(movie.production_method)
    unique_values["source"].add(movie.source)

for key, value in unique_values.items():
    print(key, value)
