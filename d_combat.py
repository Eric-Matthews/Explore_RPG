import random
# Module for combat. Takes list of PC_party and x lists of NPC_parties, and then has them fight to the death.
import d_toolbox

class Party(object):
	'Holds characters on a side in a fight, and some related data.'
	
	def __init__(self, characters, faction = 'None'):
		self.chars = characters
		
		# A holder for number of characters still capable of fighting in the party.
		self.actives = 0
		for char in self.chars:
			char.party = self
			self.actives += 1
		
		self.name = self.get_team_name(characters)
		if faction == 'pcs': 
			self.disp_name = self.name
			self.name = 'pc_party'
		
		# factional view, and interactions could change faction's opinions on others.
		self.faction = faction
		# hostility values store other sides in fight and how responds to them. 
		# Set for the fight when all parties initialised.
		self.hostility = {}
		"""String to use in battle AI."""
		self.tactics = 'tank & spank'
		# dictionary of times to do things. e.g. 'defeated': 'self_destruct', or 'pc_flee': 'extra_hit'
		self.actions = {}
	
	
	# Code to be executed each time a party member hits 0hp.
	def member_killed(self, killed, killer):
		'Code that runs when a member of the party dies, adjusting HOSTILITY{} and ACTIVE properties.'
		self.actives -= 1
		if killed.party.faction in d_toolbox.factions_with_memory:
			d_toolbox.faction_relations[killed.party.faction][killer.party.faction] -= 10
		if killer.party.name in self.hostility: 
			self.hostility[killer.party.name][0] += 10
		else: self.hostility[killer.party.name] = [20, killer.party]
	
	
	def check_actives(self):
		i = 0
		for char in self.chars:
			if int(char.hp) > 0: i += 1
		self.actives = i
	
	
	# Gens an appropriate enough name to display to the player for a side in the fight.
	def get_team_name(self, party):
		team_name = ''
		if len(party) == 1: team_name = party[0].name.title()
		elif len(party) > 2: team_name = party[0].name.title() + " & friends"
		else:
			for member in party:
				team_name = team_name + member.name.title() + " & "
			team_name = team_name.strip(" & ")
		return team_name
	
		
# returns a character's SPEED stat.
def get_speed(item):
	return item.spd

# returns the party with the most aggro against the specified character's party.
def get_most_hated_party(char):
	i = 0
	most_hated = sorted(char.party.hostility.values(), key = lambda entry: entry[1])
	while most_hated[i][1].actives < 1 or most_hated[i][1] == char.party:
		i += 1
		if i >= len(char.party.hostility):
			print "loop error, Get_Most_Hated_Party"
			print char.party.hostility
			return False
	return most_hated[i][1]
	
# Returns a random character that the active char is hostile towards.
def random_opponent(active_char):
	if hasattr(active_char, 'target'):
		target = active_char.target
	else:
		most_aggro_party = get_most_hated_party(active_char)
		if most_aggro_party != False:
			target = random.choice(most_aggro_party.chars)
			while target.hp.cur_value <= 0:
				target = random.choice(most_aggro_party.chars)
		else: target = None
	return target
	

