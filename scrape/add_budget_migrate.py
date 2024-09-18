from playhouse.migrate import *

import sys

sys.path.append("..")

from db.db import sqlite_db

migrator = SqliteMigrator(sqlite_db)

budget_field = IntegerField(null=True)

if __name__ == "__main__":
    with sqlite_db:
        migrate(
            migrator.add_column("movie", "budget", budget_field),
        )
