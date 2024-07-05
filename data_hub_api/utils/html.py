import re
import html

def convert_plain_text_to_html(plain_text: str) -> str:
    if not plain_text:
        return ''
    paragraphs = re.split(r'\n\s*\n', plain_text)
    html_paragraphs = ['<p>{}</p>'.format(html.escape(p.strip())) for p in paragraphs]
    return '\n\n'.join(html_paragraphs)
