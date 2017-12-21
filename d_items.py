# item classes.
import d_toolbox

class Item(object):
	
	stock_min_max = (2, 4)

	def __init__(self, display_name, weight, price, actions = None, effects = {}, element = None):
		if actions == None: actions = []
		self.name = display_name
		self.weight = weight
		self.price = price
		self.element = element
		self.actions = ['THROW', 'DROP'] + actions
		# Automate everyitem effects to sensible limits.
		if weight < 1: throw_die = 1
		else: throw_die = weight
		self.effects = dict({'throw':{'dice':'2d{}'.format(throw_die), 
		'on_hit': [],
		'element': element},
		'drop':{}}.items() + effects.items())
	
	def use(self, user, target = None):
		if 'use' in self.effects:
			print user.name + " uses the " + self.name + "!"
			return True
		else: 
			print "You can't use " + self.name + "."
			return False

class Equipment(Item):
	
	stock_min_max = (1, 3)
	
	def __init__(self, display_name, weight, price, equip_loc, actions = [], effects = {}, element = None):
		actions += ['EQUIP']
		effects = dict({'equip':{'slots':equip_loc}}.items() + effects.items())
		Item.__init__(self, display_name, weight, price, actions, effects)
	
	def equip(self, equipee):
		# For each slot that the item takes up, unequip anything in each of those slots, ensuring that all slots of a multi-slot equipped item are also emptied.
		for slot in self.effects['equip']['slots']:
			if equipee.equipment_slots[slot] != None:
				equipee.equipment_slots[slot].unequip(equipee)
			equipee.equipment_slots[slot] = self
			self.quantity = 1
		equipee.inv.item_rem(self.name.lower())
		if 'passive' in self.effects['equip']:
			# Code to add passive bonuses here.
			"""for k, v in passive: if k == armour equipee.armour += v"""
			print 'You gain a passive bonus'
			pass
		if 'attack' in self.effects:
			equipee.attack[self.name] = self.effects['attack']
		print "Equipped " + self.name
		
	def unequip(self, unequipee):
		# Removes an item from all of the slots it takes up, as well as removing any bonuses it gives to the equipped character.
		if 'passive' in self.effects['equip']:
			# Code to remove passive bonuses here.
			print 'You lose a passive bonus'
			pass
		if 'attack' in self.effects:
			del unequipee.attack[self.name]
		for equipped_slot in self.effects['equip']['slots']:
			unequipee.equipment_slots[equipped_slot] = None
		unequipee.inv.item_add(self)
		print "Unequipped " + self.name
	
	def use(self, equipee):
		# check if equipment has multiple use effects.
		if self.effect <> ['equip']:
			actions = ' or '.join(upper(e) for e in self.effect)
			command = raw_input(actions + "?")
			# do stuff when effects chosen.
		# otherwise equip it.
		if self.effect == ['equip'] or command.lower() == 'equip':
			self.equip(equipee)		
		
class Weapon(Equipment):
	def __init__(self, display_name, weight, price, damage, actions = [], effects = {}, equip_loc = None, on_hit = None, element = None):
		if on_hit == None: on_hit = []
		actions += ['ATTACK']
		effects = dict({'attack':{'dice': damage, 'on_hit': on_hit}}.items() + effects.items()) 
		if equip_loc == None: equip_loc = ['hand_1']
		Equipment.__init__(self, display_name, weight, price, equip_loc, actions, effects, element)

class Potion(Item):
	
	stock_min_max = (2, 6)

	def __init__(self, display_name, weight, price, affect, element = None):
		effect = {'drink': affect, 'throw': affect}
		Item.__init__(self, display_name, weight, price, ['DRINK'], effect, element)
	
	def use(self, user, target = None):
		if target in [None, user, user.name]:
			self.drink(target)
		else: 
			self.drink(target)
		return True
	
	def drink(self, target = None):
		if target == None: target = 'you'
		print target.name + ' is ' + self.effects['drink']['element'] + "'d."
		value = d_toolbox.dice_roller(self.effects['drink']['dice'])
		target.work_out_damage(value, self.effects['drink']['element'])
		
		
class Healing_Potion(Potion):
	def __init__(self, display_name, weight, price, dice, on_use = []):
		# xDy+z format dice to roll
		affect = {'dice': dice, 'element': 'heal', 'on_use': on_use}
		Potion.__init__(self, display_name, weight, price, affect)
		
		

mod_heal_potion = Healing_Potion('Blue Potion', 0.1, 10, '4d4+2')
test_sword = Weapon('Training Sword', 5, 20, '3d2+1')
doodad = Item('Thing-a-ma-bug', 1, 42) 