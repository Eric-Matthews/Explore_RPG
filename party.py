
import toolbox, character, inventory



class Party():

    def __init__(self, members, faction, max_mem = 4):
        
        if isinstance(members, character.Character): members = [members]
        self.faction = faction
        self.members = []
        self.max_size = max_mem

        for char in members:
            Party.try_add_member(self, char)
        # load some basic

        self.name = self.members[0].name
        self.species = self.members[0].species

        self.senses = {'sight': {'range': 2}}
        self.inv = inventory.Inventory(self)

    def __str__(self):
        return "A {faction} party with {cur} / {max} members.".format(faction = self.faction, cur = len(self.members), max = self.max_size)

    def print_party(self):
        print(str(self))
        for char in self.members:
            print(str(char))

    def get_no_anchors(self):
        "returns number of active ANCHORs in the party."
        # List of status able to act as ANCHOR to SUMMONs.
        able_to_anchor = ["active"]
        no_anchors = 0
        for member in self.members:
            if member.anchor == True:
                if member.status in able_to_anchor: no_anchors += 1
        return no_anchors

    def rem_char(self, to_rem):
        "Removes a CHAR from the party list. And removes buffs, summons, etc they were responsible for."
        self.members.remove(to_rem)
        print('Removed {} from the party.'.format(to_rem.name))
        self.clear_mems_buffs(to_rem)
        if to_rem.anchor == True and self.get_no_anchors() == 0: self.unsummon_all()

    def add_char(self, to_add):
        "Adds a CHAR into the party list."
        if to_add.summon == True and self.get_no_anchors() == 0:
            print('Can not summon {} to the party without an anchor.'.format(to_add.name))
        else:
            self.members.append(to_add)
            print('Added {} to the party.'.format(to_add.name))
            self.add_mems_buffs(to_add)

    def unsummon_all(self):
        "Should run whenever last ANCHOR goes down or leaves party, to unsummon SUMMON party members."
        unsummoned = []
        for member in self.members:
            if member.summon == True:
                self.members.rem_char(member)
                unsummoned.append(member.name)
        if len(unsummoned) > 0:
            to_be = "were"
            if len(unsummoned) == 1: to_be = "was"
            print('With no active anchor, {names} {prep} unsummoned!'.format(prep = to_be, names = toolbox.nicify_list(unsummoned)))
        
    def try_add_member(self, new_member):
        "Script for adding a new member to the party. If cap hit, swap out."
        # If not at member cap, just add the new CHAR.
        if len(self.members) < self.max_size:
            self.add_char(new_member)
        else:
            print("Party is full!")
            # Prompt user to decide if they want to swap someone out for new CHAR.
            replace_member = toolbox.user_choose_binary("Replace a party member for {}?".format(new_member.name))
            while replace_member == True:
                # User chooses a member to swap, or to quit.
                to_swap_out = toolbox.user_choose_one_of_many(self.members, "Party member to switch out?")
                if to_swap_out == "quit":
                    replace_member = toolbox.user_choose_binary("Swap out a party member for {}?".format(new_member.name))
                # Double check if swapping an ANCHOR. Don't allow swapping last ANCHOR for a SUMMON as this could wipe the party.
                elif to_swap_out.anchor == True and self.get_no_anchors() == 1:
                    if new_member.summon == True:
                        print("{} requires an ANCHOR to be in the party.".format(new_member.name))
                        replace_member = toolbox.user_choose_binary(
                            "Swap out a different party member for {}?".format(new_member.name))
                    else:
                        if toolbox.user_choose_binary("Remove party's only active anchor? (This will unsummon all summons)") == False:
                            replace_member = toolbox.user_choose_binary(
                                "Replace a different party member for {}?".format(new_member.name))
                        else:
                            # Do swap character stuff, and break loop.
                            self.rem_char(to_swap_out)
                            self.add_char(new_member)
                            replace_member = False
                else:
                    # Also do swap character stuff and break loop.
                    self.rem_char(to_swap_out)
                    self.add_char(new_member)
                    replace_member = False

    def clear_mems_buffs(self, remmd_member):
        "Clear all the BUFFs emenating from passed CHAR. If any were suppressing weaker versions activate them too."
        pass

    def add_mems_buffs(self, new_member):
        "Add the BUFFs from passed CHAR to the party. Suppress weaker existing BUFFs if need be."
        pass

    def char_down(self, downed_char):
        "To respond to a CHAR being put out of the fight as appropriate."
        self.clear_mems_buffs(downed_char)
        if downed_char.anchor == True:
            if self.get_no_anchors == 0: self.unsummon_all()


if __name__ == "__main__":
    # Some debug basic settings to play with on import.
    human = character.Human("Brian")
    human2 = character.Human("Laura")
    summon = character.Summon("Merkle")
    summon2 = character.Summon("Fflyp")
    wild = character.Wild("Mwar")
    dudes = [human, summon, summon]
    test_party = Party(dudes, "Testers")

    char_bank = {'human': human2, 'summon': summon2, 'wild': wild}

    import abilities
    the_attack = abilities.Modifier(25, "-", "wound", "DM", "fire")
    the_heal = abilities.Modifier(40, "+", "wound", "DM", "DM")

    test = True
    while test == True:
        command = input('> ').lower().split(None, 1)
        if len(command) == 1:
            command = command[0]
            if command in toolbox.quit_options: test = False
            elif command == 'print': test_party.print_party()
        elif len(command) == 2:
            detail = command[1]
            command = command[0]
            if command == 'add':
                detail_more = toolbox.pull_from_dict(detail, char_bank)
                if detail_more:
                    test_party.try_add_member(detail_more)
                else: print("Couldn't find {} to add.".format(detail))
            elif command == 'kill':
                detail_more = toolbox.pull_from_dict(detail, toolbox.list_to_dict(test_party.members))
                if detail_more:
                    the_attack.affect_targets(detail_more, "hp")
                else:
                    print("Couldn't find {} to kill!".format(detail))
            elif command == 'heal':
                detail_more = toolbox.pull_from_dict(detail, toolbox.list_to_dict(test_party.members))
                if detail_more:
                    the_heal.affect_targets(detail_more, "hp")
            elif command == 'rem':
                detail_more = toolbox.pull_from_dict(detail, toolbox.list_to_dict(test_party.members))
                if detail_more:
                    test_party.rem_char(detail_more)
        else:
            print('I do not know how to do that, Eric.')