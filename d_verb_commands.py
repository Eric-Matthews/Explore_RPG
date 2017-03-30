from d_toolbox import *
import d_help

# Holds the verb commands to be called by the game.
# Each command must be in the VERB BANK as well as have a function which uses the exact same name.
# The main game can pass NONE to the functions. Depending on the command this may or may not be valid input.

# All must return a string to print, and whether or not an in game day has passed with the time taken as a boolean.
# All have to return this as part of the automated and segregated way that these functions are implemented.
# Likewise this is why all take the PC as well as a second string as parameters.

# Put all commands the player can type to take action into this list.
verb_bank = ['dice', 'drop', 'equip', 'help', 'inv', 'look', 'unequip', 'use']

def dice(pc, dice_string):
	if dice_string == None: dice_string = ''
	if  dice_string.replace('+','', 1).replace('d', '', 1).isdigit() == True:
		to_print = str(dice_roller(dice_string))
	else: to_print = "Please use the format 'DICE 1d2+3'. The +X is optional."
	return to_print, False
	
def drop(pc, to_drop):
	if to_drop == None:
		print "You drop to the dirt. Ow."
		return "Better get up and moving.", True
	elif to_drop.title() in pc.inv:
		if 'DROP' in pc.inv[to_drop.title()]['item'].actions:
			pc.inv.item_rem(to_drop.title())
			return "You dispose of the {}.".format(to_drop), False
		else: return "You think the better of discarding the {}".format(to_drop), False
	else: return "You seem to have already lost the {}.".format(to_drop), False
	
def equip(pc, to_equip):
	if to_equip == None:
		return "You'll need to be more specific.", False
	elif to_equip in pc.inv:
		if hasattr(pc.inv[to_equip]['item'], 'equip'):
			pc.inv[to_equip]['item'].equip(pc)
			return "", False
		else: return "You can't equip that {}.".format(to_equip), False
	else: 
		return "You don't have any equipable {}.".format(to_equip), False

def help(pc, location):
	to_print = d_help.help_command(pc, location) 
	return to_print, False
	
def inv(pc, passed_string):
	pc.inv.print_inv()
	return '', False
	
def look(pc, looked_at_data):
	print looked_at_data
	to_print = "Not much here."
	if 'long desc' in looked_at_data: 
		to_print = looked_at_data['long desc']
	elif looked_at_data.lower() in ['me', 'char', 'self']:
		pc.print_stats()
		to_print = ''
	return to_print, False
	
def unequip(pc, to_unequip):
	if to_unequip == None:
		return "You'll need to be more specific.", False
	for slot, equipment in pc.equip_slots.items():
		if hasattr(equipment, 'name'):
			if equipment.name.lower() == to_unequip:
				equipment.unequip(pc)
				return "", False
	else: 
		return "You have no {} equipped.".format(to_unequip), False
	
def use(pc, to_use):
	if to_use == None:
		return "You'll need to be more specific", False
	elif to_use in pc.inv: 
		pc.inv.item_use(to_use, pc, pc)
		return "item used.", False
	else:
		return "You don't have any {} to use.".format(to_use), False