import collections
import importlib.util
import io
import os
import pathlib
import sys

from collections import Counter

from typing import Iterator, TextIO, Tuple

MODULE_NAME = "util"
module_path = os.path.join("tools", "charfreq-tools", "util.py")
spec = importlib.util.spec_from_file_location(MODULE_NAME, module_path)
util = importlib.util.module_from_spec(spec)
sys.modules[MODULE_NAME] = util
spec.loader.exec_module(util)

INPUT_ENCODING = "iso-8859-1"
MAX_SAMPLE_LENGTH = 256
OUTPUT_ENCODING = "utf-8"
PROGRESS_INTERVAL = 1000


def iter_keystroke_file(file: TextIO) -> Iterator[list[str]]:
    COLUMN_COUNT_LITERAL_LF = 8
    COLUMN_COUNT_LITERAL_TAB = 10
    COLUMN_COUNT_NORMAL = 9
    EXPECTED_HEADER_LINE = (
        "PARTICIPANT_ID\tTEST_SECTION_ID\tSENTENCE\tUSER_INPUT\tKEYSTROKE_ID\t"
        "PRESS_TIME\tRELEASE_TIME\tLETTER\tKEYCODE"
    )
    line_index = 0
    try:
        header_line = file.readline()
        line_index += 1
        if header_line.rstrip("\n") != EXPECTED_HEADER_LINE:
            raise ValueError(f"unexpected header line: '{header_line}'")
        for line in file:
            line_index += 1
            line = line.rstrip("\n")
            fields = line.split("\t")
            length = len(fields)
            if length == COLUMN_COUNT_NORMAL:
                # Normal line.
                pass
            elif length == COLUMN_COUNT_LITERAL_LF:
                # Line contains literal LF character.
                # Merge the following line and remove the artificial column.
                line_index += 1
                next_line = file.readline()
                if not next_line:
                    raise ValueError(f"unexpected format: {fields}")
                next_line = next_line.rstrip("\n")
                next_fields = next_line.split("\t")
                fields += next_fields
                length = len(fields)
                if length != 10 or fields[7] != "" or fields[8] != "":
                    raise ValueError(f"unexpected format: {fields}")
                fields.pop(7)
                fields[7] = "LITERAL_LF"
            elif length == COLUMN_COUNT_LITERAL_TAB:
                # Line contains a literal TAB character.
                # Remove the artificial column.
                if fields[7] != "" or fields[8] != "":
                    raise ValueError(f"unexpected format: {fields}")
                fields.pop(7)
                fields[7] = "LITERAL_TAB"
            else:
                # Abnormal line.
                raise ValueError(f"unexpected format: {fields}")
            keyname = fields[-2]
            if "\n" in keyname or "\t" in keyname:
                raise ValueError(f"\\n or \\t in keyname: {fields}")
            keycode = fields[-1]
            if "\n" in keycode or "\t" in keycode:
                raise ValueError(f"util\\n or \\t in keycode: {fields}")
            yield fields
    except Exception as e:
        raise type(e)(f"line: {line_index}, {e}") from e


def process_keystroke_file(
    file: TextIO, counter: Counter[Tuple[str, str]], ngrams: dict[Tuple[int, bool], Counter[str]]
) -> None:
    for fields in iter_keystroke_file(file):
        keyname = fields[-2]
        keycode = fields[-1]
        counter.update([(keyname, keycode)])
        if len(keyname) == 1:
            ch = keyname
            ch_uc = ch.upper() if "a" <= ch <= "z" else ch
            for key in [(1, False), (1, True)]:
                ngrams.setdefault(key, Counter())
            ngrams[(1, False)][ch] += 1
            ngrams[(1, True)][ch_uc] += 1


@util.handle_broken_pipe_error
def main() -> None:
    script_name, *args = sys.argv
    script_base = os.path.basename(script_name)

    if len(args) < 2:
        print(
            f"Usage: {script_base} <path_src> <dpath_src> [<pattern> ...]",
            file=sys.stderr,
        )
        sys.exit(1)

    path_src = pathlib.Path(args[0]).expanduser().resolve()
    dpath_dest = pathlib.Path(args[1]).expanduser().resolve()
    patterns = args[2:]

    if not dpath_dest.is_dir():
        print(f"Error: '{dpath_dest}' is not a valid directory", file=sys.stderr)
        sys.exit(1)

    counter = collections.Counter()
    name = None
    ngrams: dict[Tuple[int, bool], Counter[str]] = {}
    printed_progress = False
    total_file_count = 0

    try:
        for name, file in util.iter_files(path_src, patterns):
            total_file_count += 1
            if total_file_count % PROGRESS_INTERVAL == 0:
                print(".", end="", file=sys.stderr, flush=True)
                printed_progress = True
            with io.TextIOWrapper(file, encoding=INPUT_ENCODING) as file:
                process_keystroke_file(file, counter, ngrams)
    except Exception as e:
        print(f"Error: path_src: '{path_src}', name: {name}", file=sys.stderr)
        print(str(e), file=sys.stderr)
        raise SystemExit(1) from e

    if printed_progress:
        print(file=sys.stderr, flush=True)

    print(f"files: {total_file_count}")
    print()

    dfko = sorted(counter.items(), key=lambda item: item[1], reverse=True)

    with open(dpath_dest / "dfko.tsv", "w", encoding=OUTPUT_ENCODING) as file:
        for (keyname, keycode), count in dfko:
            file.write(f"{util.escape_string(keyname)}\t{keycode}\t{count}\n")

    util.export_ngrams(ngrams, MAX_SAMPLE_LENGTH, dpath_dest, OUTPUT_ENCODING)


if __name__ == "__main__":
    main()
