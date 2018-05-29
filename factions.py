
class Faction:
    "Stores Faction data. How they respond to other factions, specific items, etc. All Factions should be subtyped."
    # Values to be replaced by inheritance from Subclasses.
    default_type_relations = {}
    type_titles = {}
    rep_type = "error"

    # List of all in game factions, to be referenced and looked up by factions.
    factions_list = []

    def __init__(self, name, specific_type_relations = {}, memory = False, titles = type_titles, name_gen = {"prefixes": ("An", "Bo"), "suffixes": ("ne", "ob")}, items = {}):
        self.name = name
        self.vips = {}
        self.remembers = memory
        self.name_prefs = name_gen["prefixes"]
        self.name_suffs = name_gen["suffixes"]

        self.titles = titles

        # Take the dictionary of customised faction relations.
        # Then for each non-specified faction in the game assign the default relationship based on faction type.
        self.relations = specific_type_relations
        for faction in self.factions_list:
            if faction.name not in self.relations:
                their_rep_type = faction.rep_type
                def_rep = self.default_type_relations[their_rep_type]
                self.relations[faction.name] = def_rep

        self.rep_items = items

        self.factions_list.append(self)

    def add_vip(self, vip, role):
        vip_data = {"char": vip, "role": self.titles[role]}
        if vip.name not in self.vips:
            self.vips[vip.name] = vip_data

class Civilisation(Faction):
    "Factions for the city builders and industrialists. They seek to reshape the world to suit their needs."
    rep_type = "civ"
    default_type_relations = {"civ": 125, "bandit": 80, "wild": 75, "monster": 0, "pc": 110}
    type_titles = {"boss": ("king", "queen"), "second": ("lord", "lady"), "local": ("mayor"), "group": ("sir", "sel"), "bottom": ("squire"), "free": ("librarian")}

class Bandit(Faction):
    "Factions for those who use whatever they have to survive in the world. Their only goal is to make their lives as good as possible."
    rep_type = "bandit"
    default_type_relations = {"civ": 80, "bandit": 100, "wild": 75, "monster": 0, "pc": 90}
    type_titles = {"boss": ("great king", "great queen"), "second": ("king", "queen"), "local": ("lord"), "group": ("boss"), "bottom": ("footpad"), "free": ("shade")}

class Wild(Faction):
    "The factions that live in harmony with nature and the world. They seek to find their niche with the wilds of the world, or die to feed it."
    rep_type = "wild"
    default_type_relations = {"civ": 80, "bandit": 90, "wild": 110, "monster": 20, "pc": 80}
    type_titles = {"boss": ("great"), "second": ("great"), "local": ("father", "mother"), "group": ("father", "mother"), "bottom": ("childe"), "free": ("wild one")}

class Monster(Faction):
    "These factions seek little but the destruction of others. They revel in causing harm, by whichever means most appeal."
    rep_type = "monster"
    default_type_relations = {"civ": 20, "bandit": 30, "wild": 30, "monster": 90, "pc": 25}
    type_titles = {"boss": ("the deamonic"), "second": ("terrible"), "local": ("monstrous"), "group": ("beast"), "bottom": ("vile"), "free": ("the scourge")}


def faction_check(faction_name):
    for faction in Faction.factions_list:
        if faction.name == faction_name: return faction
    else: return None