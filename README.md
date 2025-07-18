# Charfreq DFKO

The purpose of this project is to analyze the dataset of the following study to determine the relative frequency of keypresses on a typical computer keyboard when transcribing English sentences, including user corrections and errors:

    Dhakal, V., Feit, A., Kristensson, P., O., & Oulasvirta, A. 2017.
    Observations on Typing from 136 Million Keystrokes.
    In Proceedings of the 2018 CHI Conference on Human Factors in Computing Systems (CHI ’18).
    https://userinterfaces.aalto.fi/136Mkeystrokes/

The name of this project is derived from the names of the authors of the study: *Dhakal*, *Feit*, *Kristensson*, and *Oulasvirta*.

This project downloads the dataset from https://userinterfaces.aalto.fi/136Mkeystrokes/data/Keystrokes.zip and processes its 168,593 non-metadata files to produce the following five tab-separated, LF-terminated, and UTF-8 encoded files:

- `dfko.tsv`

  A table of all unique (keyname, keycode) pairs and their total number of occurrences (the *count*). Column 1 is the keyname, column 2 is the keycode, and column 3 is the count. All keynames are escaped as described below. Rows are sorted in descending order of count (i.e., highest count first).

- `1-grams.tsv`

  A table of all unique 1-grams and their total number of occurrences (the *count*). Column 1 is the 1-gram and column 2 is the count. Each row is included only if its keyname corresponds to a Unicode code point (a 1-gram). All 1-grams are escaped as described below. Rows are sorted in descending order of count (i.e., highest count first).

- `1-grams-uc.tsv`

  1-grams.tsv, but for all unique 1-grams converted to uppercase.

- `1-grams-with-c-and-p.tsv`

  1-grams.tsv, but with three columns appended to each row, representing cumulative count, percentage count, and cumulative percentage count.

- `1-grams-uc-with-c-and-p.tsv`

  1-grams-uc.tsv, but with three columns appended to each row, representing cumulative count, percentage count, and cumulative percentage count.

### Escaped strings

Escaped strings are strings in which specific Unicode code points are replaced with *escape sequences* - alternate representations used to ensure safe and unambiguous encoding - as follows:

- Code points with values 0 through 31 (inclusive) or 127 are replaced with `\x##`, where `##` is the value represented as two uppercase hexadecimal digits.
- `\` is replaced with `\\`.

## Author and copyright

This project was written and copyrighted in 2025 by Chris McLaren ([@csmclaren](https://www.github.com/csmclaren)).

## License

Unless otherwise noted, all files in this project are licensed under the [MIT License](https://choosealicense.com/licenses/mit/). See the [LICENSE](LICENSE.txt) file for details.
