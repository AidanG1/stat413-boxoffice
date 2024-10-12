from boxoffice.db.frames import MovieCompleteSchema, get_movie_frame_full
from pandera.typing import DataFrame


def get_train_test_frames() -> (
    tuple[DataFrame[MovieCompleteSchema], DataFrame[MovieCompleteSchema]] | None
):
    df = get_movie_frame_full()

    if df is None:
        return None

    # training frame if before 2023-01-01
    training_frame = df[df["release_year"] < 2023]

    # testing frame if after 2023-01-01
    testing_frame = df[df["release_year"] >= 2023]

    return DataFrame[MovieCompleteSchema](training_frame), DataFrame[
        MovieCompleteSchema
    ](testing_frame)