# The Fight itself.
# Takes a dictionary for the PC party, and a list of at least 1 dictionary of 1 or more NPC sides.
# The np_ps is how many lists of NPCs are in the npc_parties list.
def fight(terrain, pc_party, npc_parties):	
	
	# Creates the flight splash screen to break up combat from game and give some info on it to the player.
	def fight_splash(parties):
		to_disp = parties['pc_party'].disp_name
		for party in parties:
			if party == 'pc_party': pass 
			else: 
				to_disp += " Vs. " + parties[party].name
				# to_disp += " ! {} !".format((parties[party]).hostility['pc_party'])
		return to_disp
		
	# Returns whether there are still active NPCs in the fight.
	def party_active(party):
		party.check_actives()
		return party.actives
	
	# Checks Party[] to see if any NPCs hostile to the PCs are still active.
	def npcs_hostile(parties):
		hostile_npcs = False
		for party in parties:
			cur_party = parties[party]
			if cur_party.faction != 'pcs':
				if bool(party_active(cur_party)) == True:
					if cur_party.hostility['pc_party'][0] > 0:
						hostile_npcs = True
		return hostile_npcs			
	
	
	# Return a CHAR if their name is passed to this function.
	# Takes a CHAR or str as valid input. Returns None if None passed.
	# If most of a name is passed, still returns true. Such as "froblin" for "froblin 0".
	def check_is_combatant(to_find, alive = True):
		if to_find == None: return None
		elif hasattr(to_find, 'name'): to_find = to_find.name
		for char in combatants:
			if alive == False or char not in dead: 
				if char.name.lower() == to_find.lower() or char.name.split()[0].lower() == to_find.lower():
					return char
		else: return None
	
	# Attack another Char in the fight using ability ACTION.
	# Takes ACTION as parameter so that many offensive abilities can use this routine to be executed.
	def do_attack(char, action, target = None):
		if target != None: target = check_is_combatant(target)
		if target == None: target = random_opponent(char)
		
		print "{} attacks {}!".format(char.name, target.name)
		damage = char.abilities[action.upper()].use_ability(char, target)
		target.party.hostility[char.party.name][0] += damage
		if int(target.hp) < 1:
			target.party.member_killed(target, char)
			char.kills += 1
			dead.append(target)
			print "{} has slain {}!".format(char.name, target.name)
	
	# Look at something or someone in the combat.
	def do_look(looker, target):
		looker.ctg -= 5
		if target == None:
			print "You look good."
		else:
			target = check_is_combatant(target)
			if target != None:
				print target.looked_at(looker.senses)
			else:
				print "You don't see {} here.".format(target)
	
	# Talk to a specific CHAR, or just the masses.
	def do_talk(talker, target):
		target = check_is_combatant(target)
		talker.ctg -= 10
		if target == None:
			print "Type a name to talk to a specific character."
			name = raw_input("> ")
			target = check_is_combatant(name)
			if target != None:
				target.talked_to(talker)
			else:
				print "You don't see {} to talk to.".format(target)
		else:
			target.talked_to(talker)
	
	# Access the CHAR's inventory and use an item.
	def do_inv(active_char, item):
		do_not_loop = active_char.inv.has_item(item)
		# If no valid item specified, print the players INV.
		# Then loop to get a valid input.
		if do_not_loop == False: active_char.inv.print_inv()
		while do_not_loop == False:
			print "Use which item?"
			item = raw_input('> ').title()
			if item.lower() in ['no', 'stop', 'exit', 'quit', 'back']:
				do_not_loop = True
			elif item in ['Inv', 'Print', 'Show']:
				active_char.inv.print_inv()
			elif item == 'Help':
				print "\n Type an item name to use it. INV displays your inventory."
				print " Type BACK or NO to return to the fight. \n"
			else: do_not_loop = active_char.inv.has_item(item)
		# If item is valid, use it. Otherwise print a no item used message.
		if active_char.inv.has_item(item) != False:
			print "{} uses {}.".format(active_char.name, item)
			active_char.inv.item_use(item, active_char, active_char)
			active_char.ctg -= 15
		else: 
			print "{} decides not to use an item.".format(active_char.name)
			active_char.ctg -= 5
	
	# The FLEE code.
	# Each hostile party gets a chance to attack the fleeing character. Chance to be hit is based on a SPD off.
	def try_flee(active_char):
		flee_faction = active_char.party.faction
		for party in parties:
			attacking_party = parties[party]
			if attacking_party.faction != flee_faction and random.randint(0, 11) > attacking_party.hostility[active_char.party.name][0]:
				attacker = random.choice(attacking_party.chars)
				if int(attacker.spd) + random.randint(0, 20) > int(active_char.spd) + random.randint(0, 20):
					if hasattr(attacker, 'ctg') == False: attacker.ctg = int(attacker.spd)
					print "{} lashes out at {} as they flee.".format(str(attacker.name), str(active_char.name))
					attacker.abilities['ATTACK'].use_ability(attacker, active_char)
		print "{} escapes.".format(active_char.name)
	
	# Gets a valid Ability command from the player for the active Char.
	def get_player_input(active_char):
		# Filler line to prevent first loop breakage.
		input = 'lorem ipsum'
		# While first input word not a valid combat command.
		while input.split()[0].upper() not in active_char.abilities.keys():
			print "Moves: " + active_char.print_abilities()
			input = raw_input('> ').lower()
			if input.split() == []:
				input = 'lorem ipsum'
			# Print help text on help.
			elif input.split()[0] == 'help':
				print "\n Type any of the commands below to do it. \n You can specify a target by typing its name;\n otherwise {} will attack the most hostile enemy.\n Typing CHAR or ME shows your stats. \n You can also type QUIT to quit.\n".format(active_char.name)
			elif input in d_toolbox.exit_commands:
				print "Quitting... =("
				exit()
			elif input in d_toolbox.sheet_commands or input.split()[0] in d_toolbox.sheet_commands or (len(input.split()) > 1 and input.split()[1] in d_toolbox.sheet_commands):
				active_char.print_stats()
		# If a one word command passed, pass a None target, otherwise return the rest of the input.
		if len(input.split()) <= 1: target = None
		else: target = input.split(None, 1)[1]
		return input.split()[0], target
	
	
	# Sets up the Parties, and puts their CHARACTERS into the COMBATANTS[].
	parties = {'pc_party': Party(pc_party, faction = 'pcs')}
	combatants = [] + parties['pc_party'].chars
	
	# Initialise the npc Parties, adding them to relevant places.
	for i in range(0, len(npc_parties)):
		npcs, faction = npc_parties[i]
		parties['npcs_'+str(i)] = Party(npcs, faction)
		combatants += parties['npcs_'+str(i)].chars
	
	# Set up the starting hostility levels for the parties. PC Party hostility is set up to allow for random target acquisition code.
	for entry in parties:
		cur_party = parties[entry]
		for party in parties.values():
			if cur_party.faction == 'pcs': hostility_int = 0
			else: hostility_int = (d_toolbox.faction_relations[cur_party.faction][party.faction]) / -10
			cur_party.hostility[party.name] = [hostility_int, party]
			
	# Sort the combatants list by speed, so it can be easily iterated over.
	combatants.sort(key = get_speed, reverse = True)
	hostile_npcs = npcs_hostile(parties)
	active_pcs = bool(party_active(parties['pc_party']))
	moved = False
	dead = []
	
	"""Terrain modifying the battle! Coming soon."""
	if terrain:
		pass
		
	# The main FIGHT loop.
	# Starts with a "splash screen" to mark the start of the fight and give the player some information.
	print fight_splash(parties)
	while active_pcs == True and (hostile_npcs == True or moved == False) == True:
		for char in combatants:
			# Give Characters CTG if they not have one, which is filled by SPD each round. Once enough is stored it can be spent to use Abilities in combat.
			if hasattr(char, 'ctg') == False: char.ctg = int(char.spd)
			else: 
				char.ctg += int(char.spd)
				if char.ctg > 100: char.ctg = 100
			if int(char.hp) > 0 and char.ctg >= 50:
				print "\n"
				# Check if active Character is a PC. If so, take PC commands.
				if char in parties['pc_party'].chars:
					action, target = get_player_input(char)
					moved = True
					# Call the valid Char commands.
					# FLEE is special, as it breaks combat.
					if action == 'attack':
						do_attack(char, action, target)
					elif action == 'talk':
						do_talk(char, target)
					elif action == 'inv':
						do_inv(char, target)
					elif action == 'look':
						do_look(char, target)
					elif action == 'flee':	
						try_flee(char)
						active_pcs = party_active(parties['pc_party'])
						return active_pcs
				
				# If not a PC, do this stuff instead.
				else: do_attack(char, 'ATTACK')
		
		# End of round combat TICKs and clean up.
		# Recheck booleans and make sure everything is tickety boo.
		for char in combatants:
			if hasattr(char, 'ticks'):
				for effect in combatant.ticks:
					"""TICKs coming soon."""
					print effect
			if int(char.hp) <= 0: 
				combatants.remove(char)
				dead.append(char)
		hostile_npcs = npcs_hostile(parties)
		active_pcs = party_active(parties['pc_party'])
	
	if active_pcs: 
	 if len(dead) > 0: print "Enemies defeated, {} returns to their journey.".format(parties['pc_party'].disp_name)
	 else: print "{} returns to their journey.".format(parties['pc_party'].disp_name)
	else: print "{} has been slain.".format(parties['pc_party'].disp_name)
	print "\n"
	
	if __debug__:
		for faction in d_toolbox.faction_relations.values(): print faction
	
	# Destroy all parties, to make sure memory is saved.
	# for party in parties: del party
	
	return active_pcs