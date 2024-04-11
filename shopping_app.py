import json
import uuid
import redis
from collections import Counter

from flask import Flask, request, jsonify, send_from_directory
from flasgger import Swagger

from dto.Item import Item
from dto.ShoppingCart import ShoppingCart

app = Flask(__name__)
swagger = Swagger(app, template_file="documentation/swagger.yml")

app.config.from_object('config.Config')  # configuration variables to the flask app

redis_cache = redis.Redis(host=app.config["CACHE_REDIS_HOST"], port=app.config["CACHE_REDIS_PORT"],
                          password=app.config["CACHE_REDIS_PASSWORD"], db=app.config["CACHE_REDIS_DB"])


@app.route('/cart/', methods=['POST'])
def create_cart():
    data = request.get_json()
    cart_id = uuid.uuid4()
    shopping_cart = ShoppingCart(cart_id, data['name'], [])

    shopping_cart_json = shopping_cart.to_json()

    redis_cache.set(str(cart_id), json.dumps(shopping_cart_json))
    return jsonify(shopping_cart_json)


@app.route('/cart/detail/<cart_id>', methods=['GET'])
def get_cart_details(cart_id):

    if _exists_cart(cart_id) is not None:
        redis_cache.get(cart_id)

        cart_details = redis_cache.get(cart_id)
        cart_details_str = cart_details.decode('utf-8')

        # Return cart details as JSON
        return jsonify(json.loads(cart_details_str))

        # Return appropriate response if cart does not exist
    return jsonify({"message": "Cart not found"}), 404


@app.route('/cart/list', methods=['GET'])
def list_carts():

    keys = redis_cache.keys('*')  # '*' only because on db are saved the carts

    results = []
    for key in keys:
        value = redis_cache.get(key)
        results.append(json.loads(value))

    return jsonify({"total": len(results), "results": results})


@app.route('/cart/update/<cart_id>', methods=['PUT'])
def update_cart(cart_id):

    update_data = request.get_json()

    if _exists_cart(cart_id) is not None:
        cart_data_redis = json.loads(redis_cache.get(cart_id))

        # update only the values on request
        for key, value in update_data.items():
            cart_data_redis[key] = value

        redis_cache.set(cart_id, json.dumps(cart_data_redis))
        return jsonify({"message": "Cart updated successfully"}), 204
    else:
        return jsonify({"message": "Cart does not exist"}), 404


@app.route('/cart/<cart_id>', methods=['DELETE'])
def delete_cart(cart_id):
    if _exists_cart(cart_id) is not None:
        redis_cache.delete(cart_id)
        return jsonify({"message": "Cart deleted successfully"})
    else:
        return jsonify({"message": "Cart does not exist"}), 404


@app.route('/cart/<cart_id>/item/add', methods=['POST'])
def add_item_to_cart(cart_id):
    item_data = request.get_json()

    if _exists_cart(cart_id) is not None:

        item_id = uuid.uuid4()
        item = Item(item_id, item_data['name'], item_data['price'])

        cart = redis_cache.get(cart_id)
        cart_json = json.loads(cart.decode('utf-8'))
        shopping_cart = ShoppingCart(cart_id, cart_json['name'], cart_json['items'])
        shopping_cart.add_item(item)

        shopping_cart_json = shopping_cart.to_json()

        redis_cache.set(str(cart_id), json.dumps(shopping_cart_json))
        return jsonify(shopping_cart_json)

    else:
        return "Cart does not exists!"


@app.route('/cart/analytics/items/count', methods=['GET'])
def get_shopping_carts_with_items_count():
    keys = redis_cache.keys('*')
    carts_with_items = sum(1 for key in keys if json.loads(redis_cache.get(key))['items'])
    return jsonify({"count": carts_with_items})


@app.route('/cart/analytics/items', methods=['GET'])
def get_max_min_avg_cart_items():
    keys = redis_cache.keys('*')  # Get all keys in Redis
    list_items_count = [len(json.loads(redis_cache.get(key))['items']) for key in keys if json.loads(redis_cache.get(key))['items']]

    if not list_items_count:
        return jsonify({"message": "No items found in any shopping cart"}), 404

    return jsonify({"max_items": max(list_items_count), "min_items": min(list_items_count),
                    "avg_items": sum(list_items_count)/len(list_items_count)})


@app.route('/cart/analytics/top-items', methods=['GET'])
def get_top_items_in_shopping_cart():
    keys = redis_cache.keys('*')
    all_items_of_carts = []

    # list.extend is to join the elements of two list in one
    for key in keys:
        items = json.loads(redis_cache.get(key))['items']
        all_items_of_carts.extend((item['item_id'], item['name'], item['price']) for item in items)

    if not all_items_of_carts:
        return jsonify({"message": "No items found in any shopping cart"}), 404

    # https://docs.python.org/3/library/collections.html
    top_items = Counter(all_items_of_carts).most_common(5)
    return jsonify({"top_items": top_items})


def _exists_cart(id):
    return redis_cache.get(id)


# @app.route('/api-docs')
# def swagger_ui():
#     return send_from_directory('documentation', 'swagger.yaml')


if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=5000)
