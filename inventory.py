
class Inventory(dict):

    def __init__(self, owner, gold = 0, bags = None, contents = None):
        self.owner = owner
        self.bags = bags
        self.gold = gold

        if contents:
            for entry in contents:
                thing = entry[0]
                self[thing.ui] = {"item": thing, "quantity": entry[1]}


    def add_item(self, new_item, quantity, visible = True):
        if new_item.ui in self:
            self[new_item.ui]["quantity"] += quantity
        else:
            self[new_item.ui] = {"item": new_item, "quantity": quantity}
        if visible == False:
            self[new_item.ui]["visible"] = False

    def rem_item(self, rem_item, quantity = 1):
        if rem_item.ui in self:
            self[rem_item.ui]["quantity"] -= quantity
            message = "Only {x} {name}s left.".format(x= self[rem_item.ui]["quantity"], name = rem_item.name)
            if self[rem_item.ui]["quantity"] <= 0:
                self.pop(rem_item.ui)
                message = "No {}s left.".format(rem_item.name)
            print(message)
        else: print("{} not in INV.".format(rem_item.name))