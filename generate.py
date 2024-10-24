from flask_frozen import Freezer
from shutil import copyfile

from app import app
from utils import get_all_posts_with_metadata, get_all_tags

freezer = Freezer(app)

@freezer.register_generator
def post():
    for post in get_all_posts_with_metadata():
        yield {'path_title': post.path_title}

@freezer.register_generator
def category():
    all_categories = {p.category for p in get_all_posts_with_metadata()}
    for category in all_categories:
        yield {'category': category}

@freezer.register_generator
def tag():
    all_tags = get_all_tags(get_all_posts_with_metadata())
    for tag in all_tags:
        yield {'tag': tag}

if __name__ == '__main__':
    freezer.freeze()
    # Copy CNAME file to the build dir.
    copyfile("CNAME", "build/CNAME")
    copyfile("enable_threads.js", "build/enable_threads.js")
