import random
import copy

import d_toolbox
from d_items import mod_heal_potion, test_sword

potion = mod_heal_potion
sword = test_sword

class Shop(object):

	shop_stocks = {'test_type': [sword, potion]}
	
	value_data = {'discount': {'min_max': ( 1, 300), 'purchase_limit': 1000, 'mark_down': 0.5, 'mark_up': 1.8},
	'rip_off': {'min_max': ( 3, 500), 'purchase_limit': 900, 'mark_down': 0.3, 'mark_up': 2.3},
	'high_end': {'min_max': ( 250, 1300), 'purchase_limit': 2000, 'mark_down': 0.5, 'mark_up': 2.0},
	'luxury': {'min_max': ( 400, 2000), 'purchase_limit': 3000, 'mark_down': 0.3, 'mark_up': 2.3}}
	
	# Default shop actions, saved to instances for individual overwriting.
	default_actions = ['buy', 'sell', 'talk', 'exit']
	
	# Default talking lines, saved to instances, so they can be overwritten on an individual basis.
	default_talk_lines = ["I hear the {species} matroscka is opening soon.", "What ya talking to me for {name}?", "I wish I had a long coat and scary voice."]
	default_greet_lines = ["Greetin's stranger.", "Hello {species}"]
	default_bye_lines = ["Go carefully stranger.", "See ya round, {name}", "Come back soon {species}."]
	default_sell_lines = ["I'll buy it for a high price.", "Hahaha, thank you."]
	default_buy_lines = ["Hahaha, thank you.", "It'll serve you well, {name}."]
	default_nonesense_lines = ["I don't know what you mean.", "Beware the Jabberwocky {species}."]

	def __init__(self, stock_type, value_type, name = None, keeper = None):
		if name == None:
			name = 'gen_these'
		if keeper == None:
			keeper = 'Genned Keeper'
		
		if __name__ == '__main__':
			debug = True
		
		self.name = name
		self.keeper = keeper
		self.like_pc = 20
		self.actions = copy.copy(type(self).default_actions)
		
		# Saves the default talk lines, and the functions to call them to the instance, so they can be individually changed for specific shops.
		self.hello_lines = type(self).default_greet_lines
		self.hello_speak = type(self).default_greet
		self.farewell_lines = type(self).default_bye_lines
		self.farewell_speak = type(self).default_bye
		self.buying_lines = type(self).default_buy_lines
		self.buying_speak = type(self).default_buy_speak
		self.selling_lines = type(self).default_sell_lines
		self.selling_speak = type(self).default_sell_speak
		self.nonsense_lines = type(self).default_nonesense_lines
		self.talk_lines = type(self).default_talk_lines
		self.talk_speak = type(self).default_talk
		
		# Gives the individual shops a slightly random set of monetery variables, to keep things more interesting. And stopping players being able to work out the shop value types as easily.
		# Shop value types inform BUY/SELL prices, max purchase price, as well as stock base cost range.
		self.purchase_limit = int(type(self).value_data[value_type]['purchase_limit'] * (random.randint(80, 121) / 100.0))
		adjust = random.randint(8, 12) / 10.0
		self.mark_up = type(self).value_data[value_type]['mark_up'] * adjust
		if __name__ == '__main__' and __debug__ == True: print "{} x {} = {}".format(type(self).value_data[value_type]['mark_up'], adjust, self.mark_up)
		adjust = random.randint(8, 12) / 10.0
		self.mark_down = type(self).value_data[value_type]['mark_down'] * adjust
		if __name__ == '__main__' and __debug__ == True: print "{} x {} = {}".format(type(self).value_data[value_type]['mark_down'], adjust, self.mark_down)
		
		self.stock_gen = 33
		self.base_stock = self.get_base_stock(stock_type, value_type)
		self.stock = {}
		self.gen_stock()
	
	# Returns the base list of items the shop type can sell.
	# Gets list of all items for stock_type, and then removes items outside the price range of the shop, from value_type.
	def get_base_stock(self, stock_type, value_type):
		base_stock = type(self).shop_stocks[stock_type]
		min, max = type(self).value_data[value_type]['min_max']
		for item in base_stock:
			if min <= item.price <= max == False:
				base_stock.remove(item)
		return base_stock
	
	# Generates the stock of the shop from its base stock.
	# Adds a few potential items each time its called. Has space to sell some off, too.
	def gen_stock(self):
		if len(self.stock) > 1:
			# sell off some items in downtime too, for more verisimilitude.
			pass
		for i in range(1, random.randint(3, 5)):
			item = random.choice(self.base_stock)
			type_min, type_max = type(item).stock_min_max
			quantity = random.randint(type_min, type_max)
			self.add_stock(item, quantity)
	
	# Add an item to the shop's stock.
	def add_stock(self, item, quantity):
		if item.name.lower() in self.stock:
			self.stock[item.name.lower()]['quantity'] += quantity
		else: self.stock[item.name.lower()] = {'quantity': quantity, 'item': item, 'visible': True}
	
	
	def rem_stock(self, item_name, quantity = 1):
		if hasattr(item_name, 'name') == True:
			item_name = item_name.name
		if quantity > self.stock[item_name]['quantity']: print "ERROR too much removed stock!"
		self.stock[item_name]['quantity'] -= quantity
		if self.stock[item_name]['quantity'] < 1:
			del self.stock[item_name]
	
	# The functions for talking. Return lines of dialogue to be printed.
	def default_talk(self, talker, lines = None):
		if lines == None: lines = self.talk_lines
		if self.like_pc > 0: 
			return self.get_random_line(talker, lines)
		else: return "Go away, wannabe thief."
		
	def default_greet(self, talker, lines = None):
		if lines == None: lines = self.hello_lines
		if self.like_pc > 0:
			return self.get_random_line(talker, lines)
		else: return "Nothing for you here."
		
	def default_bye(self, talker, lines = None):
		if lines == None: lines = self.farewell_lines
		return self.get_random_line(talker, lines)
		
	def default_buy_speak(self, talker, lines = None):
		if lines == None: lines = self.buying_lines
		return self.get_random_line(talker, lines)
		
	def default_sell_speak(self, talker, lines = None):
		if lines == None: lines = self.selling_lines
		return self.get_random_line(talker, lines)
	
	def get_random_line(self, talker, lines):
		return random.choice(lines).format(name = talker.name, species = talker.species, faction = 'PC Party')
	
	# Returns a string of the actions available in that shop.
	def make_action_string(self):
		action_string = []
		for item in self.actions:
			action_string.append(item.upper())
		action_string.insert(len(action_string) - 1, 'or')
		return " ".join(action_string)
	
	# Prints a list of items, with quantity and price.
	def print_stock(self, stock, mode):
		if mode == 'buy_from': price_mod = self.mark_down
		elif mode == 'sell_to': price_mod = self.mark_up
		for item in stock:
			if 'visible' not in item or item['visible'] == True:
				price = self.get_price(stock[item], mode)
				print "{quantity}x {name} - {cost}g each".format(name = stock[item]['item'].name, cost = price, quantity = stock[item]['quantity'])
		else:
			if len(stock) < 1:
				print "There's nothing for sale."
	
	# Returns the buy/sell price of items for the shop.
	def get_price(self, stock_entry, mode):
		# Get the default price mods, and use them if none for specific item.
		if mode == 'buy_from': price_mod = self.mark_down
		elif mode == 'sell_to': price_mod = self.mark_up
		if 'price_mod' not in stock_entry: item_price_mod = price_mod
		else: item_price_mod = stock_entry['price_mod']
		# Then work out the actual value of the item, capped for buying at the shop purchase_limit.
		value = stock_entry['item'].price * item_price_mod
		if __name__ == '__main__' and __debug__ == True: print "{} changed to {}".format(stock_entry['item'].price, value)
		if mode == 'buy_from' and value > self.purchase_limit:
			value = self.purchase_limit
		return int(value)
		
	
	def in_shop(self, shopper):
		if self.like_pc > 0: shop = True
		else: shop = False
		print self.hello_speak(self, shopper)
		while shop == True:
			print "\n"
			print self.make_action_string()
			input = raw_input('> ').lower()
			if input == 'buy':
				if len(self.stock) > 0: self.pc_buying(shopper)
				else: print "Out of stock."
			elif input == 'sell':
				if len(shopper.inv) > 0: self.pc_selling(shopper)
				else: print "You've nothing to sell."
			elif input == 'talk':
				print self.talk_speak(self, shopper)
			elif input in d_toolbox.exit_commands:
				print self.farewell_speak(self, shopper)
				shop = False
			elif input == "steal":
				print """Petty theft coming soon, you criminal."""
				self.like_pc -= 10
			elif input == "help":
				print "You're certain there's some way to make this any more clear?"
				print "Because neither I, nor {}, can think of one.".format(self.name)
				print "It's not as if you're not using the keyboard or anything..."
			elif __name__ == '__main__' and __debug__ == True and input == "details":
				print "{up} mark up, {down} mark down".format(up = self.mark_up, down = self.mark_down)
				print "{} purchase limit.".format(self.purchase_limit)
			else:
				print self.get_random_line(shopper, self.nonsense_lines)

	
	def pc_buying(self, shopper):
		print "What're ya buyin'?"
		buying = True
		selling = False
		self.print_stock(self.stock, 'sell_to')
		while buying == True:
			print "\n"
			print "You have {gold}g.".format(gold = shopper.inv.gold)
			print "STOCK, SELL, EXIT, or an item name."
			input = raw_input('> ').lower()	
			if input in d_toolbox.exit_commands:
				buying = False
			elif input in self.stock:
				item_cost = self.get_price(self.stock[input], 'sell_to')
				if shopper.inv.gold >= item_cost:
					print "Bought {}.".format(input.title())
					shopper.inv.gold -= item_cost
					shopper.inv.item_add(self.stock[input]['item'], 1)
					self.rem_stock(input)
					self.like_pc += 1
					print self.buying_speak(self, shopper)
				else: print "You only have {pc_gold}g, but need {cost}g".format(pc_gold = shopper.inv.gold, cost = item_cost)
			elif input in ['inv', 'stock']:
				self.print_stock(self.stock, 'sell_to')
			elif input == 'sell':
				if len(shopper.inv) > 0:
					buying = False
					selling = True
				else: print "You've nothing to sell."
			else: print "Got none of that."
		else:
			if selling == True:
				self.pc_selling(shopper)
			else: print "A pleasure dealing wit' ya."
	
	def pc_selling(self, shopper):
		print "What're ya sellin'?"
		selling = True
		buying = False
		self.print_stock(shopper.inv, 'buy_from')
		while selling == True:
			print "\n"
			print "INV, BUY, EXIT, or an item name."
			input = raw_input('> ').lower()	
			if input in d_toolbox.exit_commands:
				selling = False
			elif input in shopper.inv:
				print "Sold {}.".format(input.title())
				shopper.inv.gold += self.get_price(shopper.inv[input], 'buy_from')
				self.add_stock(shopper.inv[input]['item'], 1)
				shopper.inv.item_rem(input)
				print self.selling_speak(self, shopper)
			elif input in ['inv', 'stock']:
				self.print_stock(shopper.inv, 'buy_from')
			elif input == 'buy':
				if len(self.stock) > 0:
					selling = False
					buying = True
				else: print "Out of stock."
			else: print "You can't sell {}.".format(input)
		else:
			if buying == True:
				self.pc_buying(shopper)
			else: print "A pleasure dealing wit' ya."		

	
if __name__ == '__main__':
	import d_character

	test_shop = Shop('test_type', 'discount')
	
	vending_machine = Shop('test_type', 'high_end')
	vending_machine.actions.remove('talk')
	print test_shop.name
	pc = d_character.Character()
	pc.inv.item_add(potion, 3)
	pc.inv.gold = 400
	
	test_shop.in_shop(pc)