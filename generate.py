from flask_frozen import Freezer

from app import app
from utils import get_all_posts_with_metadata

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

if __name__ == '__main__':
    freezer.freeze()
