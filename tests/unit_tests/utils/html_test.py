import textwrap
from data_hub_api.utils.html import convert_plain_text_to_html


class TestConvertPlainTextToHtml:
    def test_should_return_empty_string_if_plain_text_is_empty(self):
        result = convert_plain_text_to_html('')
        assert result == ''

    def test_should_return_single_paragraph_for_single_line(self):
        result = convert_plain_text_to_html('this is a single line')
        assert result == '<p>this is a single line</p>'

    def test_should_return_multiple_paragraph_for_lines_split_by_blank_lines(self):
        plain_text = textwrap.dedent('''
            this is the first line

            this is the second line
        ''')
        result = convert_plain_text_to_html(plain_text)
        assert result == textwrap.dedent('''
            <p>this is the first line</p>

            <p>this is the second line</p>
        ''').strip()
