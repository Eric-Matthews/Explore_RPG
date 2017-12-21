# Attempt to make a more sensible and streamlined character class.
# Uses object types as its values for easier modification and use.

import random
import copy
import math as maths

import d_toolbox
import d_abilities
import d_items

class Stat(object):
	'Measure the qualities of a CHARACTER.'
	
	def __init__(self, base):
	# Create the stat with its base value for that character.
		self.base_value = base
		self.cur_value = base
		self.modifiers = {}
	
	def __str__(self):
	# How the stat is printed.
		return str(self.cur_value) + '/' + str(self.base_value)
		
	def __int__(self):
		return int(self.cur_value)
	
	def calc_cur(self):
	# Recalculates the current value of the stat.
		self.cur_value = self.base_value
		for k, p in self.modifiers.items():
			# if modifier is a wound, subtract from the value, rather than add.
			if k == 'wound': 
				self.cur_value -= p
			else: self.cur_value += p
			
	def get_percent(self):
		return int((self.cur_value / self.base_value) * 100)
			
	def add_modifier(self, mod_type, value):
	# Adds a modifier of given TYPE to the stat modifier dictionary.
	# Only WOUNDS is a cumulative TYPE. All others are overwritten.
		if mod_type in self.modifiers and mod_type == 'wound':
			self.modifiers[mod_type] += value
		else: 
			self.modifiers[mod_type] = value
		if 'wound' in self.modifiers and self.modifiers['wound'] < 0:
			self.modifiers['wound'] = 0
		self.calc_cur()

class HP(Stat):
	'Measures a derived qualitiy of a CHARACTER.'
	
	def __init__(self, base, char):
		self.base = base
		self.char = char
		HP.calc_base(self)
		self.cur_value = self.base_value
		self.modifiers = {}
		
	def calc_base(self):
		self.base_value = 0
		for item in self.base:
			self.base_value += getattr(self.char, item).cur_value

			
class Inventory(dict):
	"A custom dictionary for a CHARACTER's items"
	default_efficiency = 2
	
	def __init__(self, str, end, efficiency = None):
		"If no carry efficiency passed, use the default value. This stat is for quads, etc."
		Inventory.update_max_weight(self, str, end, efficiency)
		self.cur_weight = 0
		self.gold = 0
	
	def __str__(self):
		return "{weight}\n {gold}g".format(weight = str(self.cur_weight) + '/' + str(self.max_weight), gold = self.gold)
	
	def print_inv(self):
		print 'Encumberance: ' + str(self)
		for item in self:
			print self[item]['item'].name +'; ' + str(self[item]['item'].weight) + ' x' + str(self[item]['quantity'])
	
	def update_max_weight(self, str, end, efficiency = None):
		# updates the max capacity of the inventory object.
		# Should be called when base stats are updated.
		if efficiency == None: efficiency = Inventory.default_efficiency
		self.max_weight = (str + end) * efficiency
	
	def item_add(self, item, quantity = None):
		if quantity == None: quantity = 1
		self.cur_weight += (quantity * item.weight)
		if item.name.lower() in self:
			self[item.name.lower()]['quantity'] += quantity
		else: 
			self[item.name.lower()] = {}
			self[item.name.lower()]['item'] = item
			self[item.name.lower()]['quantity'] = quantity
		if __debug__ == False: print "Added {}.".format(item)
			
	def item_rem(self, item, quantity = 1):
		if hasattr(item, 'name'): item = item.name.lower()
		if item in self:
			self[item]['quantity'] -= quantity
			self.cur_weight -= self[item]['item'].weight
			if self[item]['quantity'] <= 0:
				del self[item]
		else: 
			print str(item).title() + " not in inventory."
		
	def item_use(self, item, user, target):
	# Check if the item can be used, if so use it and remove from INV.
		if isinstance(item, d_items.Item): item = item.name
		if hasattr(self[item]['item'], 'use'): 
			new_day = self[item]['item'].use(user, target)
			self.item_rem(item)
			return False
		else:
			print "Can't use that."
			return False
	
	# Checks to see if there ITEM is in the INV.
	# Works with both ITEMs and a str of item name.
	def has_item(self, item):
		if isinstance(item, d_items.Item): item = item.name
		elif item == None: item = 'lorem ipsum'
		if item in self: 
			return self[item]
		else: 
			return False
		
