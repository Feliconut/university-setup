from pathlib import Path
from typing import Generator, List


def beautify(string):
    return string.replace('_', ' ').replace('-', ' ').title()


def unbeautify(string):
    return string.replace(' ', '-').lower()


MAX_LEN = 50


def generate_short_title(title):
    short_title = title or '...'
    if len(title) >= MAX_LEN:
        short_title = title[:MAX_LEN - len(' ... ')] + ' ... '
    short_title = short_title.replace('$', '')
    return short_title


def recursive_iterdir(path: Path) -> Generator[Path, None, None]:
    for entry in path.iterdir():
        if entry.is_dir():
            yield entry
            yield from recursive_iterdir(entry)


def cut_string(string, max_length) -> List[str]:
    # cut the string into pieces of max_length
    pieces = []
    while len(string) > max_length:
        pieces.append(string[:max_length])
        string = string[max_length:]
    pieces.append(string)
    return pieces
