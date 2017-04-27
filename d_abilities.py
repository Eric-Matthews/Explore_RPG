from random import randint
# Abilities, which are used in combat by the characters in the game.
import d_toolbox

def roll_attack_damage(attacking_char):
	dam_roll = attacking_char.attack.get('dice')
	if dam_roll == None: dam_roll = attacking_char.unarmed_attack['dice']
	damage = d_toolbox.dice_roller(dam_roll) + (int(attacking_char.str) / 3)
	return damage
	
def attack(attacker, target):
	damage = roll_attack_damage(attacker)
	target.take_damage(damage)
	return damage
	
def look(looker, target):
	print "{} looks at {}.".format(looker.name, target.name)
	print "If you could quantify health {} would be at {}.".format(target.name, target.hp)
	
def item(user, target):
	print "Use which item?"
	user.inv.print_inv()
	print "Pretend its been used, ok?"
	"""Get this working."""

class Ability(object):
	'Things that the character can do in a fight, using up CTG.'
	'Some can also be performed outside of battle.'
	# effect = the function that enacts the impact of using the ability.
	# disp_name = the name to display to the player when the ability is used.
	# ctg_cost = the amount of CTG (Combat Time Gague) spent to use it.
	# targets = [] of valid target types for the ability.
	# success = the % of successful use of the ability. Rolled when attempting to use, not the same as missing.
	
	def __init__(self, disp_name, effect, ctg_cost, targets, success):
		self.effect = effect
		self.name = disp_name
		self.ctg_cost = ctg_cost
		self.targets = targets
		self.success = success
		
	def __str__(self):
		return self.name
		
	# To be called before trying to use the ability.
	# Checks to ensure the target is valid.
	def target_valid(self, target_type):
		return target_type in self.targets
		
	# Check success, and then run the effect of the ability.
	def use_ability(self, user, target = None):
		user.ctg -= self.ctg_cost
		if randint(0, 101) < self.success:
			return self.effect(user, target)
		else: return 0
		
		

base_attack = Ability('attack', attack, 35, ['any'], 100)
base_look = Ability('look', look, 10, ['any'], 100)