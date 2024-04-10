import json
import uuid

from flask import Flask, request, jsonify
import redis
from dto.Item import Item
from dto.ShoppingCart import ShoppingCart

app = Flask(__name__)
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


def _exists_cart(id):
    return redis_cache.get(id)


if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=5000)
