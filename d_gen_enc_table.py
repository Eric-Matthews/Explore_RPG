import random
# Creates random encounter lists.
# Base list for each terrain type (taking into account neighbouring tiles), with addition section for elemental affinities.
import d_toolbox
import d_character


# Format:
""" 
'type': '' - The encounter type of the encounter, for machine parsing.
Can be either COMBAT or EVENT. (ENVIRONMENT or LOCATION?)

'combat' - An encounter that goes direct to combat.
'npc_ps': {'npc_ps':{}...} - A dictionary of dictionary of enemy factions to encounter.
	'faction': '' - The string name of the faction of these NPCs.
	'no_enc': [int] - A list of ints, randomly picked to pick that many types from the npc_types list.
	'npc_types': [(TYPE, 'NAME')] - A list of the types of enemies that could be encountered for that faction in that encounter. The types of NPC are stored in tuples of (TYPE, 'NAME').
	
'event' - calls some other script somewhere to do some non-combat stuff. Things like environmental hazards, encounter modifiers. Maybe break apart if they get unwieldy or require lots of different input.
'events': [] - The list of possible events here.

'roll_on': '' - Roll again on a different encounter table.
"""
terrain_encounter_tables = {
	'castle': [{'type': 'combat', 'npc_ps':{'party_1': {'npc_types':[(d_character.Thrush, 'Swollamental')], 'no_enc': [1, 1, 2, 2, 3, 4], 'faction': 'wild'}}}, {'roll_on': 'faction'}],
	
	'city': [{'type': 'event', 'events':['pick pocket', 'secret shop']}, {'roll_on': 'faction'}],
	
	'desert': [{'type': 'event', 'events':['quicksand']}, 
	{'type': 'combat', 'npc_ps':{'party_1': {'npc_types':[(d_character.Jackalizard, 'Jackalizard')], 'no_enc': [1, 2, 2, 2, 3], 'faction': 'wild'}}}],
	
	'forest': [{'type': 'combat', 'npc_ps':{'party_1': {'npc_types':[(d_character.Umbrulf, 'Big Bad Shadow')], 'no_enc': [1], 'faction': 'wild'}}}, 
	{'type': 'combat', 'npc_ps':{'party_1': {'npc_types':[(d_character.Bramboar, 'Bramboar')], 'no_enc': [1, 1, 1, 2, 3], 'faction': 'wild'}}}],
	
	'mountains': [{'type': 'combat', 'npc_ps':{'party_1': {'npc_types':[(d_character.Froblin, 'Froblin')], 'no_enc': [1, 2, 2, 3], 'faction': 'froblins'}}}, 
	{'type': 'event', 'events':['rocks fall everybody dies.']}],
	
	'plains': [{'type': 'combat', 'npc_ps':{'party_1': {'npc_types':[(d_character.Character, 'Bandit')], 'no_enc': [1, 2, 2, 3], 'faction': 'bandits'}}}, 
	{'type': 'combat', 'npc_ps':{'party_1': {'npc_types':[(d_character.Froblin, 'Froblin')], 'no_enc': [1, 2, 2, 3], 'faction': 'froblins'}}}],
	
	'town': [{'type': 'combat', 'npc_ps':{'party_1': {'npc_types':[(d_character.Character, 'Bandit')], 'no_enc': [1, 2, 2, 3], 'faction': 'bandits'}}}, 
	{'type': 'combat', 'npc_ps':{'party_1': {'npc_types':[(d_character.Character, 'Bandit')], 'no_enc': [1, 2, 2, 3], 'faction': 'bandits'}, 'party_2': {'npc_types': [(d_character.Character, 'Merchant')], 'no_enc': [1, 1, 2], 'faction': 'civilisation'}}}, 
	{'type': 'event', 'events':['hidden shop']}, 
	{'roll_on': 'faction'}],
	
	'water': [{'type': 'combat', 'npc_ps':{'party_1': {'npc_types':[(d_character.Froblin, 'Froblin')], 'no_enc': [1, 2, 2, 3, 4], 'faction': 'froblins'}}}]}
	
faction_encounter_tables = {
	'wild': [{'type': 'combat', 'npc_ps':{'party_1': {'npc_types':[(d_character.Umbrulf, 'Big Bad Shadow')], 'no_enc': [1], 'faction': 'wild'}}}, 
	{'type': 'combat', 'npc_ps':{'party_1': {'npc_types':[(d_character.Thrush, 'Elethrush')], 'no_enc': [1, 1, 2, 3], 'faction': 'wild'}}}],
	
	'civilisation': [{'type': 'combat', 'npc_ps':{'party_1': {'npc_types':[(d_character.Character, 'Enforcer')], 'no_enc': [1, 2, 3], 'faction': 'civilisation'}}}, 
	{'type': 'combat', 'npc_ps':{'party_1': {'npc_types':[(d_character.Character, 'merchant')], 'no_enc': [1, 2, 3], 'faction': 'civilisation'}}}]}
	
def get_encounter(coords, region, ele_tuple = (0, 0, 0)):
	element = d_toolbox.get_element(ele_tuple)
	
	# Pick either the tile on, or an adjacent tile for the encounter to be generated from.
	if random.randint(0, 4) < 3:
		terrain = region[coords]['type']
		if __debug__: print "On tile"
	else:
		if __debug__: print "Adjacent tile"
		adjacents = region.collect_adjacents(coords)
		coords = random.choice(adjacents.keys())
		terrain = adjacents[coords]
	# And then make sure only one terrain type is passed to be rolled.
	print "An encounter in the {}!\n".format(terrain)
	terrain = random.choice(terrain.split())
	return get_encountered(coords, terrain, region, element)
	
def get_encountered(coords, terrain, region, element):
	enc = random.choice(terrain_encounter_tables[terrain])
	
	# roll on follow up tables if instructed to.
	if 'roll_on' in enc:
		if enc['roll_on'] == 'faction':
			enc = random.choice(faction_encounter_tables[region[coords]['faction']])
		elif enc['roll_on'] == 'elemental':
			print "An elemental encounter of {}.".format(element)
	
	if 'npc_ps' in enc:
		npc_parties = []
		for party in enc['npc_ps']:
			p_ed = enc['npc_ps'][party]
			npc_side = []
			no_enc = random.choice(p_ed['no_enc'])
			for i in range(0, no_enc):
				new_npc = random.choice(p_ed['npc_types'])
				if no_enc == 1: name = new_npc[1]
				else: name = new_npc[1] + " " + str(i)
				new_npc = new_npc[0](name = name)
				if 'merchant' in name.lower():
					print "Assigning different speech."
					new_npc.talk_lines = "This is a test speech, {talker_name}."
				npc_side.append(new_npc)
			npc_parties.append((npc_side, p_ed['faction']))
		return 'combat', npc_parties
	
	elif 'events' in enc:
		print enc
		return 'event', random.choice(enc['events'])
		
	else: return 'bug', 'Phew, you bugged out of encountering something... wait is that even good?'