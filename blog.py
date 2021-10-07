import base64
import requests
import mistune

from collections import namedtuple
from flask import Flask, render_template
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import html
from typing import List

GITHUB_REPO_CONTENT_API = 'https://api.github.com/repos/{repo}/contents/{path}'
GITHUB_REPO_TREE_API = 'https://api.github.com/repos/{repo}/git/trees/main?recursive=1'
ParsedPost = namedtuple('ParsedPost', ['title', 'date', 'tags', 'category', 'content'])


def decorated_highlight(code: str, lang: str) -> str:
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


class HighlightRenderer(mistune.HTMLRenderer):
    def block_code(self, code, lang=None) -> str:
        if lang:
            return decorated_highlight(code, lang)
        return f'<pre><code>' + mistune.escape(code) + '</code></pre>'


def get_github_content(repo: str, path: str) -> str:
    resp = requests.get(GITHUB_REPO_CONTENT_API.format(repo=repo, path=path))
    encoded_content = resp.json()['content']
    return base64.b64decode(encoded_content).decode()


def get_all_posts_from_github(repo: str) -> List[str]:
    resp = requests.get(GITHUB_REPO_TREE_API.format(repo=repo))
    post_paths = [
        file['path'] for file in resp.json()['tree']
        if file['path'].startswith('posts/')]
    # strip dir and extension
    return [path[len('posts/'):-len('.md')] for path in post_paths]


def gen_post_md(path_title: str) -> str:
    return '- [{pt}](/post/{pt})'.format(pt=path_title)


def parse_post_metadata(md: str) -> ParsedPost:
    _, metadata_str, content = md.split('---\n')
    metadata = {'content': content}
    for line in metadata_str.strip().split('\n'):
        key, value = line.split(': ')
        if key == 'tags':
            metadata['tags'] = eval(value.strip())
        else:
            metadata[key] = value.strip()
    return ParsedPost(**metadata)


app = Flask(__name__)


@app.route("/post")
def posts():
    post_list = get_all_posts_from_github('KevinXuxuxu/blog')
    print(post_list)
    md_factory = mistune.create_markdown(renderer=HighlightRenderer())
    md = '\n'.join(['Here is a list of all my blogs'] + [gen_post_md(pt) for pt in post_list])
    print(md)
    html = md_factory(md)
    print(html)
    return render_template('layout.html', title='fzxu\'s Blog', content=html)

@app.route("/post/<path_title>")
def post(path_title):
    md = get_github_content('KevinXuxuxu/blog', 'posts/{}.md'.format(path_title))
    parsed_post = parse_post_metadata(md)
    md_factory = mistune.create_markdown(renderer=HighlightRenderer())
    html = md_factory(parsed_post.content)
    return render_template(
        'layout.html', title=parsed_post.title, sub_title=parsed_post.date, content=html)
