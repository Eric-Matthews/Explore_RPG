# External imports
import sys
from random import randint
# Import other stuff I have written for the game.
# verb_bank and do_verbs used for dynamically calling functions from player input.
from d_verb_commands import verb_bank
do_verbs = __import__('d_verb_commands')
from d_region import Region
from d_character import Character
import d_combat
from d_items import mod_heal_potion, test_sword
import d_toolbox
import d_gen_enc_table


def game_over(pc, region):
	print "\n"
	print "GAME OVER."
	print "{} {}% explored.".format(region.name, region.explored_percent())
	print "{} kills.".format(pc.kills)
	print "\n"
	quit()
	
def game():	
	def custom_start():
	# Custom world gen, takes user input for the parameters.
		name = raw_input("What is this land called?")
		x_wide = int(raw_input("How wide is the land?"))
		y_vast = int(raw_input("And how vast is it?"))
		towns = int(raw_input("How many settlements are there?"))
		biome = (raw_input("Plains or forest?"))
		specials = raw_input("Anything else?")
		return (name, (x_wide, y_vast, towns, biome, specials))

	game_on = True
	faction_rels = d_toolbox.faction_relations
	
	# In game months, and how they affect the elemental balance.
	# 100hot/cold-100, 100dry/wet-100, 100light/shade-100
	# import the list from d_toolbox.py so only one place to update.
	month_data = d_toolbox.month_data
	# Set a random starting month and day.
	day = randint(1, 31)
	for i in range(0, randint(1, 13)):
		month = d_toolbox.set_month()
	
	# Make the PC, and put them in the region, which the user can choose to set the parameters of. Then print the region.
	print "Welcome!"
	pc = Character(stat_bonus = 10)
	game_mode = raw_input("Adventure in a random land?")
	if game_mode.lower() == "no": 
		name, settings = custom_start()
	else:
		name = "Testian"
		settings = (8, 8, 5, 'plains', 'Castle')
		pc.inv.item_add(mod_heal_potion, 1)
		pc.inv.item_add(test_sword, 1)
	pc.inv.print_inv()
	pc.helps = 0
	pc.is_pc = True
	pc_party = [pc]
	
	world = Region(*settings, name = name)
	world.pc_loc = world.randcoords()
	world.map_unfog(world.pc_loc, pc.map_view_dist)
	world.print_map(world.pc_loc)
	print world.pc_loc
	
	print "Good luck, %s. Type HELP for help." % pc.name
	
	# Main game loop.
	while game_on == True:
		# Set turn based varaibles to initial values.
		# Prepare for user input.
		new_day = False
		input, tries = ([], 0)
		while input == []:
			tries += 1
			if tries % 4 == 0:
				print "Type HELP for help."
			elif tries == 17:
				print "At least type -something-."
			input = str(raw_input('> ')).lower().split(None, 1)
		
		# Ensure that a follow on is passed to the function.
		# However it is ok for some functions to take NONE as a parameter.
		if len(input) == 1: input.append(None)
		if input[0] in ['inventory', 'items', 'item']: input[0] = 'inv'
		
		# Quit the game.
		if input[0] in ['exit', 'quit']: game_on = False
		else:
			# Check for movement command, then execute it.
			if d_toolbox.check_is_move(input[0]) == True or d_toolbox.check_is_move(input[1]) == True:
				world.move(input[0], input[1])
				new_day = True
			
			#elif input[0] == 'equip' and input[1] in pc.inv:
			#	pc.inv[input[1]].equip()
			
			# Print underlying map data.
			elif input[0] == 'print' and __debug__ == True:
				if input[1].split(None, 1)[0] == 'map':
					world.print_map_data()
				elif input[1] in ['char', 'me', 'sheet']:
					pc.print_stats()
				elif input[1].split(',', 1)[1].isdigit() == True:
					input_coords = (int(input[1].split(',', 1)[0]), int(input[1].split(',', 1)[1]))
					world.print_map_data(input_coords)
			
			# Commands due to location, which are stored in the map data are checked.
			elif input[0].upper() in world[world.pc_loc]['actions']:
				if input[0] == 'rest':
					new_day = True
					print "{} rests in the {}.".format(pc.name, world[world.pc_loc]['type'])
					# Could set this to world[].terrain_efficiency
					pc.do_rest(30)
				elif input[0] == 'look' and input[1] == None:
					input[1] = world[world.pc_loc]
					if __debug__ == True: do_verbs.look(input[0], input[1])
					print world[world.pc_loc]['long desc']
				elif input[0] == 'talk':
					if len(input) < 2:
						input = 'no'
					else: input = input[1]
					world.talk(pc, input)
				elif input[0] == 'shop':
					if len(input) < 2:
						input = 'no'
					else: input = input[1]
					world.shop(pc, input)
			
			
			# All other commands are dynamically followed.
			# They must be in VERB_BANK and a function of the same name in the d_verb_commands.py file.
			elif input[0] in verb_bank:
				if input[0] == 'help':
					input[1] = world[world.pc_loc]
				elif input[0] == 'look' and input[1] == None:
					input[1] = world[world.pc_loc]
				if __debug__: print input[0], input[1]
				to_print, new_day = getattr(do_verbs, input[0])(pc, input[1])
				print to_print
			else: print "{}? I don't think that's a good idea.".format(input)
			
			# Post command clean up and actions.
			if new_day == True:
				if randint(0, 99) < world[world.pc_loc]['encounter rate']:
					enc_type, encountered = d_gen_enc_table.get_encounter(world.pc_loc, world)
					if __debug__ == True: print enc_type, encountered
					
					if enc_type == 'combat': 
						alive = d_combat.fight(world[world.pc_loc]['type'], pc_party, encountered)
					elif enc_type == 'event': 
						print "You found a {}!".format(encountered)
						alive = "diff result"
						"""For non-combat encounters"""
					else: print "Its definitely bad."
					
					if alive == False:
						game_over(pc, world)
			
				day += 1
			world.map_unfog(world.pc_loc, pc.map_view_dist)
			world.print_map(world.pc_loc)
			
			if day >= 31:
				day = 1
				month = d_toolbox.set_month()
				print "The sign of " + month.title() + " rises to fill the night sky."
			# Print a bit about current location.
			# A brief description, and what actions the PC can do here.
			print "Day {} of {}.".format(day, month.title())
			print world[world.pc_loc]['short desc']
			print world[world.pc_loc]['actions']

if __name__ == '__main__':
	game()