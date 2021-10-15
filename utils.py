import os
import mistune

from collections import namedtuple
from flask.helpers import url_for
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import html
from typing import List

ParsedPost = namedtuple('ParsedPost', ['title', 'path_title', 'date', 'tags', 'category', 'content'])
_all_post_metadata_cache = None

class HighlightRenderer(mistune.HTMLRenderer):

    def decorated_highlight(self, code: str, lang: str) -> str:
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = html.HtmlFormatter(style='solarized-light')
        pygments_highlight = highlight(code, lexer, formatter)
        # get everything between <pre>
        i, j = pygments_highlight.find('<pre>') + len('<pre>'), pygments_highlight.find('</pre>')
        code = pygments_highlight[i:j]
        # add <code> element to correct place
        i = len('<span></span>')
        code = code[:i] + '<code>' + code[i:] + '</code>'
        return f'''<div class="highlight">
    <pre class="code" data-lang="{lang}">{code}</pre>
</div>'''

    def block_code(self, code, lang=None) -> str:
        if lang:
            return self.decorated_highlight(code, lang)
        return f'<pre><code>' + mistune.escape(code) + '</code></pre>'


def get_md_factory() -> 'mistune.markdown.Markdown':
    return mistune.create_markdown(renderer=HighlightRenderer(), plugins=['strikethrough'])


def get_local_content(path_title: str) -> str:
    with open('posts/{}.md'.format(path_title), 'r') as f:
        return f.read()


def get_all_post_titles() -> List[str]:
    return [file_name[:-3] for file_name in os.listdir('posts')]


def get_all_posts_with_metadata() -> List[ParsedPost]:
    global _all_post_metadata_cache
    if _all_post_metadata_cache is None:
        _all_post_metadata_cache = []
        for path in os.listdir('posts'):
            with open('posts/' + path, 'r') as f:
                _all_post_metadata_cache.append(
                    parse_post_metadata(path[:-3], f.read()))
    return _all_post_metadata_cache


def gen_post_md(path_title: str) -> str:
    return '- [{}]({})'.format(path_title, url_for('post', path_title=path_title))


def parse_post_metadata(path_title: str, md: str) -> ParsedPost:
    _, metadata_str, content = md.split('---\n')
    metadata = {'content': content, 'path_title': path_title}
    for line in metadata_str.strip().split('\n'):
        key, value = line.split(': ')
        if key == 'tags':
            metadata['tags'] = eval(value.strip())
        else:
            metadata[key] = value.strip()
    return ParsedPost(**metadata)