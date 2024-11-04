from playhouse.migrate import *

from boxoffice.db.db import WikipediaDay, sqlite_db, sqlite_db_connect, MovieMetacritic, MovieTrailerViews

migrator = SqliteMigrator(sqlite_db)

budget_field = IntegerField(null=True)

if __name__ == "__main__":
    sqlite_db_connect()
    with sqlite_db:
        # WikipediaDay.create_table()
        MovieTrailerViews.create_table()
        # MovieMetacritic.create_table()
