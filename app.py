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
    post_list = get_all_post_titles()
    md = '\n'.join(
        ['Here is a list of all my blogs'] +
        [gen_post_md(pt) for pt in post_list])
    return _render_md(md, title='fzxu\'s Blog')

@app.route("/category/<category>/")
def category(category):
    all_posts = get_all_posts_with_metadata()
    filtered_post_path_titles = [p.path_title for p in all_posts if p.category == category]
    md = '\n'.join(
        [f'Here is a list of all blogs of category `{category}`'] +
        [gen_post_md(path_title) for path_title in filtered_post_path_titles])
    return _render_md(md, title=category)

@app.route("/post/<path_title>/")
def post(path_title):
    md = get_local_content(path_title)
    parsed_post = parse_post_metadata(path_title, md)
    return _render_md(parsed_post.content, title=parsed_post.title, sub_title=parsed_post.date)
