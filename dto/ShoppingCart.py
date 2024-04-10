from dto.Item import Item


class ShoppingCart:
    def __init__(self, cart_id, name, items):
        self.cart_id = cart_id
        self.name = name
        self.items = items

    def get_cart_id(self):
        return self.cart_id

    def set_cart_id(self, cart_id):
        self.cart_id = cart_id

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item_id):
        self.items = [item for item in self.items if item.item_id != item_id]

    def total_price(self):
        return sum(item.get_price() for item in self.items)

    def __str__(self):
        items_str = ', '.join(str(item) for item in self.items)
        return f"{{cart_id: {self.cart_id}, name: {self.name}, items: [{items_str}]}}"

    def to_json(self):

        items_json = []
        for item in self.items:
            if isinstance(item, dict):
                items_json.append(item)
            elif isinstance(item, Item):
                items_json.append(item.to_json())

        return {
            'cart_id': str(self.cart_id),
            'name': self.name,
            'items': items_json
        }
