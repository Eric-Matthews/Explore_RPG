# In game help system.
# prints helpful information
def help_command(PC, location):
	location_type = location['type']
	if PC.helps == 0:
		to_print = """
You are {}. The X marks you!
Keep typing HELP for context based help.
		""".format(PC.name)
	elif PC.helps == 1:
		to_print = """
Type INV to access your inventory.
Don't forget to EQUIP a weapon.
The ? is unexplored map.
		"""
	elif PC.helps == 10 or PC.helps == 11:
		to_print = """
Some rare locations can have more to do.
		"""
	elif "castle" in location_type :
		to_print = """
You are at a large imposing fortress.
It seems to be impenetrable at this time.
Castles are marked on the map by #.
			"""
	elif "town" in location_type:
			to_print = """
This town seems fairly dead. Maybe
Edwin will come by at some point.
Towns are marked on the map by m.
			"""
	elif "mountain" in location_type:
		to_print = """
These tall, imposing mountains makes
a nice break in the uniform skyline.
Mountains are marked on the map by ^.
		"""
	elif PC.helps == 69:
		to_print = """Me and my wife are also called {}.""".format(pc.name)
	elif PC.helps == 121:
		to_print = "If you're reading this: stop cheating!"
	elif PC.helps % 2 == 0:
		to_print = """
Use N, S, E, W, to move on the grid.
or type QUIT to quit.
- is plains. Y is Forest.
		"""
	elif PC.helps % 2 != 0:
		to_print = """
Combinations such as NW or SE can also
be used to move.
The X marks your location.
		"""
	else:
		to_print = """
Hello Brian. You shouldn't really see this.
Being attacked by two enemies at once isn't fun.
Have you tried using the poison sword in a double battle?
		"""
	PC.helps += 1
	return to_print