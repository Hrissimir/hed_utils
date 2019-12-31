from unittest import TestCase

from hed_utils.support import text_tool


class TestTextTool(TestCase):

    def test_get_indices_single_letter(self):
        text = "123aa2a2322abb"
        self.assertListEqual(text_tool.get_indices(text, "1"), [0])
        self.assertListEqual(text_tool.get_indices(text, "2"), [1, 5, 7, 9, 10])
        self.assertListEqual(text_tool.get_indices(text, "a"), [3, 4, 6, 11])

    def test_get_indices_substring(self):
        text = "123aa2a2322abb"
        self.assertListEqual(text_tool.get_indices(text, "23"), [1, 7])
        self.assertListEqual(text_tool.get_indices(text, "bb"), [12])

    def test_invert_quotes(self):
        text = "asd'asds\"__23123___ A\"'''"
        inverted_text = "asd\"asds'__23123___ A'\"\"\""
        self.assertEqual(text_tool.invert_quotes(text), inverted_text)

    def test_normalize_spacing(self):
        raw_text = "game_start_utc	country	tournament	host_team	guest_team	ratio_1	ratio_X	ratio_2"
        normalized_text = "game_start_utc country tournament host_team guest_team ratio_1 ratio_X ratio_2"
        self.assertEqual(text_tool.normalize_spacing(raw_text), normalized_text)
        raw_text = """a b \nc\td\ne\tf"""
        self.assertEqual("a b c d e f", text_tool.normalize_spacing(raw_text))

    def test_html_escape_unescape(self):
        expected = "&lt;"
        self.assertEqual("&lt;", text_tool.html_escape("<"))
        self.assertEqual("<", text_tool.html_unescape("&lt;"))

    def test_split_to_lines(self):
        text_leading_and_trailing_spaces_empty_line_and_line_spacing = \
            """
            line1 
            
            line2
            """
        lines = text_tool.split_to_lines(text_leading_and_trailing_spaces_empty_line_and_line_spacing)
        self.assertListEqual(lines, ["line1", "line2"])
        lines = text_tool.split_to_lines(text_leading_and_trailing_spaces_empty_line_and_line_spacing,
                                         keep_empty_lines=True)
        self.assertListEqual(lines, ["line1", "", "line2"])

        lines = text_tool.split_to_lines(text_leading_and_trailing_spaces_empty_line_and_line_spacing,
                                         keep_empty_lines=True, strip_lines=False)
        self.assertListEqual(lines, ["line1 ", "            ", "            line2"])

        lines = text_tool.split_to_lines(text_leading_and_trailing_spaces_empty_line_and_line_spacing,
                                         strip_text=False)
        self.assertListEqual(lines, ["line1", "line2"])
        lines = text_tool.split_to_lines(text_leading_and_trailing_spaces_empty_line_and_line_spacing,
                                         strip_text=False, keep_empty_lines=True)
        self.assertListEqual(lines, ["", "line1", "", "line2", ""])

    def test_split_to_words(self):
        text = """a \rb \n c \n\n  \t \td"""
        self.assertListEqual("a b c d".split(), text_tool.split_to_words(text))

    def test_find_dates(self):
        text = "asd 123 qasd2 2qwa 23 41 a 2019-02-34 sasd 2020-01-23"
        expected_dates = ["2020-01-23"]
        self.assertListEqual(expected_dates, text_tool.find_dates(text))

    def test_normalize(self):
        raw_items = ["Une conservation téléphonique", "Les vacances d'été"]
        expected_normalized_items = ['Une conservation telephonique', "Les vacances d'ete"]
        actual_normalized_items = [text_tool.normalize(i) for i in raw_items]
        self.assertListEqual(expected_normalized_items, actual_normalized_items)
