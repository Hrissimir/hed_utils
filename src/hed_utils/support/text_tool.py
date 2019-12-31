import html
import re
import sys
import unicodedata

from typing import List


def find_dates(text: str, datefmt="%Y-%m-%d") -> List[str]:
    date_patterns = {
        "%Y-%m-%d": r"(?:\D|^)([12]\d{3}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01]))(?:\D|$)"
    }
    pattern = date_patterns[datefmt]
    return list(re.findall(pattern, text))


def get_indices(text: str, sub: str) -> List[str]:
    """Gets all the indexes of occurrence of 'sub' in 'text'"""

    indices = []
    processed_chars = 0
    working_part = text

    while sub in working_part:
        idx = processed_chars + working_part.index(sub)
        indices.append(idx)
        processed_chars = idx + len(sub)
        working_part = text[processed_chars:]

    return indices


def html_escape(text, quote=True):
    return html.escape(text, quote)


def html_unescape(text):
    return html.unescape(text)


def invert_quotes(text: str):
    QUOTE = "'"
    QUOTES = "\""
    single_quote_indices = get_indices(text, QUOTE)
    double_quote_indices = get_indices(text, QUOTES)
    inverted_chars = []
    for i in range(len(text)):
        if i in single_quote_indices:
            inverted_chars.append(QUOTES)
        elif i in double_quote_indices:
            inverted_chars.append(QUOTE)
        else:
            inverted_chars.append(text[i])
    return "".join(inverted_chars)


def normalize_spacing(text: str) -> str:
    """Substitutes all consecutive whitespaces in the given text with a single space."""

    return re.sub(r"\s+", " ", text)


def normalize(text, *, map_cmb=True, map_digits=True, map_whitespace=True, form="NFKD") -> str:  # pragma: no-cov
    text = unicodedata.normalize(form, text)

    if map_cmb:
        cmb_map = dict.fromkeys(c
                                for c
                                in range(sys.maxunicode)
                                if unicodedata.combining(chr(c)))
        text = text.translate(cmb_map)

    if map_digits:
        digits_map = {c: ord("0") + unicodedata.digit(chr(c))
                      for c
                      in range(sys.maxunicode)
                      if unicodedata.category(chr(c)) == "Nd"}
        text = text.translate(digits_map)

    if map_whitespace:
        whitespace_map = {ord("\t"): " ",
                          ord("\f"): " ",
                          ord("\r"): None}
        text = text.translate(whitespace_map)

    return text


def split_to_lines(text: str, *, strip_text=True, strip_lines=True, keep_empty_lines=False) -> List[str]:
    if strip_text:
        text = text.strip()

    lines = text.split("\n")

    if strip_lines:
        lines = [line.strip() for line in lines]

    if not keep_empty_lines:
        lines = [line for line in lines if line]

    return lines


def split_to_words(text: str) -> List[str]:
    return re.split(r"\s+", text)
