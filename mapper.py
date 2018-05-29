import toolbox, random

class Tile():

    tile_type_key = {"plains": {"icon": "_", "encounter_rate": 20, "elems": [100, 100]},
                     "forest": {"icon": "Y", "encounter_rate": 20, "elems": [100, 100]},
                     "mountains": {"icon": "^", "encounter_rate": 20, "elems": [100, 100]},
                     "city": {"icon": "M", "encounter_rate": 20, "elems": [100, 100]},
                     "town": {"icon": "m", "encounter_rate": 20, "elems": [100, 100]},
                     "water": {"icon": "~", "encounter_rate": 20, "elems": [100, 175]}}

    def __init__(self, terrain, chars = None, shops = None, elems = None, name = None, explored = False, faction = "wild"):
        self.explored = explored
        self.terrain = terrain
        self.faction = faction
        self.name = name

        self.icon = self.tile_type_key[terrain]["icon"]

        self.people = []
        if chars:
            toolbox.add_chars_maybe_list(chars, self.people)

        self.shops = []
        if shops:
            toolbox.add_chars_maybe_list(shops, self.shops)

        self.elems = []
        if elems == None:
            elems = self.tile_type_key[terrain]['elems']
        for item in elems: self.elems.append(item)

        self.long_desc = ""
        self.desc = "A tile."
        self.encounter_lists = None

    def __str__(self):
        if self.explored == True: explord = 'explored'
        else: explord = 'unexplored'
        return explord + " {faction} {terrain}. \nShops: {shops}\nChars:{chars}".format(faction = self.faction, terrain = self.terrain, shops = self.shops, chars = self.people)



class Map(dict):

    def __init__(self, dimensions, name = None, terrain = None, towns = 10, pc_party = None):

        self.max_x, self.max_y = dimensions
        self.pc_loc = None
        self.name = name
        self.poi_lookup = {}
        self.pc_party = pc_party

        if terrain == None: terrain = "plains"

        for i in range(0, self.max_y):
            for j in range(0, self.max_x):
                coords = (j, i)
                self[coords] = Tile(terrain)

        area = self.max_x * self.max_y
        terrain_to_add = []
        for i in range(0, int(area/50) + 1):
            if toolbox.randint(0, 3) >= 2:
                length = random.randint(3, (3 + int(i / 3)))
                width = random.randint(3, (3 + int(i / 3)))
                density = 8
                shape = random.choice(['|', '|', '||', '-', '-', '='])
                forest_tiles = toolbox.shaper(shape, length, width, density)
                forest_origin = self.rand_coords()
                terrain_to_add.append(("forest", forest_origin, forest_tiles))
            if toolbox.randint(0, 5) >= 4:
                length = random.randint(2, int((4 + i) / 2))
                width = random.randint(3, (3 + int(i / 3)))
                density = 6
                shape = random.choice(['|', '|', '||', '-', '-', '='])
                mountain_tiles = toolbox.shaper(shape, length, width, density)
                mountain_origin = self.rand_coords()
                terrain_to_add.append(("mountains", mountain_origin, mountain_tiles))
            # river
            "Need thier own shaper."

        for terrain in terrain_to_add:
            t_type = terrain[0]
            origin = terrain[1]
            for tile in terrain[2]:
                try_tile = (origin[0] + tile[0], origin[1] + tile[1])
                try:
                    self[try_tile]
                except: KeyError
                else:
                    self[try_tile] = Tile(t_type)

        for i in range(0, towns):
            self.make_towns()


    def make_towns(self):
        coords = self.rand_coords()
        faction = "civilisation"
        no_shops = 1 + random.choice([0, 0, 1, 1, 2])
        shops = []
        for i in range(0, no_shops): shops.append(toolbox.gen_shop(faction))
        self[coords] = Tile("town", faction = faction, shops = shops)

    def rand_coords(self):
        return toolbox.randint(0, self.max_x), toolbox.randint(0, self.max_y)

    def place_pc(self, pc_loc):
        "Places the PC in the given location."
        self.pc_loc = pc_loc
        self.pc_explore()
        
    def check_valid_move(self, move):
        "Checks that the move command issued to the Map does not take the PC out of bounds."
        new_loc = (self.pc_loc[0] + move[0], self.pc_loc[1] + move[1])
        try:
            self[new_loc]
        except KeyError:
            print("wrong move")
            return False
        else:
            # print("move works")
            return new_loc

    def move_pc(self, new_loc):
        "Moves the PC to a new location, should have already been checked as valid."
        print("Moving PC from {} to {}.".format(self.pc_loc, new_loc))
        self.pc_loc = new_loc
        print(self[self.pc_loc])
        if self[self.pc_loc].explored == False:
            print("exploring!")
            print(self[self.pc_loc].long_desc)
        else:
            if self[self.pc_loc].desc: print(self[self.pc_loc].desc)
        self.pc_explore()

    def pc_explore(self):
        "Sets the PC_LOC and SIGHT RANGE TILEs EXPLORED = TRUE"
        self[self.pc_loc].explored = True
        if self.pc_party.senses['sight']['range'] > 1:
            adjacents = self.collect_adjacents(self.pc_loc, self.pc_party.senses['sight']['range'])
            for tile in adjacents:
                adjacents[tile].explored = True

    def collect_adjacents(self, coords, dist = 1):
        "Returns a dictionary of TILE COORDS a DISTance away."
        "Defaults to returning adjacent TILES."
        if __debug__: print ("{} looking for adjs!".format(coords))
        base_x, base_y = coords
        adjacents = {}
        for i in range(dist * -1, dist + 1):
            y = base_y + i
            if 0 <= y < self.max_y:
                for c in range(dist * -1, dist + 1):
                    x = base_x + c
                    if 0 <= x < self.max_x and (x, y) != coords:
                        adjacents[(x, y)] = self[(x, y)]
        return adjacents


    def print_map(self, disp_size, sight = False):
        "Prints the draw distance of the area around the PC into the console. Bounded by the map."
        if self.pc_loc == None: pc_x, pc_y = (0, 0)
        else: pc_x, pc_y = self.pc_loc
        centre_mod = int(disp_size / 2)

        if self.max_x - centre_mod <= pc_x: from_x = self.max_x - disp_size
        elif 0 + centre_mod >= pc_x: from_x = 0
        else: from_x = pc_x - centre_mod

        if self.max_y - centre_mod <= pc_y: from_y = self.max_y - disp_size
        elif 0 + centre_mod >= pc_y: from_y = 0
        else: from_y = pc_y - centre_mod

        if __debug__: print("PC X: {}, PC Y: {}".format(pc_x, pc_y))
        # print(self.max_x - centre_mod)
        # print(self.max_y - centre_mod)
        if __debug__: print("From X: {}, From Y: {}".format(from_x, from_y))

        to_print = []
        for i in range(from_y, from_y + disp_size):
            to_add = []
            for j in range(from_x, from_x + disp_size):
                if (j, i) == self.pc_loc:
                    to_add.append("X")
                else:
                    if self[(j, i)].explored == True or sight == True: to_add.append(self[(j, i)].icon)
                    else: to_add.append("?")
            to_print.append(' '.join(to_add))

        for line in to_print:
            print (''.join(line))


if __name__ == "__main__":
    the_world = Map((20, 20))
    the_world.print_map(20, sight = True)