class Character(object):
	'A creature in the game, with STATS, INVENTORY, and such.'
	# This race's base values that individuals share.
	species = "human"
	base_stats = {'int': 10, 'cur': 10, 'spd': 10, 'end': 10, 'str': 10, 'vit': 10}
	stat_order = ['str', 'vit', 'int', 'cur', 'end', 'spd']
	hp_base = ['end', 'vit']
	equipment_slots = {'hand_1': None, 'hand_2': None, 'head': None, 'torso': None, 'feet': None}
	unarmed_attack = {'dice': '2d3', 'name': "unarmed", 'on_hit':None}
	elemental_resz = {}
	racial_traits = []
	senses = []
	movement = ['walk']
	abilities = {'TALK': 'talk', 'INV': 'inv', 'FLEE': 'flee', 'ATTACK': d_abilities.base_attack, 'LOOK': d_abilities.base_look}
	map_view_dist = 1
	armour = 0
	
	default_talk_lines = "{talker_name} converses with {self_name}."
	
	def __init__(self, name = None, stat_bonus = 0):
	# For each stat the character can have, create that stat from default values.
		for k, v in type(self).base_stats.items():
			stat_value = Stat(v + random.randint(-1, 1) + stat_bonus)
			setattr(self, k, stat_value)
		self.hp = HP(type(self).hp_base, self)
		self.inv = Inventory(self.str.cur_value, self.end.cur_value)
		self.equip_slots = type(self).equipment_slots
		
		self.armour = type(self).armour
		self.unarmed = type(self).unarmed_attack
		self.attack = {}
		
		self.elemental_resz = type(self).elemental_resz
		self.senses = type(self).senses
		self.abilities = type(self).abilities
		self.traits = type(self).racial_traits
		self.map_view_dist = type(self).map_view_dist
		if name == None:
			name = type(self).species
		self.name = name.title()
		self.sign = d_toolbox.set_month()
		self.elemental_tup = d_toolbox.month_data[self.sign]
		
		self.talk_lines = type(self).default_talk_lines
		
		self.kills = 0
		self.is_pc = False
	
	def use_item(self, command, item_to_use, target = None):
		pass
	
	def print_stats(self):
		# prints all of the CHAR's stats to screen in human readable way.
		print self.name
		if len(self.attack) < 1: attack = self.unarmed
		else: attack = self.attack
		print "Attack: {}".format(attack)
		print 'HP' + ': ' + str(getattr(self, 'hp'))
		for stat in self.stat_order:
			if stat in type(self).base_stats:
				stat_mods = getattr(self, stat).modifiers
				print stat.capitalize()	+ ': ' + str(getattr(self, stat).cur_value)
				if stat_mods.items() > 0:
					for k, p in stat_mods.items():
						print k.capitalize() +': ' + str(p)
	
	def get_stat(self, stat):
		if hasattr(self, stat):
			return int(getattr(self, stat))
		else:
			return "No stat"
	
	def stat_change(self, stat, mod_type, value):
		# apply a MOD_TYPE modifier of VALUE to stat STAT.
		getattr(self, stat).add_modifier(mod_type, value)
		if self.is_pc == True: 
			print self.name + "- " + stat + ': ' + str(getattr(self, stat))
		
	def take_damage(self, value):
		self.stat_change('hp', 'wound', value)
		if value < 0: heal_take = 'heal'
		else: heal_take = 'take'
		print "{} {}s {} damage".format(self.name, heal_take, int(maths.sqrt(value**2)))
	
	
	# Code to be executed when CHAR dies.
	def killed(self, killer, loot):
		'Code that runs when a CHAR dies, updating their PARTY\'s HOSTILITY{}, ACTIVES[], and COMBAT()de LOOT[] data.'
		self.party.actives.remove(self)
		if self.party.faction in d_toolbox.factions_with_memory:
			d_toolbox.faction_relations[self.party.faction][killer.party.faction] -= 10
		if killer.party.name in self.party.hostility: 
			self.party.hostility[killer.party.name][0] += 10
		else: self.party.hostility[killer.party.name] = [20, killer.party]
		for item in self.inv:
			dropped_item = self.inv[item]['item']
			dropped_quan = self.inv[item]['quantity']
			loot.append((dropped_item, dropped_quan))
		if __debug__ == False:
			print loot
	
	def work_out_damage(self, value, element):
		if element in self.elemental_resz:
			value = value * elemental_resz[element]
		if element == 'heal':
			value *= -1
		self.take_damage(value)
		
	def do_rest(self, rest_amount):
		if hasattr(self, 'long_term_effects') == True:
			print "Do long term effect stuff."
		for stat in (type(self).stat_order + ['hp']):
			if 'wound' in getattr(self, stat).modifiers:
				getattr(self, stat).modifiers['wound'] = getattr(self, stat).modifiers['wound'] /2
				getattr(self, stat).calc_cur()
		print "What a good rest."
	
	def print_abilities(self):
		moves = []
		for ability in self.abilities:
			moves.append(str(self.abilities[ability]).upper())
		return str(moves)
		
	def looked_at(self, looker_senses):
		return "A {}, who looks {}.".format(self.species, str(self.hp))
		
	def talked_to(self, talkee):
		print self.talk_lines.format(talker_name = talkee.name, self_name = self.name)


