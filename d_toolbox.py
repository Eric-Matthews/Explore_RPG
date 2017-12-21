from random import randint
from math import sqrt 
# Does not import any of my own modules.
# Bottom level functions used in many places.

# In game months, and how they affect the elemental balance.
# 100hot/cold-100, 100dry/wet-100, 100light/shade-100
month_data = {'sun': (50, 0, 50),
	'glowshroom': (-50, 0, 50),
	'crystal': (0, 50, 50),
	'shower': (0, -50, 50),
	'shadowflame': (50, 0, -50),
	'moon': (-50, 0, -50),
	'cave': (0, 50, -50),
	'storm': (0, -50, -50),
	'air': (50, -50, 0),
	'water': (-50, -50, 0),
	'fire': (50, 50, 0),
	'earth': (-50, 50, 0)}

opposed_elements = {'fire': 'water', 'air': 'earth', 'water':'fire', 'earth': 'air', 'light': 'shade', 'shade': 'light'}
	
# Default values of the factions; how they get along with each other.
faction_relations = {'bandits': {'pcs': -10, 'bandits': 20, 'civilisation': -30, 'froblins': -20, 'wild': -40},
	'civilisation': {'pcs': 10, 'bandits': -40, 'civilisation': 20, 'froblins': -20, 'wild': -30}, 
	'froblins': {'pcs': -10, 'bandits': -20, 'civilisation': -30, 'froblins': 30, 'wild': -40},
	'wild': {'pcs': -20, 'bandits': -20, 'civilisation': -30, 'froblins': -10, 'wild': -5}}

factions_with_memory = ['civilisation', 'froblins', 'bandits']

exit_commands = ['exit', 'back', 'quit', 'just let it end', "i'm outta here"]
sheet_commands = ['me', 'char', 'sheet']


# Gets the month of the game year from the list.
def set_month(month_order = ['sun', 'glowshroom', 'crystal', 'shower', 'shadowflame', 'moon', 'cave', 'storm', 'air', 'water', 'fire', 'earth']):
	new_month = month_order.pop(0)
	month_order.append(new_month)
	return new_month

def dice_roller(dice_string):
	# rolls dice given in the format of xDy+z, with +z being optional.
	# returns the total.
	no_rolls, rest = int(dice_string.split('d',1)[0]), dice_string.split('d',1)[1]
	if '+' in rest: 
		die_size, total_roll = int(rest.split('+', 1)[0]), int(rest.split('+', 1)[1])
	else: 
		total_roll = 0
		die_size = int(rest)
	for i in range(0, no_rolls):
		total_roll += randint(1, die_size)
	return total_roll
	
# check if command is valid move to nearby space
# takes command to check, and optional specific movement to check it is
def check_is_move(to_check, specific = None):
	# dictionary of valid move commands keyed to their direction of movement
	checks = {'move_n': ['n', 'north'], 
	'move_e': ['e', 'east'], 
	'move_s': ['s', 'south'], 
	'move_w': ['w', 'west'],
	'move_ne': ["ne", "north east", "en", "east north"],
	'move_nw': ["nw", "north west", "wn", "west north"],
	'move_se': ["se", "south east", "es", "east south"],
	'move_sw': ["sw", "south west", "ws", "west south"]}
	# list to be filled with direction commands found
	valids = []
	if specific:
		specifics = specific.split()
		for specific_command in specifics:
			valids += checks['move_' + specific_command]
	else:
		valids = (checks['move_n'] + checks['move_e'] + checks['move_s'] +
		checks['move_w'] + checks['move_ne'] + checks['move_nw'] + checks['move_se'] + checks['move_sw'])
	if to_check:	
		if to_check.lower() in valids:
			return True
		else: return False
	else: return False

def get_element(ele_tuple):
	hc, dw, ls = ele_tuple
	if hc >= 75: 
		if dw >= 50: element = 'fire'
		elif dw <= -50: element = 'air'
		else: element = 'hot'
	elif hc <= -75:
		if dw >= 50: element = 'earth'
		elif dw <= -50: element = 'water'
		else: element = 'cold'
	elif -50 < hc < 50:
		if dw >= 75: element = 'dry'
		elif dw <= -75: element = 'wet'
		else: element = None
	if ls >= 75:
		if element == None or ls > (sqrt(dw**2) + sqrt(hc**2)): element = 'light'
	elif ls <= -75:
		if element == None or ls < (-sqrt(dw**2) + -sqrt(hc**2)): element = 'shade'
	return element