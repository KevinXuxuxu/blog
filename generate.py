from flask_frozen import Freezer

from app import app
from utils import get_all_posts_from_local

freezer = Freezer(app)

@freezer.register_generator
def post():
    for title in get_all_posts_from_local():
        yield {'path_title': title}


if __name__ == '__main__':
    freezer.freeze()
