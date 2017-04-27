import sys, random
import copy
from random import randint, randrange
from d_toolbox import check_is_move
import d_shops, d_toolbox

# Creates the gameworld, and saves the world file (TBD).

# Make a better name gen, that takes Faction into account.
def name_gen(existing_names = ['']):
	pref_bank = ["Tar", "Lon", "Dar", "Lan", "Dor", "Rad", "Rar", "Lod"]
	suf_bank = ["air", "in", "og", "aig", "an", "'gan", "at", "lan", "lir", "'ir", "nar", "dan"]
	
	name = ''
	tries = 0
	while name in existing_names and tries < 10:
		pre = pref_bank[randint (0 , len(pref_bank) -1)]
		suf = suf_bank[randint (0 , len(suf_bank) -1)]
		name = pre + suf
		tries += 1
	
	existing_names.append(name)
	return name
	
class Region(dict):
	# Creates the Region along input parameters.
	# Shapes used in mapping terrain types in regions.
	shapes = ['|', '-', '/', '\\', '||', '=', '//', '\\\\']
	
	# Base descriptions for tiles.
	# [adj] is replaced by an adjective.
	# [v#] is replaced by a verb with either -ing or -s on the ending depending on whether # is an s or ing.
	# [name] is replaced by the name of the tile.
	castle_desc = ["A [adj] castle [verb] the scenery.",
		"Many [adj] shacks sprawl against the [adj] walls of a castle."]
	city_desc = ["The noise and stink of [name] [vs] your senses. This truly is a [adj] city.",
		"This [adj] collecting of buildings of wood and [adj] stone can been seen [ving] upwards from across the area."]
	desert_desc = ["Sand and sun, as far as you can see.",
		"Only a few [adj] rocks break up the view."]
	forest_desc = ["A [adj] forest.",
		"A [adj] tree seems to be [ving]."]
	mountains_desc = ["A [adj] mountain [verbs] the sky."]
	plains_desc = ["Just [adj] fields as far as you can see.",
		"Gently rolling hills, with [adj] farms dotted here and there.",
		"Just a plain ol' plains."]
	town_desc = ["Farmland turns to [adj] buildings, [ving] closer together forming [name].",
		"A [adj] wall divides a few [adj] buildings from the wildness you've been exploring."]
	water_desc = ["A [adj] expanse of water"]
	
	descript_table = {'castle': castle_desc, 
		'city': city_desc,
		'desert': desert_desc,
		'forest': forest_desc,
		'mountains': mountains_desc,
		'plains': plains_desc,
		'town': town_desc,
		'water': water_desc,
		}
		
	char_loc_list = {}
	
	def __init__(self, x, y, towns = 1, biome = 'plains', specials = '', difficulty = 'normal', name = ''):
		# Limits to the dimensions of the region are set here.
		if x < 4: x = 4
		elif x > 20: x = 20
		if y < 4: y = 4
		elif y > 20: y = 20
		# Set the X & Y of the map, -1 as later iterators are non-inclusive.
		self.maxx = x
		self.maxy = y
		self.name = name
		self.pc_loc = ()
		
		self.lookuptable = {}
		
		tile_default = self.lookup_tile_data(biome)
		
		for d in range (0, y):
			for c in range (0, x):
				# use X Y as tuple coord key for tile data.
				coords = (d, c)
				self[coords] = {
				'type': tile_default['type'],
				'disp': tile_default['disp'],
				'faction': tile_default['faction'],
				'encounter rate': tile_default['encounter rate'],
				'explored': False,
				'actions': ["LOOK", "TALK", "REST"],
				'chars': {},
				'shops': {},
				'name': "",
				'element': "",
				'short desc': "{}".format(tile_default['type'].title()),
				'long desc': ""}
				
		self.manifest_biome(biome)
				
		for i in range(towns):
			self.make_towns()
		
		self.make_specials(specials)
		
		self.map = self.make_map()
	
	def lookup_tile_data(self, terrain_type):
	# a lookup function for the terrain types.
	# display: character shown in UI
	# faction: effects the random encounter table, and hostility
	# encounter rate: how often random encounters had here.
		tile_data = {
		'castle': {'type': 'castle', 'disp':'#', 'faction':'civilisation', 'encounter rate': 40, 'actions':[], 'short desc': "A castle"},
		'city': {'type': 'city', 'disp':'M', 'faction':'civilisation', 'encounter rate': 70, 'actions':["SHOP"], 'short desc': "A city"},
		'desert': {'type': 'desert', 'disp':'_', 'faction':'wild', 'encounter rate': 15, 'actions':[], 'short desc': "Desert"},
		'forest': {'type': 'forest', 'disp':'Y', 'faction':'wild', 'encounter rate': 20, 'actions':[], 'short desc': "Forest"},
		'mountains': {'type': 'mountains', 'disp':'^', 'faction':'wild', 'encounter rate': 20, 'actions':[], 'short desc': "Mountains"},
		'plains': {'type': 'plains', 'disp':'-', 'faction':'wild', 'encounter rate': 15, 'actions':[], 'short desc': "Plain ol' plains"},
		'town': {'type': 'town', 'disp':'m', 'faction':'civilisation', 'encounter rate': 50, 'actions':["SHOP"], 'short desc': "A town"},
		'water': {'type': 'water', 'disp':'~', 'faction':'wild', 'encounter rate': 10, 'actions':[], 'short desc': "Wet."}}
		if terrain_type.lower() in tile_data: 
			return tile_data[terrain_type.lower()]
		else: print "tile look up: erroneous type entry"
	
	def retrieve_tile_data(self, terrain_type):
	# returns the default values for the terrain type looked up.
		terrain_defaults = self.lookup_tile_data(terrain_type)
		type = terrain_defaults['type']
		disp = terrain_defaults['disp']
		faction = terrain_defaults['faction']
		e_r = terrain_defaults['encounter rate']
		actions = terrain_defaults['actions']
		short_desc = terrain_defaults['short desc']
		return (type, disp, faction, e_r, short_desc, actions)
	
	def assign_tile_data(self, coord_list, type, disp, faction, e_r, short_desc, actions = [], name = '', element = ''):
	# Writes the tile data given in params to all coordinates given in the coord_list.
	# Does not overwrite existing types or actions, but adds to them.
		for coords in coord_list:
			for item in type:
				if item not in self[coords]['type']:
					self[coords]['type'] = self[coords]['type'] + ' ' + type
			for item in actions:
				if item not in self[coords]['actions']:
					self[coords]['actions'].append(item)
			self[coords]['disp'] = disp
			self[coords]['faction'] = faction
			self[coords]['encounter rate'] = e_r
			self[coords]['element'] = element
			if self[coords]['name']: 
				name = self[coords]['name']
			else: self[coords]['name'] = name
			if name != '':
				short_desc = name + ", " + short_desc
			self[coords]['short desc'] = short_desc
			self[coords]['long desc'] = self.description_gen(coords)
	
	def description_gen(self, coords):
		# generates the long descriptions for tiles.
		
		vowels = ['a', 'e', 'i', 'o', 'u']
		adjs = ['old', 'ruined', 'impressive', 'grand', 'orante', 'lush', 'rickety', 'ramshackle', 'dilapidated', 'wispy', 'dark', 'glowing']
		verbs = ['climb', 'tower', 'fall', 'loom']
	
		"""For now, towns only count as town. When upgrading this feature, use their full typing. And generally make more involved and specific descriptions. Including use of adjacent tile data."""
		type = self[coords]['type']
		if 'town' in type: type = 'town'
		elif 'city' in type: type = 'city'
		desc = self.descript_table[type][randint(0, len(self.descript_table[type]) - 1)]
				
		# for each [COMMAND] to replace as commanded in the description template, replace it.
		# [adj] = adjective, [v#] = verb with -s or -ing as #.
		# [name] = tile.name
		desc = desc.split()
		for i, item in enumerate(desc):
			if item[0] == '[':
				if 'adj' in item: 
					desc[i] = adjs[randint(0, len(adjs) -1)]
					if desc[i][0] in vowels:
						if desc[i - 1].lower == 'a': desc[i - 1] += 'n'
				elif 'v' in item:
					if 'ing' in item: suf = 'ing'
					elif 's' in item: suf = 's'
					desc[i] = verbs[randint(0, len(verbs) -1)] + suf
					if desc[i][0] in vowels:
						if desc[i - 1].lower == 'a': desc[i - 1] += 'n'
				elif 'name' in item: desc[i] = self[coords]['name']
		return " ".join(desc)
	
	def manifest_biome(self, biome):
	# Makes the terrain match the biome, not a monoculture.
		area = self.maxx * self.maxy
		# Different biomes different mod chances.
		"""Split out, and return the values to use."""
		if biome.lower() == 'plains':
			# roll to add mountains
			roll = (randint(1, 100) - 90)
			if roll >= 0:
				mount_no = (roll / 2) + (area / randint(10, 20))
				shape = self.shapes[randint(0, 7)]
				peak_coords = self.randcoords()
				"""Needs to call better name gen."""
				self[peak_coords]['name'] = "Peak"
				self.lookuptable['mountains'] = self.shaper(peak_coords[0], peak_coords[1], shape, mount_no, 'mountains')
			# roll to add forest
			roll = (randint(1, 100) - 25)
			if roll >= 0:
				# creates an empty lookup table for forest as there can be more than one forest on a map.
				# this allows the loop for forest# to append.
				self.lookuptable['forest'] =  []
				forest_no = randint(1, 3)
				forest_size = ((area / randint(10, 15)) * ((roll / 20) + 1) / forest_no)
				for i in range(0, forest_no):
					shape = self.shapes[randint(0, 7)]
					forest_coords = self.randcoords()
					"""Needs to use better name gen"""
					self[forest_coords]['name'] = "Forest Heart"
					self.lookuptable['forest'] += (self.shaper(forest_coords[0], forest_coords[1], shape, forest_size, 'forest'))
		# Genned terrain differences looked up and modified in the Region's base data.
		for table in self.lookuptable:
			tile_data = self.lookup_tile_data(table)
			for item in self.lookuptable[table]:
				self[item]['type'] = tile_data['type']
				self[item]['disp'] = tile_data['disp']
				self[item]['faction'] = tile_data['faction']
				self[item]['encounter rate'] = tile_data['encounter rate']
				self[item]['actions'] = tile_data['actions']
				if self[item]['actions'] == []:
					self[item]['actions'] += ["LOOK", "TALK", "REST"]
				self[item]['short desc'] = tile_data['short desc']
	
	def shaper(self, base_x, base_y, shape, quantity, type):
		"""Needs to check for and make / \ shapes."""
		# Throw an error if erroneous shape passed.
		if shape not in self.shapes: 
			print "shape pass error"
			end
		if type in ['plains', 'forest']: min_density = 1
		elif type in ['mountains']: min_density = 3
		else: min_density = 2
		# more debug stuff. Prints passed values.
		if __debug__ == False:
			print type + ' with min density of ' + str(min_density)
			print "X: " + str(base_x) + " Y: " + str(base_y)
			print "#: " + str(quantity) + " in shape: " + shape
		# Adds the generated start point to start list of tiles to modify at end.
		shaped_list = [(base_x, base_y)]
		# Depending on shape, assign coordinates for generation of the terrain features. Here for shape.
		if shape in ['|', '||']: coord_a, coord_b = base_x, base_y
		# elif shape in ['-', '=']: coord_b, coord_a = base_y, base_x
		else: coord_b, coord_a = base_y, base_x
		# Sets density ratio for shaped feature.
		if shape in ['|', '-']: divisor = 5
		# elif shape in ['||', '=']: divisor = 4
		else: divisor = 4
		# How dense the feature will be. 1 = v. dense, 3 = spaced.
		density = randint(1, min_density)
		# Now start generating the desired number of modded tiles.
		for i in range(0, quantity):
			if i % divisor == 0:
				new_coords = (coord_a + randrange(-1 * density, 1* density, 2), coord_b)
			else:
				new_coords = (coord_a, coord_b + randrange(-1 * density, 1* density, 2))
			if shape in ['-', '=']: new_coords = (new_coords[1], new_coords[0])
			# if the tile has been genned before, find a new one nearby.
			while new_coords in shaped_list:
				if randint(0, 1) == 1: 
					new_coords = (new_coords[0], new_coords[1] + randrange(-1, 1, 2))
				else: 
					new_coords = (new_coords[0] + randrange(-1, 1, 2), new_coords[1])
			# Drop any out of map limits genned tiles, then add those that are left to the list to change. 
			if 0 <= new_coords[0] < self.maxx and 0 <= new_coords[1] < self.maxy: 
				shaped_list.append(new_coords)
				if __debug__ == False: print "added " + str(new_coords)
			elif __debug__ == False: print "didn't add " + str(new_coords)
		return shaped_list
	
	def make_towns(self):
	# creates towns in the Region.
		coords = self.randcoords()
		attempts = 5
		while self[coords]['type'] in ['town', 'water']:
			if attempts < 0: break
			coords = self.randcoords()
			attempts -= 1
		adjacents = self.get_value_coords(self.collect_adjacents(coords), 'town city')
		if adjacents != []:
			if __debug__ == False: print "turning " + str(adjacents) + " to cities"
			tile_data = self.retrieve_tile_data('city')
			if len(adjacents) > 1:
				name = name_gen()
			else: name = self[adjacents[0]]['name']
			self.assign_tile_data(adjacents, *tile_data, name = name)
		elif adjacents == []:
			tile_data = self.retrieve_tile_data('town')
			name = name_gen()
		if __debug__ == False: print tile_data, coords, adjacents
		self.assign_tile_data([coords], *tile_data, name = name)
		
		shop_numbers = {'town': (1, 2), 'city': (1,4), 'castle': (0, 2)}
		if 'city' in self[coords]['type']: type = 'city'
		elif 'castle' in self[coords]['type']: type = 'castle'
		elif 'town' in self[coords]['type']: type = 'town'
		
		min, max = shop_numbers[type]
		number_of_shops = random.randint(min, max)
		
		if len(self[coords]['shops']) < number_of_shops:
			for i in range(len(self[coords]['shops']), number_of_shops):
				self.gen_shop(coords)
			
			
	def gen_shop(self, coords):
		if __debug__ == False: print "added SHOP to {}".format(coords)
		shop = d_shops.Shop('test_type', 'discount')
		self[coords]['shops'][shop.name.lower()] = shop
			
	def make_specials(self, specials):
	# Put the specials from the special list into the map.
		specials_list = specials.split()
		for item in specials_list:
			if item.lower() == 'explored':
				for tile in self:
					self[tile]['explored'] = True
			
	def make_map(self):
	# Generates the map for the Region to be displayed on screen.
		map = []
		for y in range(0, self.maxy):
		# Adds map data a row at a time. Filling this list/y.
			to_add = []
			for x in range(0, self.maxx):
			# If explored show tile, otherwise a ?.
				if  self[(x, y)]['explored'] == True:
					to_add.append(self[(x, y)]['disp'])
				else: to_add.append("?")
			map.append(to_add)
		return map
				
	def print_map(self, PC_loc = None):
	# Code to print the Region's map to the screen.
		map = copy.deepcopy(self.map)
		if PC_loc is None:
			pass
		else: 
			map[PC_loc[1]][PC_loc[0]] = 'X'
		for t in map:
			print " ".join(t)
	
	def print_map_data(self, tile = None):
		if tile == None:
			for y in range(0, self.maxy):
				for x in range(0, self.maxx):
					print " {}, {}: {}".format(x, y, self[(x, y)])
		else: print self[tile]
	
	
	def explored_percent(self):
		tiles, explored_tiles = 0.0, 0.0
		for y in range(0, self.maxy):
			for x in range(0, self.maxx):
				tiles += 1.0
				if self[(x, y)]['explored'] == True:
					explored_tiles += 1.0
		return int((explored_tiles / tiles) * 100)
		
	
	def map_unfog(self, explorer_loc, vision = 1):
	# Code to explore the tiles around a point. 
	# Updating their entry and the map.
		to_unfog = self.get_value_coords(self.collect_adjacents(explorer_loc, dist = vision, look_for = 'explored'), [False])
		to_unfog.append(explorer_loc)
		for tile in to_unfog:
			self[tile]['explored'] = True
			self.map[tile[1]][tile[0]] = self[tile]['disp']
			if self[tile]['long desc'] == "":
				self[tile]['long desc'] = self.description_gen(tile)
	
	def collect_adjacents(self, coords, dist = 1, look_for = 'type'):
	# Returns surrounding tiles, and their checked property.
	# Defaults to adjacent tiles, and their terrain type.
		if __debug__ == False: print "{} looking for adj.s".format(coords)
		base_x, base_y = coords
		adjacents = {}
		for i in range(dist * -1, dist + 1):
			y = base_y + i
			if 0 <= y < self.maxy:
				for c in range(dist * -1, dist + 1):
					x = base_x + c
					if 0 <= x < self.maxx and (x, y) != coords:
						property = self[(x, y)][look_for]
						adjacents[(x, y)] = property
		return adjacents

	def has_value(self, list_to_check, to_check_for):
	# Checks to see if a property value is in a list.	
		has_type = False
		for item in list_to_check:
			if isinstance(item, bool) == False:
				if item in to_check_for:
					has_type = True
			else: 
				if item == to_check_for: has_type = True
		return has_type
		
	def get_value_coords(self, dict_to_check, list_to_check_for):
	# Returns the coords of tiles that have the looked for value of the property.
		if isinstance(list_to_check_for, basestring) == True:
			list_to_check_for = list_to_check_for.split()
		value_loc = []
		for to_check_for in list_to_check_for:
			if self.has_value(dict_to_check.values(), to_check_for) == True:
				for k, v in dict_to_check.items():
					if isinstance(v, bool) == True:
						if to_check_for == v: value_loc.append(k)
					else:
						if to_check_for in v: value_loc.append(k)
		return value_loc
		
	def randcoords(self, axis='both'):
	# Randomly generates one or both of an x, y value.
	# Has a -1 in the randint because inclusive vs. range exclusive.
		if axis.lower() not in ('x', 'y', 'both'):
			axis = 'both'
			print "randcoords: erroneous axis bug"
		if axis.lower() in ['x', 'both']:
			randx = randint(0, self.maxx - 1)
		if axis.lower() in ['y', 'both']:
			randy = randint(0, self.maxy - 1)
		if axis.lower() == 'both': return (randx, randy)
		elif axis.lower() == 'y': return (randy)
		elif axis.lower() == 'x': return (randx)
		else: print "randcoords error"
		
	def move(self, word1, word2):
		move_directions = ['n', 'e', 's', 'w', 'ne', 'se', 'sw', 'nw']
		command = None
		
		# If only one word is valid move command, make that the command.
		if check_is_move(word1) ^ check_is_move(word2) == True:
			if check_is_move(word2) == True: command = word2
			elif check_is_move(word1) == True: command = word1
		# Check what the combined command of both words is, if both are valid move actions.
		# If both words are same direction, command is that direction once.
		elif check_is_move(word1) and check_is_move(word2) == True:
			if check_is_move(word1, 'n'):
				if check_is_move(word2, 'e'): command = 'ne'
				elif check_is_move(word2, 'w'): command = 'nw'
				if check_is_move(word2, 'n'): command = 'n'
			elif check_is_move(word1, 'e'):
				if check_is_move(word2, 'n'): command = 'ne'
				elif check_is_move(word2, 's'): command = 'se'
				elif check_is_move(word2, 'e'): command = 'e'
			elif check_is_move(word1, 's'):
				if check_is_move(word2, 'e'): command = 'se'
				elif check_is_move(word2, 'w'): command = 'sw'
				elif check_is_move(word2, 's'): command = 's'
			elif check_is_move(word1, 'w'):
				if check_is_move(word2, 'n'): command = 'nw'
				elif check_is_move(word2, 's'): command = 'sw'
				elif check_is_move(word2, 'w'): command = 'w'
					
		# Now to resolve the move command
		if command:
			pc_x, pc_y = self.pc_loc
			if check_is_move(command, 'n') == True or 'n' in command:
				if pc_y > 0:
					pc_y -= 1
				else: print "Can go no further north."
			if check_is_move(command, 's') == True or 's' in command:
				if pc_y < self.maxy -1:
					pc_y += 1
				else: print "Can go no further south."
			if check_is_move(command, 'e') == True or 'e' in command:
				if pc_x < self.maxx -1:
					pc_x += 1
				else: print "Can go no further east."
			if check_is_move(command, 'w') == True or 'w' in command:
				if pc_x > 0:
					pc_x -= 1
				else: print "Can go no further west."
			self.pc_loc = pc_x, pc_y
		else:
			print "That's a bit self contradictory."
		
	# For adding a character to a location.
	def add_char(self, char_to_add, loc = None):
		# If no location given, presume PC location.
		if loc == None:
			loc = self.pc_loc
		# if the CHAR is already in a location, remove it from that location's Char list.
		if char_to_add.name.lower() in type(self).char_loc_list:
			del self[type(self).char_loc_list[char_to_add.name.lower()]]['chars'][char_to_add.name.lower]
		# Update the Char location list with new location.
		# And put the Char in that loc's Char list.
		type(self).char_loc_list[char_to_add.name.lower()] = loc
		self[loc]['chars'][char_to_add.name.lower] = char_to_add
	
	# The player attempts to visit a shop in the LOC.
	def shop(self, shopper, input):
		if input in self[self.pc_loc]['shops']:
			self[self.pc_loc]['shops'][input].in_shop(shopper)
		else:
			# If no shops in LOC, print an appropriate message instead.
			if len(self[self.pc_loc]['shops']) < 1:
				if self.has_value(self[self.pc_loc]['type'].split(), ['city', 'town', 'castle']) == True: print "For some odd reason there is no open shop in this {}.".format(self[self.pc_loc]['type'])
				else: print "You search the {} for hours, but are still surprised when you're unable to find any shops.".format(self[self.pc_loc]['type'])
			# If only one shop in location, go to it automatically.
			elif len(self[self.pc_loc]['shops']) == 1:
				random.choice(self[self.pc_loc]['shops'].values()).in_shop(shopper)
			else:
			# Otherwise print list of Shops in loc, and player picks one to visit.
				for shop in self[self.pc_loc]['shops']:
					print "{} - a shop.".format(shop.title())
				while input not in self[self.pc_loc]['shops'] and input not in d_toolbox.exit_commands:
					print "Type the name of the shop you want to visit."
					print "Type LIST to see the names again, or EXIT to go back."
					input = raw_input("> ").lower()
					if input == 'list':
						for shop in self[self.pc_loc]['shops']:
							print "{} - a shop.".format(shop.title())
				if input in self[self.pc_loc]['shops']:
					print "\n\n\n"
					print "You enter {}.".format(input.title())
					self[self.pc_loc]['shops'][input].in_shop(shopper)
	
	
	# The player tries to talk to someone in the LOC.
	def talk(self, talker, input):
		# if passed an input which is in [loc][Chars] go talk to them.
		if input in self[self.pc_loc]['chars']:
			self[self.pc_loc]['chars'][input].talked_to(talker)
		else:
		# If no Chars in loc, print an appropriate message instead.
			if len(self[self.pc_loc]['chars']) < 1:
				if self.has_value(self[self.pc_loc]['type'].split(), ['city', 'town', 'castle']) == False: print "You can't find anyone to talk to in the {}.".format(self[self.pc_loc]['type'])
				else: print "You don't find anyone interesting to talk to in this {}.".format(self[self.pc_loc]['type'])
			else:
			# Otherwise print list of chars in loc, and player picks one to talk to.
				for char in self[self.pc_loc]['chars']:
					print self[self.pc_loc]['chars'][char].name
				while input not in self[self.pc_loc]['chars'] and input not in d_toolbox.exit_commands:
					print "Type the name of who you would like to speak to."
					print "Type LIST to see the names again, or EXIT to go back."
					input = raw_input("> ").lower()
					if input == 'list':
						for char in self[self.pc_loc]['chars']:
							print self[self.pc_loc]['chars'][char].name
				if input in self[self.pc_loc]['chars']:
					self[self.pc_loc]['chars'][input].talked_to(talker)
		return