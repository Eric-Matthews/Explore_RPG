import random, character, new_shops, factions


quit_options = ["quit", "exit", "leave"]
yes_options = ["yes", "ok", "y", "true", "yeah", "yarp"]
no_options = ["no", "false", "n", "not ok", "narp", "nope"]


def get_user_choice(message):
    "Display a passed message to the user, and return their input."
    print(message)
    return input("> ").lower()


def user_choose_binary(message = "YES or NO?"):
    "Returns True or False based on user response to a message."
    choice = None
    while choice not in (yes_options + no_options): choice = get_user_choice(message)
    else:
        if choice in yes_options: choice = True
        elif choice in no_options or choice in quit_options: choice = False
        else: choice = "binary choice error"
    return choice


def user_choose_one_of_many(options, message = "Choose one of the following:"):
    "Takes a list, prints them to the screen and returns the users choice of one of them"
    chosen = False
    print(message + "\nOr type QUIT to quit.")
    # Enumerate the choices into a dictionary, keyed to the display name and number of item.
    # Player can use either to select it.
    options_dict = {}
    for x, item in enumerate(options):
        print("{}: {}".format(x, item.name))
        options_dict[(str(x), item.name.lower())] = item
    keys = options_dict.keys()

    # Get player's choice. If the input is in the key, they have chosen that item and it is returned.
    # Player can also exit without a choice.
    while chosen == False:
        choice = input("> ").lower()
        if choice in quit_options: return "quit"
        for item in keys:
            if choice in item: 
                return options_dict[item]
        # If input not a valid choice, ask again until valid choice or quit.
        else:
            print("Choice not found.")
            print(message + " Or type QUIT to quit.")
        
def nicify_list(a_list):
    "Adds an 'and' to lists if they're of length 2 or more. While returning them as a joined string."
    if len(a_list) > 1:
        a_list.insert(-1, "and")
    return " ".join(a_list)

def list_to_dict(a_list):
    a_dict = {}
    for item in a_list:
        a_dict[item.name.lower()] = item
    return a_dict

def pull_from_dict(to_find, a_dict):
    if to_find in a_dict: return a_dict[to_find]
    else: return False

def add_chars_maybe_list(maybe_list, target_list):
    if isinstance(maybe_list, character.Character):
        target_list.append(maybe_list)
    else:
        for char in maybe_list: target_list.append(char)

def randint(lower, maximum):
    # Because the heckery with RANGE and RANDOM.RANDINT being a mix of inclusive and exclusive. Excludes MAXIMUM from being returned.
    return random.randint(lower, maximum - 1)

def shaper(shape, length, width, density):
    shapes = ['|', '-', '/', '\\', '||', '=', '//', '\\\\']
    if shape not in shapes:
        raise ValueError("Shape Error! None valid shape passed!")
    if __debug__ == True:
        print ("{} by {} ".format(width, length) + shape + " with density {}.".format(density))
    # If shape has more than one line, set it to draw the other one by looping again.
    if shape in ['||', '=', '//', '\\\\']: thicc = 3
    else: thicc = 2

    shaped_list = []
    for w in range(1, thicc):
        x = w * width
        for i in range(0, length):
            for n in range(0, density):
                # Use random's randint because I need inclusive rng or else trims one side of the shape.
                # picks a number of tiles according to density as it moves along the shape's length.
                coord_a = x + random.randint(-1 * width, 1 * width)
                coord_b = i + random.randint(-1, 1)
                # Assign the coords to make the desired shape and add to coord list.
                if shape in ['|', '||', '\\', '\\\\']:
                    coord_x, coord_y = coord_a, coord_b
                if shape in ['-', '=', '/', '//']:
                    coord_x, coord_y = coord_b, coord_a
                shaped_list.append((coord_x, coord_y))
    # if __debug__: print(shaped_list)
    return shaped_list

def gen_shop(faction = None):
    if faction:
        faction = factions.faction_check(faction)
    stock_type = random.choice(['discount', 'rip_off', 'high_end', 'luxury'])
    return new_shops.Shop("test_type", stock_type, faction = faction)