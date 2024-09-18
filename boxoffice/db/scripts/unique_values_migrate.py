from playhouse.migrate import *

from db import sqlite_db, Movie, BoxOfficeDay

migrator = SqliteMigrator(sqlite_db)

if __name__ == "__main__":
    # first want to drop the movie__tmp__ table if it exists
    sqlite_db.execute_sql("DROP TABLE IF EXISTS movie__tmp__")

    # create a temporary table with the same schema as the movie table
    sqlite_db.execute_sql(
        """
        CREATE TABLE movie__tmp__ AS
        SELECT * FROM movie
        """
    )

    # drop the movie table
    sqlite_db.execute_sql("DROP TABLE movie")

    # create the movie table with the new schema
    sqlite_db.create_tables([Movie])

    # copy the data from the temporary table to the new table
    sqlite_db.execute_sql(
        """
        INSERT INTO movie
        SELECT * FROM movie__tmp__
        """
    )

    # drop the temporary table
    sqlite_db.execute_sql("DROP TABLE movie__tmp__")

    # do the same thing for the boxofficeday table
    sqlite_db.execute_sql("DROP TABLE IF EXISTS boxofficeday__tmp__")

    sqlite_db.execute_sql(
        """
        CREATE TABLE boxofficeday__tmp__ AS
        SELECT * FROM boxofficeday
        """
    )

    sqlite_db.execute_sql("DROP TABLE boxofficeday")

    sqlite_db.create_tables([BoxOfficeDay])

    sqlite_db.execute_sql(
        """
        INSERT INTO boxofficeday
        SELECT * FROM boxofficeday__tmp__
        """
    )

    sqlite_db.execute_sql("DROP TABLE boxofficeday__tmp__")

    # migrate(
    #     migrator.drop_not_null("movie", "running_time"),
    #     migrator.drop_not_null("boxofficeday", "theaters"),
    # )
