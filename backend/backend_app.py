import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from storage import StorageJson

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes
limiter = Limiter(get_remote_address, app=app)  # Configure request limiter
logging.basicConfig(level=logging.INFO,  # Configure basic logging
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

REQ_KEYS = ["title", "content", "author", "date"]


def validate_post_input(data_dict: dict) -> bool:
    """Validate that all required keys are present in data dict.
    Returns true if all required keys are present, otherwise returns false"""
    for key in REQ_KEYS:
        if key not in data_dict:
            return False
    return True


def validate_sort_dir(sort: str, direction: str) -> bool:
    """Validate that sort and direction query variables are viable.
    Checks that sort is a key from the post keys,
    Checks the direction is either 'asc' or 'desc'.
    Returns true if the inputs are valid, otherwise returns false"""
    if sort in REQ_KEYS and (direction == 'asc' or direction == 'desc'):
        return True
    return False


def get_direction(direction: str) -> bool:
    """Convert viable direction variable to boolean.
    'desc' => True, 'asc' => False"""
    if direction == "asc":
        return False
    else:
        return True


def sort_posts(sort_key, reverse, posts_data):
    """Gets a sort key, reverse and the posts data, returns a sorted version
    of the posts data by the sort key and in the direction
    (asc or desc) by reverse var"""
    if sort_key == "date":
        return sorted(posts_data, key=lambda x: datetime.
                      strptime(x[sort_key], '%Y-%m-%d'), reverse=reverse)
    else:
        return sorted(posts_data, key=lambda x: x[sort_key], reverse=reverse)


@app.route('/api/posts', methods=['GET'])
@limiter.limit("10/minute")  # Limit to 10 requests per minute
def get_posts():
    """Returns list of posts if sort and direction query vars are provided,
    Returns the list sorted based on the variables.
    If query params provided have invalid value returns an error"""
    app.logger.info('GET request received for /api/posts')
    posts_data = storage.list_posts()['posts']

    sort_key = request.args.get('sort')
    direction = request.args.get('direction')

    if sort_key and direction:
        if validate_sort_dir(sort_key, direction):
            reverse = get_direction(direction)
            sorted_posts = sort_posts(sort_key, reverse, posts_data)
            return jsonify(sorted_posts), 200  # OK
        else:
            return jsonify({'error': 'Wrong query parameters'}), 400

    return jsonify(posts_data), 200


@app.route('/api/posts', methods=['POST'])
@limiter.limit("10/minute")  # Limit to 10 requests per minute
def add_post():
    """Adds a new post dict from the request to the persistent storage
    Returns the new create post to the client.
    If any of the required fields are missing return an error"""
    app.logger.info('POST request received for /api/posts')
    posts_data = storage.list_posts()['posts']

    new_post = request.get_json()
    if not validate_post_input(new_post):
        return jsonify({"error": "One or more required "
                                 "fields are missing"}), 400

    if len(posts_data) == 0:
        new_id = 1
    else:
        new_id = max(post['id'] for post in posts_data) + 1

    new_post['id'] = new_id

    storage.add_post(new_post)

    return jsonify(new_post), 201


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
@limiter.limit("10/minute")  # Limit to 10 requests per minute
def delete_post(post_id):
    """Deletes a post with the provided id from the storage.
    If post doesn't exist returns an error."""
    app.logger.info('DELETE request received for /api/posts/<post_id>')

    try:
        post = storage.find_post_by_id(post_id)
    except KeyError:
        return jsonify({"error": "Post was not found"}), 404

    storage.delete_post(post_id)
    return jsonify({"message": f"Post with id {post_id} "
                               f"has been deleted successfully."}), 200


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
@limiter.limit("10/minute")  # Limit to 10 requests per minute
def update_post(post_id):
    """Updates provided fields in the post with provided id.
    If post doesn't exist returns an error."""
    app.logger.info('PUT request received for /api/posts/<post_id>')

    try:
        post = storage.find_post_by_id(post_id)
    except KeyError:
        return jsonify({"error": "Post was not found"}), 404

    new_data = request.get_json()
    storage.update_post(post_id, new_data)

    return jsonify(post), 200  # OK


@app.route('/api/posts/search', methods=['GET'])
@limiter.limit("10/minute")  # Limit to 10 requests per minute
def search_posts():
    """Filters the data from storage based on provided query variables.
    If no variables given returns all data, if nothing was found
    returns empty list."""
    app.logger.info('GET request received for /api/posts/search')

    title_query = request.args.get('title')
    content_query = request.args.get('content')
    author_query = request.args.get('author')
    date_query = request.args.get('date')

    filtered_posts = storage.list_posts()['posts']

    # If none of the queries provided - returns all posts
    if title_query is None and content_query is None \
            and author_query is None and date_query is None:
        return jsonify(filtered_posts), 200  # OK

    # Handle each given query separately
    if title_query:
        filtered_posts = [post for post in filtered_posts
                          if title_query.lower() in post['title'].lower()]
    if content_query:
        filtered_posts = [post for post in filtered_posts
                          if content_query.lower() in post['content'].lower()]
    if author_query:
        filtered_posts = [post for post in filtered_posts
                          if author_query.lower() in post['author'].lower()]
    if date_query:
        filtered_posts = [post for post in filtered_posts
                          if date_query in post['date']]

    return jsonify(filtered_posts), 200  # OK


if __name__ == '__main__':
    storage = StorageJson('posts.json')
    POSTS = storage.list_posts()
    app.run(host="0.0.0.0", port=5002, debug=True)
