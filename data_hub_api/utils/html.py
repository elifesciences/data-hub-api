import re
import html

def convert_paragraph_text_to_html(paragraph_text: str, is_bold: bool = False) -> str:
    inner_html = html.escape(paragraph_text.strip()).replace('\n', '<br/>\n')
    if is_bold:
        inner_html = f'<strong>{inner_html}</strong>'
    return f'<p>{inner_html}</p>'


def convert_plain_text_to_html(plain_text: str, is_first_paragraph_bold: bool = False) -> str:
    if not plain_text:
        return ''
    paragraphs = re.split(r'\n\s*\n', plain_text)

    html_paragraphs = [
        convert_paragraph_text_to_html(paragraph, is_bold=(is_first_paragraph_bold and index == 0))
        for index, paragraph in enumerate(paragraphs)
    ]
    return '\n\n'.join(html_paragraphs)
