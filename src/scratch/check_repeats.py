import os
import re

from src.util import get_location


def main():
    """
    Checks for repeat in the empire_species.txt file (repeats by line)
    """

    assets_dir = "../factories/assets"

    files = [
        "empire_species.txt",
        "empire_suffix.txt",
        "stars_prefix.txt",
    ]

    del_files = {"stars_prefix.txt"}

    for file in files:
        fn = os.path.join(assets_dir, file)
        check_file(fn, delete_repeats=file in del_files)

    sort_files = [
        "empire_suffix.txt",
    ]

    for file in sort_files:
        fn = os.path.join(assets_dir, file)
        sort_file_abc(fn)


def check_file(
    file_name: str,
    *,
    delete_repeats: bool = False,
    strip_whitespace: bool = True,
):
    location = get_location()
    file = os.path.join(location, file_name)

    # contains the names as key, line number as value
    names = dict()

    repeat_lines = []

    print(f"Checking {file_name} for repeats")

    whitespace_reg = re.compile(r"\s+")

    with open(file, "r") as f:
        for i, line in enumerate(f):
            line = line.strip()

            if strip_whitespace:
                # remove all whitespace with no space
                line = whitespace_reg.sub("", line)

            if line in names:
                print(f"Line {i + 1} is a repeat of line {names[line] + 1}")

                repeat_lines.append(i + 1)
            else:
                names[line] = i

    print(f"Finished checking {file_name} for repeats")

    if delete_repeats:
        print(f"Deleting repeats from {file_name}")

        with open(file, "r") as f:
            lines = f.readlines()

        for i in repeat_lines:
            lines[i - 1] = ""

        with open(file, "w") as f:
            f.writelines(lines)

        print(f"Finished deleting repeats from {file_name}")


def sort_file_abc(file_name: str):
    location = get_location()
    file = os.path.join(location, file_name)

    print(f"Sorting {file_name} alphabetically")

    with open(file, "r") as f:
        lines = f.readlines()

    lines.sort()

    with open(file, "w") as f:
        f.writelines(lines)

    print(f"Finished sorting {file_name} alphabetically")


if __name__ == "__main__":
    main()
