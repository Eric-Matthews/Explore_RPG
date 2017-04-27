import random
# Module for combat. Takes list of PC_party and x lists of NPC_parties, and then has them fight to the death.
import d_toolbox

class Party(object):
	'A collection of CHARs. All CHARs must belong to a PARTY, even if it is a PARTY of 1 to engage in COMBAT().'
	
	char_lists = ['members', 'default_combatants', 'actives']
	
	def __init__(self, characters, faction, name = None, cmb_limit = 3):
		self.members = characters
		
		# Set the default default characters who partake of combat.
		self.default_combatants = []	
		self.combatant_limit = cmb_limit
		
		if len(self.members) < self.combatant_limit: max_range = len(self.members)
		else: max_range = self.combatant_limit
		for i in range(0, max_range):
			if self.default_combatants.append(members[i])
		
		# A holder for chars in the party unable to fight.
		self.actives = []
		for char in self.members:
			char.party = self
			if int(char.hp) < 0 : self.actives.append(char)
	
		
		# Set the party's name.
		if name == None:
			if faction == 'pcs': 
				self.name = 'pc party'
			else: self.name = self.get_team_name(characters)
		else: self.name = name
		
		# factional view, and interactions could change faction's opinions on others.
		self.faction = faction
		# Hostility values store other sides in fight and how responds to them. 
		# Set in combat, to only use relations against other groups in the combat.
		self.hostility = {}
		"""Function to determine char actions in battle AI."""
		self.tactics = 'tank & spank'
		# dictionary of times to do things. e.g. 'defeated': 'self_destruct', or 'pc_flee': 'extra_hit'
		self.specials = {}
	
	
	def get_team_name(self, party):
		'Using the .NAME of one or two MEMBERs of a PARTY, it gens an appropiate .NAME for the PARTY.'
		team_name = ''
		if len(party) == 1: team_name = party[0].name.title()
		elif len(party) > 2: team_name = party[0].name.title() + " with {} friends".format(len(party) - 1)
		else:
			for member in party:
				team_name = team_name + member.name.title() + " & "
			team_name = team_name.strip(" & ")
		return team_name
	
	
	def get_most_hated_party(self):
		'Returns the PARTY with the most aggro vs the calling PARTY. Ignoring itself, and PARTies with no combatants active.'
		i = 0
		most_hated = sorted(self.hostility.values(), key = lambda entry: entry[0])
		if __debug__: print most_hated
		while most_hated[i][1].count_actives() < 1 or most_hated[i][1] == self:
			i += 1
			if i >= len(self.hostility):
				print "loop error, Get_Most_Hated_Party"
				return False
		return most_hated[i][1]

		
	def get_starting_combatants(self):
		'Returns the CHARs who will start as combatants in a COMBAT(). Based off of .DEFAULT_COMBATANTS[], but will use RANDOM.CHOICE() to add other .ACTIVE[] CHARs if not enough in .DEFAULT_COMBATANTS[] to reach the .COMBATANT_LIMIT.'
		
		# Set up empty list to fill and return. Also ensure that PARTY is not breaking its .COMBATANT_LIMIT.
		combatants = []
		self.ensure_combatant_limit()
		if len(self.default_combatants) < self.combatant_limit: max_range = len(self.default_combatants)
		else: max_range = self.combatant_limit
		
		# Add any ACTIVE CHARs in .DEFAULT_COMBATANTS[] to the combatant list.
		for i in range(0, max_range):
			if self.default_combatants[i] in self.actives: combatants.append(self.default_combatants[i])
		
		# Fill any gaps it can with healthy CHARs.
		if len(combatants) < self.combatant_limit:
			if __debug__: print "Trying to add more CHARS."
			healthies = sorted(self.actives, key = lambda entry: entry.hp.get_percent)
			for char in healthies:
				if len(combatants) >= self.combatant_limit: break
				else:
					if char not in combatants: 
						if __debug__: print "Adding {}.".format(char.name)
						combatants.append(char)
			
		return combatants
	
	
	def set_default_combatants(self):
		setting = True
		print "Organising {}.".format(self.name)
		print "[]"
		while setting == True:
			input = raw_input('> ').lower()
			if input in d_toolbox.exit_commands: setting = False
			elif input == 'line': 
				for char in self.default_combatants:
					print "{}: {} hp".format(char.name, str(char.hp))
			
	
	
	def ensure_combatant_limit(self):
		while len(self.default_combatants) > self.combatant_limit:
			self.default_combatants.remove(random.choice(self.default_combatants))
		
	def add_member(self, new_char):
		'Function for a CHAR joining the PARTY.'
		self.members.append(new_char)
		if len(self.default_combatants) < self.combatant_limit:
			self.default_combatants.append(new_char)
		print "{} has joined {}!".format(new_char.name, self.name)
		
	def minus_member(self, leaver):
		'Function for a CHAR leaving the PARTY. Removes that CHAR from the appropiate lists.'
		for list in self.char_lists:
			if __debug__: print list
			list_to_check = getattr(self, list)
			if leaver in list_to_check: list_to_check.remove(leaver)
		print "{} has left {}!".format(new_char.name, self.name)
	
	"""def count_actives(self):
		'Returns the number of CHARs in party still able to fight.'
		n = 0
		for char in self.members:
			if char in self.incapacitated: n += 1
		return n"""