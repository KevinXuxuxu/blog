import os
import mistune
import time

from collections import namedtuple
from flask.helpers import url_for
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import html
from typing import List, Tuple

ParsedPost = namedtuple('ParsedPost', ['title', 'path_title', 'date', 'tags', 'category', 'content'])
_all_post_metadata_cache = None
_post_metadata_template = '''---
title: {title}
date: {time}
tags: []
category: default
---
'''

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


def get_local_content(folder: str, path_title: str) -> str:
    with open('{}/{}.md'.format(folder, path_title), 'r') as f:
        return f.read()


def get_all_posts_with_metadata() -> List[ParsedPost]:
    global _all_post_metadata_cache
    if _all_post_metadata_cache is None:
        _all_post_metadata_cache = []
        for path in os.listdir('posts'):
            with open('posts/' + path, 'r') as f:
                _all_post_metadata_cache.append(
                    parse_post_metadata(path[:-3], f.read()))
    return sorted(_all_post_metadata_cache, key=lambda p: p.date, reverse=True)


def get_all_tags(posts: List[ParsedPost]) -> List[str]:
    rtn = set()
    for p in posts:
        for t in p.tags:
            rtn.add(t)
    return sorted(list(rtn))


def gen_post_md(path_title: str) -> str:
    return '- [{}]({})'.format(path_title, url_for('post', path_title=path_title))


def parse_attribute(line: str) -> Tuple[str, str]:
    parts = line.split(': ')
    return parts[0], ': '.join(parts[1:])


def parse_post_metadata(path_title: str, md: str) -> ParsedPost:
    parts = md.split('---\n')
    metadata_str, content = parts[1], '---\n'.join(parts[2:])
    metadata = {'content': content, 'path_title': path_title}
    for line in metadata_str.strip().split('\n'):
        key, value = parse_attribute(line)
        if key == 'tags':
            metadata['tags'] = eval(value.strip())
        else:
            metadata[key] = value.strip()
    return ParsedPost(**metadata)


def gen_new_post(title: str):
    path_title = title.replace(' ', '-')
    with open(f'posts/{path_title}.md', 'w') as f:
        f.write(_post_metadata_template.format(
            title=title,
            time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        ))
