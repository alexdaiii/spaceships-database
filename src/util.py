import inspect
import os

import pandas as pd

MIN_NUM_STARS = 1000
MAX_NUM_STARS = 100000


def get_location(file: str | None = None) -> str:
    # https://stackoverflow.com/questions/13699283/how-to-get-the-callers-filename-method-name-in-python
    if file is None:
        frame = inspect.stack()[1]
        file = frame[0].f_code.co_filename

    return os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(file)))


def get_m_and_b(
    x1: float, y1: float, x2: float, y2: float
) -> tuple[float, float]:
    """
    Get the slope and y-intercept of a line given two points.
    """
    m = (y2 - y1) / (x2 - x1)
    b = y1 - m * x1
    return m, b


def get_yhat(x: float, m: float, b: float) -> float:
    """
    Get the y-value of a line given an x-value, slope, and y-intercept.
    """
    return m * x + b


def df_info(df: pd.DataFrame):
    """
    Only works in development mode.
    """
    from tabulate import tabulate

    print(tabulate(df, headers="keys", tablefmt="psql"))
