# convert the -1 values in running time for the movies table and theaters in the BoxOfficeDay table to NULL

from db import sqlite_db_connect, Movie, BoxOfficeDay

if __name__ == "__main__":
    sqlite_db_connect()

    Movie.update(running_time=None).where(Movie.running_time == -1).execute()

    BoxOfficeDay.update(theaters=None).where(BoxOfficeDay.theaters == -1).execute()
