import inspect
import os

MIN_NUM_STARS = 1000
MAX_NUM_STARS = 100000


def get_location(file: str | None = None) -> str:
    # https://stackoverflow.com/questions/13699283/how-to-get-the-callers-filename-method-name-in-python
    if file is None:
        frame = inspect.stack()[1]
        file = frame[0].f_code.co_filename

    return os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(file)))
