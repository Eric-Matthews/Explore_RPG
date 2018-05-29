import random
import toolbox, items, name_gen, character, party

potion = items.Item("mod_heal_potion", 20)
sword = items.Item("test_sword", 50)


class Shop(object):
    shop_stocks = {'test_type': [sword, potion]}

    value_data = {'discount': {'min_max': (1, 300), 'purchase_limit': 1000, 'mark_down': 0.5, 'mark_up': 1.8},
                  'rip_off': {'min_max': (3, 500), 'purchase_limit': 900, 'mark_down': 0.3, 'mark_up': 2.3},
                  'high_end': {'min_max': (250, 1300), 'purchase_limit': 2000, 'mark_down': 0.5, 'mark_up': 2.0},
                  'luxury': {'min_max': (400, 2000), 'purchase_limit': 3000, 'mark_down': 0.3, 'mark_up': 2.3}}

    # Default shop actions, saved to instances for individual overwriting.
    default_actions = ['buy', 'sell', 'talk', 'exit']
    default_like_pc = 120


    def __init__(self, stock_type, value_type, faction = None, name=None, keeper=None):
        if __debug__: print("Only basic name gen. To do: IMPROVE THIS!")
        if name == None:
            name = (random.choice(
                ['dynamic', 'sellout', 'item', 'adventure', 'wonderful', 'overloaded', 'no bad items', 'fair price',
                 'marvellous']) + " " + random.choice(
                ['shop', 'emporium', 'market', 'sale', 'mongery', 'dealer'])).title()
        if keeper == None:
            keeper = character.Human(name_gen.person_name_gen())
        if faction == None:
            like_pc = type(self).default_like_pc
        else: like_pc = faction.relations["pc"] + 10

        self.name = name
        self.keeper = keeper
        self.like_pc = like_pc
        self.actions = type(self).default_actions[:]

        self.talk_lines = ["I hear the {species} matroscka is opening soon.", "What ya talking to me for {name}?",
                        "I wish I had a long coat and scary voice."]
        self.greet_lines = ["Greetin's stranger.", "Hello {species}"]
        self.bye_lines = ["Go carefully stranger.", "See ya round, {name}", "Come back soon {species}."]
        self.sell_lines = ["I'll buy it for a high price.", "Hahaha, thank you."]
        self.buy_lines = ["Hahaha, thank you.", "It'll serve you well, {name}."]
        self.oostock_lines = ["Nuthin' to sell, stranger.", "Out of stock stranger."]
        self.nonsense_lines = ["I don't know what you mean.", "Beware the Jabberwocky {species}."]
        self.hate_lines = ["This is a local shop, for local people. There's nothing for you here.", "Get lost stranger.",
                           "Beat it, wannabe thief."]

        # Gives the individual shops a slightly random set of monetery variables, to keep things more interesting.
        # And stops players being able to work out the shop value types as easily.
        # Shop value types inform BUY/SELL prices, max purchase price, as well as stock base cost range.
        self.purchase_limit = int(
            type(self).value_data[value_type]['purchase_limit'] * (random.randint(80, 121) / 100.0))
        adjust = random.randint(8, 12) / 10.0
        self.mark_up = type(self).value_data[value_type]['mark_up'] * adjust
        if __name__ == '__main__' and __debug__ == True:
            print("x {} = {}".format(type(self).value_data[value_type]['mark_up'], adjust, self.mark_up))
        adjust = random.randint(8, 12) / 10.0
        self.mark_down = type(self).value_data[value_type]['mark_down'] * adjust
        if __name__ == '__main__' and __debug__ == True:
            print("x {} = {}".format(type(self).value_data[value_type]['mark_down'], adjust, self.mark_down))

        self.base_stock = self.get_base_stock(stock_type, value_type)
        self.stock = {}
        self.gen_stock()


    # Returns the base list of items the shop type can sell.
    # Gets list of all items for stock_type, and then removes items outside the price range of the shop, from value_type.
    def get_base_stock(self, stock_type, value_type):
        base_stock = type(self).shop_stocks[stock_type]
        min, max = type(self).value_data[value_type]['min_max']
        for item in base_stock:
            if min <= item.value <= max == False:
                base_stock.remove(item)
        return base_stock


    # Generates the stock of the shop from its base stock.
    # Adds a few potential items each time its called. Has space to sell some off, too.
    def gen_stock(self):
        if len(self.stock) > 1:
            # sell off some items in downtime too, for more verisimilitude.
            if __debug__: print("Add shops sell stock too clauses.")
        for i in range(1, random.randint(3, 5)):
            item = random.choice(self.base_stock)
            type_min, type_max = type(item).stock_min_max
            quantity = random.randint(type_min, type_max)
            self.add_stock(item, quantity)

    # Add an item to the shop's stock.
    def add_stock(self, item, quantity):
        if item.ui in self.stock:
            self.stock[item.ui]['quantity'] += quantity
        else:
            self.stock[item.ui] = {'quantity': quantity, 'item': item, 'visible': True}

    def rem_stock(self, item, quantity=1):
        if quantity > self.stock[item.ui]['quantity']:
            if __debug__: print("ERROR too much removed stock!")
        self.stock[item.ui]['quantity'] -= quantity
        if self.stock[item.ui]['quantity'] < 1:
            del self.stock[item.ui]

    def talk(self, talker, situation, lines = None):
        # Line should be LIST. Situation a STR: talk, greet, bye, buy, or sell
        if lines: lines = lines
        else:
            if self.like_pc < 80: lines = self.hate_lines
            elif situation == "greet": lines = self.greet_lines
            elif situation == "talk": lines = self.talk_lines
            elif situation == "bye": lines = self.bye_lines
            elif situation == "sell": lines = self.sell_lines
            elif situation == "buy": lines = self.buy_lines
            elif situation == "oostock": lines = self.oostock_lines
            else: lines = self.nonsense_lines
        return random.choice(lines).format(name = talker.name, species = talker.species)


    # Returns a string of the actions available in that shop.
    def make_action_string(self):
        actions = []
        for item in self.actions:
            actions.append(item.upper())
        actions.insert(len(actions) - 1, 'or')
        return " ".join(actions)

    # Prints a list of items, with quantity and price.
    def print_stock(self, stock, mode):
        if mode == 'pc_buy':
            price_mod = self.mark_down
        elif mode == 'pc_sell':
            price_mod = self.mark_up
        if __debug__: print(stock)
        for item in stock:
            if __debug__: print(item)
            if 'visible' not in stock[item] or stock[item]['visible'] == True:
                price = self.get_price(stock[item], mode)
                print("{quantity}x {name} - {cost}g each".format(
                    name=stock[item]['item'].name, cost=price, quantity=stock[item]['quantity']))
        else:
            if len(stock) < 1:
                print("There's nothing for sale.")

    # Returns PC's choice from the items in stock. Gives player adequate info to make choice. Returns ITEM.
    def get_choice_items(self, inventory, mode, message):
        print(message)
        look_up = {}
        index = []
        for ui in inventory:
            item = inventory[ui]["item"]
            look_up[item.name] = {"ui": ui, "item": item}
        for x, item in enumerate(look_up):
            index.append(look_up[item])
            price = self.get_price(look_up[item], mode)
            item_code = look_up[item]["ui"]
            print("{x}: {no}x {it} - {price}g".format(x = x, no = inventory[item_code]["quantity"], it = item, price = price))

        choice = input(">").lower()
        if choice in look_up:
            if __debug__: print("Name")
            choice = look_up[choice]["item"]
        elif choice.isdigit() == True and int(choice) in list(range(0, len(look_up))):
            if __debug__: print("ID")
            choice = index[int(choice)]["item"]
        elif choice in toolbox.quit_options:
            pass
        elif choice in ["buy", "talk"]:
            pass
        else:
            print("No idea what that is.")
        if __debug__: print(choice)
        return choice

    # Returns the buy/sell price of items for the shop.
    def get_price(self, stock_entry, mode):
        # Get the default price mods, and use them if none for specific item.
        if mode == 'pc_sell':
            price_mod = self.mark_down
        elif mode == 'pc_buy':
            price_mod = self.mark_up
        else:
            if __debug__: print("Shop mode error!")
            price_mod = 1
        # Then work out the actual value of the item, capped for buying at the shop purchase_limit.
        if hasattr(stock_entry, "value") == True:
            price = stock_entry.value * price_mod
        else: price = stock_entry['item'].value * price_mod
        if __name__ == '__main__' and __debug__ == True:
            print("value of {} adjusted to {}".format(stock_entry['item'].value, price))
        if mode == 'pc_sell' and price > self.purchase_limit:
            price = self.purchase_limit
        return int(price)

    def in_shop(self, shopper):
        shop = False
        print("You enter {}.".format(self.name.title()))
        print(self.talk(shopper, "greet"))
        if self.like_pc > 80: shop = True

        while shop == True:
            print("\n")
            print(self.make_action_string())
            user_input = input('> ').lower().split()
            if user_input[0] == 'buy':
                if len(self.stock) > 0:
                    shop = self.pc_buying(shopper)
                else: print(self.talk(shopper, "oostock"))
            elif user_input[0] == 'sell':
                if len(shopper.inv) > 0:
                    shop = self.pc_selling(shopper)
                else: print("You've nothing to sell.")
            elif user_input[0] == 'talk':
                print(self.talk(shopper, "talk"))
            elif user_input[0] in toolbox.quit_options:
                print(self.talk(shopper, "bye"))
                shop = False
            elif user_input[0] == 'steal':
                print("Petty theft to be added... one day. You Criminal.")
                if __debug__: print("REMEMBER TO ADD THEFT STUFF!")
                self.like_pc -= 10
            elif user_input == "help":
                print("You're certain there's some way to make this any more clear?")
                print("Because neither I, nor {}, can think of one.".format(self.keeper.name))
                print("It's not as if you're not using the keyboard or anything...")
            elif __name__ == '__main__' and __debug__ == True and user_input == "details":
                print("{up} mark up, {down} mark down".format(up=self.mark_up, down=self.mark_down))
                print("{} purchase limit.".format(self.purchase_limit))
            else:
                print(self.talk(shopper))


    def pc_selling(self, shopper):
        print(self.talk(shopper, "buy"))
        selling = True
        while selling == True:
            print("\n")
            print("You have {gold}g.".format(gold=shopper.inv.gold))
            choices_message = "BUY, EXIT, TALK, or an item by name or number."
            user_choice = self.get_choice_items(shopper.inv, "pc_sell", choices_message)
            if user_choice in toolbox.quit_options:
                selling = False
                return False
            elif user_choice == "buy":
                selling = False
                return self.pc_buying(shopper)
            elif user_choice == 'talk':
                print(self.talk(shopper, "talk"))
            elif user_choice in shopper.inv:
                raise "sell stuff"

    def pc_buying(self, shopper):
        print(self.talk(shopper, "sell"))
        buying = True
        while buying == True:
            print("\n")
            print("You have {gold}g.".format(gold=shopper.inv.gold))
            choices_messge = "SELL, EXIT, TALK, or an item by name or number."
            user_choice = self.get_choice_items(self.stock, "pc_buy", choices_messge)
            if user_choice in toolbox.quit_options:
                buying = False
                return False
            elif user_choice == "sell":
                buying = False
                return self.pc_selling(shopper)
            elif user_choice == "talk":
                print(self.talk(shopper, "talk"))
            elif user_choice in self.stock:
                raise "buy stuff"


if __name__ == '__main__':
    import character

    test_shop = Shop('test_type', 'discount')

    vending_machine = Shop('test_type', 'high_end')
    vending_machine.actions.remove('talk')
    print(test_shop.name)
    pc = character.Human("Player")
    pc_party = party.Party(pc, 'pcs')
    pc_party.inv.add_item(potion, quantity=3)
    pc_party.inv.gold = 400

    print (pc_party.inv)
    test_shop.in_shop(pc_party)