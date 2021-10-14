from flask import Flask, render_template

from utils import *


app = Flask(__name__)

app.config['FREEZER_DESTINATION_IGNORE'] = ['.git*']

def _render_md(md: str, title: str, sub_title: str = '') -> str:
    md_factory = get_md_factory()
    html = md_factory(md)
    return render_template('layout.html', title=title, sub_title=sub_title, content=html)

@app.route("/")
def posts():
    post_list = get_all_posts_from_local()
    md = '\n'.join(['Here is a list of all my blogs'] + [gen_post_md(pt) for pt in post_list])
    return _render_md(md, title='fzxu\'s Blog')

@app.route("/post/<path_title>/")
def post(path_title):
    md = get_local_content(path_title)
    parsed_post = parse_post_metadata(md)
    return _render_md(parsed_post.content, title=parsed_post.title, sub_title=parsed_post.date)
