import textwrap
from data_hub_api.utils.html import convert_plain_text_to_html


class TestConvertPlainTextToHtml:
    def test_should_return_empty_string_if_plain_text_is_empty(self):
        result = convert_plain_text_to_html('')
        assert result == ''

    def test_should_return_single_paragraph_for_single_line(self):
        result = convert_plain_text_to_html('this is a single line')
        assert result == '<p>this is a single line</p>'

    def test_should_escape_special_charaters_as_html(self):
        result = convert_plain_text_to_html('this is a single line with these < > charaters')
        assert result == '<p>this is a single line with these &lt; &gt; charaters</p>'

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

    def test_should_return_multiple_paragraph_for_lines_split_by_blank_lines_with_space(self):
        plain_text = 'this is the first line\n  \nthis is the second line'
        result = convert_plain_text_to_html(plain_text)
        assert result == textwrap.dedent('''
            <p>this is the first line</p>

            <p>this is the second line</p>
        ''').strip()

    def test_should_make_first_paragraph_bold_if_enabled(self):
        plain_text = textwrap.dedent('''
            this is the first line

            this is the second line
        ''')
        result = convert_plain_text_to_html(plain_text, is_first_paragraph_bold=True)
        assert result == textwrap.dedent('''
            <p><strong>this is the first line</strong></p>

            <p>this is the second line</p>
        ''').strip()

    def test_should_return_paragraph_with_br_when_there_is_a_single_new_line(self):
        plain_text = textwrap.dedent('''
            this is the first line
            this is the second line
        ''')
        result = convert_plain_text_to_html(plain_text)
        assert result == textwrap.dedent('''
            <p>this is the first line<br/>
            this is the second line</p>
        ''').strip()
