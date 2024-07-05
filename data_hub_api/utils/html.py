def convert_plain_text_to_html(plain_text: str) -> str:
    if not plain_text:
        return ''

    paragraphs = plain_text.strip().split('\n\n')
    html_paragraphs = ['<p>{}</p>'.format(p.strip()) for p in paragraphs]

    return '\n\n'.join(html_paragraphs)
