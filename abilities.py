
class Modifier():

    def __init__(self, value, pos_neg, type, source, element):
        self.value = value
        self.type = type
        self.pos_neg = pos_neg
        self.source = source
        self.element = element

    def affect_targets(self, char, stat):
        try:
            char.receive_effect(self, stat)
        except AttributeError:
            for character in char:
                character.receive_effect(self, stat)


class Buff():

    def __init__(self, duration, modifier_list):
        self.duration = duration
        self.modifiers = modifier_list