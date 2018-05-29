
import copy

class Type_affinity:
    "Records a CHARACTER's relation to an effect type. Both existing, and min-max. Note min-max can be changed in rare situations."

    def __init__(self, initial, min, max):
        self.current = initial
        self.default = initial
        self.mod_list = {}
        self.min = min
        self.max = max

    def __str__(self):
        return "{cur}; default is {dflt} of range {min} to {max}.".format(cur = self.current, min = self.min, max = self.max, dflt = self.default)

    def add_modifier(self, effect_name, effect_value):
        self.mod_list[effect_name] = effect_value
        self.mod_current(effect_value)

    def rem_modifier(self, effect_name):
        self.mod_current(0 - self.mod_list.pop(effect_name))

    def mod_current(self, value):
        self.current = self.current + value
        if self.min < self.current < self.max == False:
            if self.current > self.max: self.current = self.max
            elif self.current < self.min: self.current = self.min


class Stat:
    "Measure the qualities of CHARACTERs. Have method to modify and recalculate themselves."

    def __init__(self, base, owner):
        self.base_value = base
        self.cur_value = base
        self.modifiers = {'wound': {'pos_neg': '-', 'value': 0}}
        self.owner = owner

    def __int__(self):
        return int(self.cur_value)

    def __str__(self):
        return "{cur} / {base}".format(cur = int(self.cur_value), base = self.base_value)

    def add_modifier(self, modifier):
        "Adds the modifier into the STAT's modifiers listing, and recalcs if replaces an active modifier."
        # Wounds work a little differently, as they just build up and can only ever be negative.
        print("modifying with " + str(modifier))
        mod_by = modifier.value
        if modifier.type == 'wound':
            # Check if the effect is healing or harming. Multiply the value as necessary.
            if modifier.pos_neg == "+":
                pos_neg = -1
            elif modifier.pos_neg == "-":
                pos_neg = 1
            else:
                pos_neg = 0
                print ("pos-neg error on {}".format(modifier.source))
            mod_by = mod_by * pos_neg
            # Add the MODIFIER value to the WOUND value. Subtract the WOUND MODIFIER, adjust the WOUND_MOD by the new effect.
            # Ensure that WOUNDS can never go under 0.
            # And then reapply the WOUND_MOD to the stat.
            print ("A mod of {cur} is being changed by {mod}.".format(cur = self.cur_value, mod = mod_by))
            self.cur_value += self.modifiers['wound']['value']
            self.modifiers['wound']['value'] += mod_by
            print ("Changed to {}".format(self.modifiers))
            if self.modifiers['wound']['value'] < 0: self.modifiers['wound']['value'] = 0
            self.cur_value -= self.modifiers['wound']['value']
            print("Therefore current value changed to {} by mod of {}!".format(self.cur_value, self.modifiers['wound']['value']))
        # Compare non-wound modifier with existing active bonus/penalty, and if larger overwrite it as active..
        else:
            if modifier.type not in self.modifiers:
                self.modifiers[modifier.type][modifier.pos_neg]['value'] = 0
            self.modifiers[modifier.type][modifier.source] = {'pos_neg': modifier.pos_neg, 'value': mod_by}
            if modifier.value > self.modifiers[modifier.type][modifier.pos_neg]['value']:
                self.recalc_mods()
        if self.cur_value <= 0:
            # Do bad stuff for dead stat.
            pass

    # Fix this - broken. "holder" does not work as should.
    def recalc_mods(self):
        "Works out which bonus and penalty should apply to the STAT, and uses this to generate current stat."
        total_mod = 0
        for mod_type in self.modifiers:
            hold_big = {'value': 0}
            hold_small = {'value': 0}
            for source in mod_type:
                if source['pos_neg'] == '-':
                    if source['value'] > hold_small['value']: hold_small = source
                elif source['pos_neg'] == '+':
                    if source['value'] > hold_big['value']: hold_big = source
                else: print('pos_neg error')
            if mod_type not in self.owner.immune_mod_types: total_mod += (hold_big - hold_small)
        self.cur_value = self.base_value + total_mod


class Character:
    "The beings in the game world, that fight and move. PC and their team are these. As are NPCs."
    summon = False
    anchor = False
    # Default default type affinity value, and range. How all non-specified elements should be treated.
    default_default_mod_level = (1, (0, 2))
    # Elemental types this Class of Character defaultly is not default towards.
    # example default mod type: ['fire', 0.5, (0, 2)]. This mod type defaults to taking half damage from fire, and has normal bounds.
    default_element_mods = [('fire', 0.5, (0, 2))]

    def __init__(self, name):
        # .status takes the condition of the Char, KO, dead, petrified, etc. Records what state is in and what can be done.
        self.status = "active"
        self.name = name

        self.element_mods = {}
        # Creates an empty dict to hold the resistances, keyed by element name.
        # For each named element on the char type, make an entry for that element.
        for mod_type in self.default_element_mods:
            # Take ELEMENTAL MODs and make a Type_Affinity for each of them.
            initial = mod_type[1]
            mod_min, mod_max = mod_type[2]
            self.element_mods[mod_type[0].lower()] = Type_affinity(initial, mod_min, mod_max)
            print(self.element_mods[mod_type[0]])

        self.hp = Stat(20, self)

    def __str__(self):
        return "{}: {} hp".format(self.name, str(self.hp))

    def receive_effect(self, effect, target_stat):
        # Takes an effect from an ability that wants to MODIFY stats and calculates effectiveness.
        # Checks for the effectiveness of the ELEMENT of the ability on SELF. Feedsback.
        if effect.element not in self.element_mods: def_value = self.default_default_mod_level[0]
        else: def_value = self.element_mods[effect.element].current
        if 0.8 <= def_value <= 1.2 == False:
            if def_value > 2.1: multiplier = 'incredibly weak to'
            elif def_value > 1.2: multiplier = 'weak to'
            elif def_value > 0: multiplier = 'resists'
            elif def_value == 0: multiplier = 'immune to'
            elif def_value < 0: multiplier = 'drains'
            else: multiplier = 'effected by'
            print('{char} is {level} {type}!'.format(char = self.name, type = effect.type, level = multiplier))
        else:
            pass
        # multiplies the modifier of the effect by SELF's susceptibility to that element.
        effect.value = effect.value * def_value
        # Checks to ensure targeted STAT exists, and then adds the effect modifier to it.
        if hasattr(self, target_stat):
            target_stat = getattr(self, target_stat)
            target_stat.add_modifier(effect)
        else:
            print("{name} has no {stat} to attack!".format(name = self.name, stat = self.target_stat))

class Human(Character):
    anchor = True
    summon = False
    species = "human"

class Summon(Character):
    summon = True
    anchor = False
    default_element_mods = []
    species = "eidolon"

class Wild(Character):
    summon = False
    anchor = False
    species = "dryad"