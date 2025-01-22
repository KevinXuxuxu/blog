from flask import Flask, render_template, Response
import feedgenerator
from datetime import datetime

from utils import *

from opencoder.app import sub_app

app = Flask(__name__)

app.config["FREEZER_DESTINATION_IGNORE"] = [".git*", "online_tool"]
app.register_blueprint(sub_app, url_prefix="/opencoder")


@app.after_request
def add_coop_coep_headers(response):
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
    return response


@app.route("/")
def index():
    all_posts = get_all_posts_with_metadata()
    index_md = get_local_content("pages", "index")
    md_factory = get_md_factory()
    html = md_factory(index_md)
    tags = get_top_k_tags(all_posts, 25)
    return render_template(
        "index.html", rendered_content=html, posts=all_posts, tags=tags
    )


@app.route("/blog/category/<category>/")
def category(category):
    all_posts = get_all_posts_with_metadata()
    filtered_posts = [p for p in all_posts if p.category == category]
    return render_template("category.html", category=category, posts=filtered_posts)


@app.route("/blog/tag/<tag>/")
def tag(tag):
    all_posts = get_all_posts_with_metadata()
    filtered_posts = [p for p in all_posts if tag in p.tags]
    return render_template("tag.html", tag=tag, posts=filtered_posts)


@app.route("/blog/post/<path_title>/")
def post(path_title):
    md = get_local_content("posts", path_title)
    parsed_post = parse_post_metadata(path_title, md)
    md_factory = get_md_factory()
    html = md_factory(parsed_post.content)
    return render_template("post.html", post=parsed_post, rendered_content=html)


@app.route("/feed.xml")
def rss_posts():
    feed = feedgenerator.Rss201rev2Feed(
        title="fzxu.me",
        link="https://site.fzxu.me/",
        description="Hey there, I'm fzxu. I (am hoping to) write about coding, system design and all other technical stuffs that I know (or would like to explore) here. Any comments/discussions are greatly welcomed.",
        language="en",
    )
    for post in get_all_posts_with_metadata():
        feed.add_item(
            title=post.title,
            link=f"https://site.fzxu.me/blog/post/{post.path_title}/",
            description=f"Tags: {', '.join(post.tags)}<br>Category: {post.category}",
            pubdate=datetime.strptime(post.date, "%Y-%m-%d %H:%M:%S"),
            unique_id=post.path_title,
        )
    xml = feed.writeString("utf-8")
    return Response(xml, mimetype="application/xml")
