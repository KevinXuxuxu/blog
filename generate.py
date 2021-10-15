from flask_frozen import Freezer

from app import app
from utils import get_all_post_titles, get_all_posts_with_metadata

freezer = Freezer(app)

@freezer.register_generator
def post():
    for title in get_all_post_titles():
        yield {'path_title': title}

@freezer.register_generator
def category():
    all_categories = {p.category for p in get_all_posts_with_metadata()}
    for category in all_categories:
        yield {'category': category}

if __name__ == '__main__':
    freezer.freeze()