class Ghost(Character):
	'An incorporeal creature.'
	species = "ghost"
	base_stats = {'int': 10, 'cur': 3, 'spd': 10, 'end': 10, 'str': 10}
	hp_base = ['int', 'end']
	racial_traits = ['incorporeal']
	movement = ['float']

class Monimal(Character):
	'This class is for the monster-animals that the PC encounters, fights, and collects/tames through their adventures.'
	species = "Monimal"
	abilities = {'FLEE': 'flee', 'ATTACK': d_abilities.base_attack, 'LOOK': d_abilities.base_look}
	formes = []
	element = None
	
	def default_talk(self, talkee):
		print "The {} does not respond to {} attempts at dialogue.".format(self.species, talkee.name)
	
	def __init__(self, name = None):
		Character.__init__(self, name)
		self.element = type(self).element
		if self.element != None:
			self.elemental_resz[self.element] = 0.5
			self.elemental_resz[d_toolbox.opposed_elements[self.element]] = 2
		if self.element in self.formes: self.cur_forme = self.element
		else: self.cur_forme = 'neutral'
		
		
	def looked_at(self, looker_senses):
		return "A {} {}, who looks {}.".format(self.cur_forme, self.species, str(self.hp))
		
	
class Thrush(Monimal):
	'Elementally adaptive birds. Fast, but vulnerable.'
	species = "thrush"
	base_stats = {'int': 3, 'cur': 10, 'spd': 14, 'end': 6, 'str': 4, 'vit': 4}
	hp_base = ['end', 'vit']
	equipment_slots = {'talons': None, 'head': None}
	unarmed_attack = {'dice': '1d4', 'name': "peck", 'on_hit':None}
	movement = ['fly', 'walk']
	racial_traits = ['adaptive']
	element = random.choice(['fire', 'air', 'water', 'earth', None])
	formes = ['fire', 'air', 'water', 'earth', 'neutral']
	
class Bramboar(Monimal):
	species = "Bramboar"
	base_stats = {'int': 2, 'cur': 8, 'spd': 8, 'end': 12, 'str': 14, 'vit': 14}
	hp_base = ['end', 'vit']
	equipment_slots = {'torso': None, 'head': None}
	senses = ['smell']
	unarmed_attack = {'dice': '2d6', 'name': "gore", 'on_hit':None}
	element = 'earth'
	armour = 2
	
class Jackalizard(Monimal):
	species = "Jackalizard"
	base_stats = {'int': 4, 'cur': 10, 'spd': 10, 'end': 12, 'str': 11, 'vit': 12}
	hp_base = ['end', 'vit']
	equipment_slots = {'torso': None, 'head': None}
	senses = ['uv']
	unarmed_attack = {'dice': '2d3', 'name': "bite", 'on_hit':None}
	element = random.choice(['earth', 'fire'])
	armour = 1
	
class Umbrulf(Monimal):
	species = "Umbrulf"
	base_stats = {'int': 3, 'cur': 12, 'spd': 9, 'end': 13, 'str': 16}
	hp_base = ['end', 'str']
	equipment_slots = {'torso': None, 'head': None}
	senses = ['life']
	unarmed_attack = {'dice': '3d5', 'name': "bite", 'on_hit':None}
	element = 'shade'
	racial_traits = ['incorporeal']
	senses = ['scent']
	armour = 1
	
class Froblin(Monimal):
	species = "Froblin"
	base_stats = {'int': 4, 'cur': 9, 'spd': 9, 'end': 10, 'str': 8, 'vit': 9}
	hp_base = ['end', 'vit']
	equipment_slots = {'hand_1': None, 'hand_2': None, 'torso': None, 'head': None}
	unarmed_attack = {'dice': '1d5', 'name': "bite", 'on_hit':None}
	racial_traits = ['adaptive']
	movement = ['swim']
	formes = ['earth', 'water', 'neutral']
	
	
# If main do this shiz to test stuff as an island.
if __name__ == '__main__':
	from d_items import mod_heal_potion, test_sword
	from d_toolbox import dice_roller
	potion_to_add = mod_heal_potion
	sword = test_sword
	print "Running!"
	PC = Character()
	PC.print_stats()
	print ''
	ghost = Ghost()
	ghost.print_stats()
	end = False
	while end == False:
		input = raw_input('> ').lower()
		if input in ['exit', 'quit']:
			end = True
		elif input in ['wound', 'enchant']:
		# tests to see if wounds / enchant functions work.
			stat = PC.stat_order[random.randint(0, 5)]
			PC.stat_change(stat, input, random.randint(1, 5))
		elif input == 'add':
			PC.inv.item_add(potion_to_add)
		elif input == 'equip':
			sword.equip(PC)
		elif input == 'inv':
			PC.inv.print_inv()
		elif input == 'print':
			PC.print_stats()
	quit()