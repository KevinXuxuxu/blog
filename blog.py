import base64
import requests
import mistune

from collections import namedtuple
from typing import Tuple, List
from flask import Flask, render_template

GITHUB_REPO_CONTENT_API = 'https://api.github.com/repos/{repo}/contents/{path}'
ParsedPost = namedtuple('ParsedPost', ['title', 'date', 'tags', 'category', 'content'])

def get_github_content(repo: str, path: str) -> str:
    resp = requests.get(GITHUB_REPO_CONTENT_API.format(repo=repo, path=path))
    encoded_content = resp.json()['content']
    return base64.b64decode(encoded_content).decode()


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


@app.route("/post/<path_title>")
def hello_world(path_title):
    md = get_github_content('KevinXuxuxu/blog', 'posts/{}.md'.format(path_title))
    parsed_post = parse_post_metadata(md)
    md_factory = mistune.create_markdown()
    html = md_factory(parsed_post.content)
    return render_template(
        'layout.html', title=parsed_post.title, sub_title=parsed_post.date, content=html)
