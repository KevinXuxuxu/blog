from flask import Flask, render_template

from utils import *


app = Flask(__name__)

app.config['FREEZER_DESTINATION_IGNORE'] = ['.git*']


@app.route("/")
def index():
    all_posts = get_all_posts_with_metadata()
    index_md = get_local_content('pages', 'index')
    md_factory = get_md_factory()
    html = md_factory(index_md)
    return render_template('index.html', rendered_content=html, posts=all_posts)

@app.route("/category/<category>/")
def category(category):
    all_posts = get_all_posts_with_metadata()
    filtered_posts = [p for p in all_posts if p.category == category]
    return render_template('category.html', category=category, posts=filtered_posts)

@app.route("/post/<path_title>/")
def post(path_title):
    md = get_local_content('posts', path_title)
    parsed_post = parse_post_metadata(path_title, md)
    md_factory = get_md_factory()
    html = md_factory(parsed_post.content)
    return render_template('post.html', post=parsed_post, rendered_content=html)
