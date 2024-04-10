class Item:
    def __init__(self, id, name, price):
        self.id = id
        self.name = name
        self.price = price

    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_price(self):
        return self.price

    def set_price(self, price):
        self.price = price

    def __str__(self):
        return "{item_id: " + str(self.id) + ", name: " + self.name + ", price: " + str(self.price) + "}"

    def to_json(self):

        return {
            'item_id': str(self.id),
            'name': self.name,
            'price': self.price
        }

