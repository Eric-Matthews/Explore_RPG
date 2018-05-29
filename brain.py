from mapper import Map
from toolbox import randint
import party, character

valid_move_commands = ['n', 's', 'e', 'w','ne','nw','se', 'sw']

if __name__ == '__main__':
    pc = character.Human('Brian')
    pc_party = party.Party(pc, 'pcs')
    the_world = Map((30, 30), pc_party = pc_party)
    the_world.place_pc((randint(0, the_world.max_x), randint(0, the_world.max_y)))

    game_on = True
    disp_size = 16

    while game_on == True:
        the_world.print_map(disp_size)
        command = input("> ").lower()

        if command in ['quit', 'exit']: game_on = False
        elif command in valid_move_commands:
            move = [0, 0]
            if 'n' in command: move[1] = -1
            elif 's' in command: move[1] = 1
            if 'e' in command: move[0] = 1
            elif 'w' in command: move[0] = -1
            move = (move[0], move[1])

            move_check = the_world.check_valid_move(move)
            print(move_check)
            if move_check: the_world.move_pc(move_check)
        elif __debug__ == True and command == 'reveal':
            for tile in the_world:
                the_world[tile].explored = True
                the_world.move_pc(the_world.pc_loc)
