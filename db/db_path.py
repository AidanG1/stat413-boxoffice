import os

# the base_db_path is the path to the sqlite database file, relative to the root of the project
base_db_path = os.path.join(
    os.path.join(os.path.dirname(__file__)),
    "data/data.sqlite",
)

if __name__ == "__main__":
    print(base_db_path)