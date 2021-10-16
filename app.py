from flask import Flask, render_template

from utils import *


app = Flask(__name__)

app.config['FREEZER_DESTINATION_IGNORE'] = ['.git*']


@app.route("/")
def index():
    all_posts = get_all_posts_with_metadata()
    return render_template('index.html', posts=all_posts)

@app.route("/category/<category>/")
def category(category):
    all_posts = get_all_posts_with_metadata()
    filtered_posts = [p for p in all_posts if p.category == category]
    return render_template('category.html', category=category, posts=filtered_posts)

@app.route("/post/<path_title>/")
def post(path_title):
    md = get_local_content(path_title)
    parsed_post = parse_post_metadata(path_title, md)
    md_factory = get_md_factory()
    html = md_factory(parsed_post.content)
    return render_template(
        'post.html', title=parsed_post.title, sub_title=parsed_post.date, content=html)
