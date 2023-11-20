import inspect

from sqlalchemy_data_model_visualizer import generate_data_model_diagram

from src import models as mods
from src.database.base import Base


def main():
    output_file_name = "my_data_model_diagram"

    models = [
        m
        for m in mods.__dict__.values()
        if inspect.isclass(m) and issubclass(m, Base)
    ]

    generate_data_model_diagram(
        models,
        output_file_name,
    )


if __name__ == "__main__":
    main()
