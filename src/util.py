import inspect
import os


def get_location(file: str | None = None) -> str:
    # https://stackoverflow.com/questions/13699283/how-to-get-the-callers-filename-method-name-in-python
    if file is None:
        frame = inspect.stack()[1]
        file = frame[0].f_code.co_filename

    return os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(file))
    )
