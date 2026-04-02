import textwrap
from data_hub_api.utils.html import convert_html_to_xhtml, convert_plain_text_to_html


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
        plain_text = 'this is the first line\n\nthis is the second line'
        result = convert_plain_text_to_html(plain_text)
        assert result == textwrap.dedent('''
            <p>this is the first line</p>

            <p>this is the second line</p>
        ''').strip()

    def test_should_return_multiple_paragraph_for_lines_split_by_blank_lines_with_space(self):
        plain_text = 'this is the first line\n   \nthis is the second line'
        result = convert_plain_text_to_html(plain_text)
        assert result == textwrap.dedent('''
            <p>this is the first line</p>

            <p>this is the second line</p>
        ''').strip()

    def test_should_ignore_additional_new_lines_between_paragraphs(self):
        plain_text = 'this is the first line\n\n\n\n\nthis is the second line'
        result = convert_plain_text_to_html(plain_text)
        assert result == textwrap.dedent('''
            <p>this is the first line</p>

            <p>this is the second line</p>
        ''').strip()

    def test_should_make_first_paragraph_bold_if_enabled(self):
        plain_text = 'this is the first line\n \nthis is the second line'
        result = convert_plain_text_to_html(plain_text, is_first_paragraph_bold=True)
        assert result == textwrap.dedent('''
            <p><strong>this is the first line</strong></p>

            <p>this is the second line</p>
        ''').strip()

    def test_should_return_paragraph_with_br_when_there_is_a_single_new_line(self):
        plain_text = 'this is the first line\nthis is the second line'
        result = convert_plain_text_to_html(plain_text)
        assert result == textwrap.dedent('''
            <p>this is the first line<br/>
            this is the second line</p>
        ''').strip()

    def test_should_remove_trailing_whitespace(self):
        plain_text = 'this is the first line \t\nthis is the second line \t'
        result = convert_plain_text_to_html(plain_text)
        assert result == textwrap.dedent('''
            <p>this is the first line<br/>
            this is the second line</p>
        ''').strip()

    def test_should_preserve_leading_whitespace(self):
        plain_text = '\t this is the first line \n\t this is the second line \t'
        result = convert_plain_text_to_html(plain_text)
        assert result == textwrap.dedent('''
            <p>\t this is the first line<br/>
            \t this is the second line</p>
        ''').strip()


class TestConvertHtmlToXhtml:
    def test_should_return_unchanged_html_with_no_issues(self):
        assert convert_html_to_xhtml('<p>hello world</p>') == '<p>hello world</p>'

    def test_should_self_close_br_tag(self):
        assert convert_html_to_xhtml('<p>line 1<br>\nline 2</p>') == '<p>line 1<br/>\nline 2</p>'

    def test_should_self_close_img_tag(self):
        assert convert_html_to_xhtml(
            '<p><img alt="alt" src="https://example.com/img.png"></p>'
        ) == '<p><img alt="alt" src="https://example.com/img.png"/></p>'

    def test_should_self_close_hr_tag(self):
        assert convert_html_to_xhtml('<hr>') == '<hr/>'

    def test_should_not_alter_already_self_closed_tags(self):
        assert convert_html_to_xhtml('<br/>') == '<br/>'

    def test_should_replace_nbsp_with_numeric_character_reference(self):
        assert convert_html_to_xhtml('hello&nbsp;world') == 'hello&#160;world'

    def test_should_preserve_xml_builtin_entities(self):
        assert convert_html_to_xhtml('a&lt;b&gt;c&amp;d') == 'a&lt;b&gt;c&amp;d'

    def test_should_not_alter_non_void_elements(self):
        assert convert_html_to_xhtml('<p>text</p>') == '<p>text</p>'

    def test_should_not_alter_closing_tags(self):
        assert convert_html_to_xhtml('<p>text</p>') == '<p>text</p>'
