import os
from argparse import ArgumentParser


def modify_steam_urls(directory):
    """
    Opens all '.url' files in the specified directory, appends '" -silent"' to Steam URLs,
    and counts the number of modified files.
    """
    modified_count = 0
    for filename in os.listdir(directory):
        if not filename.endswith(".url"):
            continue
        filepath = os.path.join(directory, filename)
        try:
            with open(filepath, "r", encoding="UTF") as f:
                lines = f.readlines()

            modified = False
            for i, line in enumerate(lines):
                if not line.startswith("URL=steam"):
                    continue
                if '" -silent' not in line:
                    lines[i] = line.rstrip() + '" -silent\n'
                    modified = True
                    modified_count += 1
                    break
            if modified:
                with open(filepath, "w", encoding="UTF") as f:
                    f.writelines(lines)
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    print(f"Modified {modified_count} files.")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("directory",
                        nargs="?",
                        default=".",
                        help="folder, where the steam URLs should be modified")
    args = parser.parse_args()
    directory = args.directory

    if os.path.exists(directory) and os.path.isdir(directory):
        modify_steam_urls(directory)
    else:
        print(f"Error: Directory '{directory}' does not exist or is not a directory.")
