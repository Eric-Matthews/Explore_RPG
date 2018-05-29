
class Item():
    taken_ids = {}
    stock_min_max = (1, 3)

    def __init__(self, name, value, disp_name = None):
        self.ui = str(len(Item.taken_ids))
        Item.taken_ids[name] = self.ui

        self.dev_name = name
        self.value = value

        if disp_name:
            self.name = disp_name
        else: self.name = name


    def __str__(self):
        return "#{ui} - {name}".format(ui = self.ui, name = self.name)