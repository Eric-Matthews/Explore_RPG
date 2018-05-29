
class Inventory(dict):

    def __init__(self, owner, gold = 0, bags = None, contents = None):
        self.owner = owner
        self.bags = bags
        self.gold = gold
        self.max_gold = False

        if contents:
            for entry in contents:
                thing = entry[0]
                self[thing.ui] = {"item": thing, "quantity": entry[1]}


    def add_gold(self, gold, secret = False):
        self.gold += gold
        if self.max_gold and self.gold > self.max_gold: self.gold = self.max_gold
        if secret == False:
            print("Gained {}g. Total: {}g.".format(gold, self.gold))

    def rem_gold(self, gold, secret = False):
        self.gold -= gold
        if self.gold < 0: self.gold = 0
        if secret == False:
            print("Lost {}g. Total: {}g.".format(gold, self.gold))

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