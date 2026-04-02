import re
import html
from html.entities import name2codepoint


_XML_BUILTIN_ENTITIES = frozenset({'lt', 'gt', 'amp', 'quot', 'apos'})

_VOID_ELEMENTS = frozenset({
    'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
    'link', 'meta', 'param', 'source', 'track', 'wbr'
})


def _replace_named_entity_with_numeric_ref(match: re.Match) -> str:
    name = match.group(1)
    if name in _XML_BUILTIN_ENTITIES:
        return match.group(0)
    codepoint = name2codepoint.get(name)
    if codepoint is not None:
        return f'&#{codepoint};'
    return match.group(0)


def _self_close_void_element(match: re.Match) -> str:
    tag_name = match.group(1).lower()
    attrs = match.group(2) or ''
    if tag_name in _VOID_ELEMENTS:
        return f'<{tag_name}{attrs}/>'
    return match.group(0)


def convert_html_to_xhtml(html_str: str) -> str:
    """Convert HTML to be XML-compatible (XHTML).

    - Named HTML entities (e.g. &nbsp;) are replaced with numeric character
      references (e.g. &#160;) because XML only has five built-in named
      entities (&lt; &gt; &amp; &quot; &apos;).
    - Void elements (e.g. <br>, <img ...>) are self-closed (<br/>, <img .../>)
      so the output can be parsed as XML.
    """
    result = re.sub(r'&([a-zA-Z]+);', _replace_named_entity_with_numeric_ref, html_str)
    result = re.sub(r'<([a-zA-Z]+)(\s[^>]*)?>',  _self_close_void_element, result)
    return result


def convert_paragraph_text_to_html(paragraph_text: str, is_bold: bool = False) -> str:
    lines = [line.rstrip() for line in paragraph_text.split('\n')]
    inner_html = html.escape('\n'.join(lines)).replace('\n', '<br/>\n')
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
