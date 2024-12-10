import pygame
import sys
import random

#langstons ant constants
MAX_ANTS = 4
DEFAULT_GRID_SIZE = 100
DEFAULT_STEPS = 1000
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

#pokemon game constants
DEFAULT_HP = 35
DEFAULT_DP = 15
POKEMON_TYPES = ["fire", "water", "grass"]
TYPE_ADVANTAGE = {"fire": "grass", "water": "fire", "grass": "water"}

FIRE_MOVES = {
    "burn": {"hp": -10, "dp": 0, "self_hp": 0, "self_dp": 0},
    "immolate": {"hp": -15, "dp": 0, "self_hp": -5, "self_dp": -1},
    "kindle": {"hp": 0, "dp": -5, "self_hp": 10, "self_dp": 0},
}

WATER_MOVES = {
    "bubble burst": {"hp": -10, "dp": 0, "self_hp": 0, "self_dp": 0},
    "water blast": {"hp": -15, "dp": 0, "self_hp": -5, "self_dp": 0},
    "splash": {"hp": 2, "dp": 2, "self_hp": 5, "self_dp": 0},
}

GRASS_MOVES = {
    "leaf storm": {"hp": -10, "dp": 0, "self_hp": 0, "self_dp": 0},
    "leech": {"hp": 0, "dp": -5, "self_hp": 5, "self_dp": 0},
    "seed rain": {"hp": -15, "dp": 0, "self_hp": -5, "self_dp": 0},
}

#global state
simulation_done = False
ant1_movement_rule = None  #storing ant 1's movement rules

#helper functions for the Pokemon game
def apply_damage(player, opponent, move):
    """Applies damage and effects based on the move."""
    opponent["hp"] += move["hp"]
    opponent["dp"] += move["dp"]
    player["hp"] += move["self_hp"]
    player["dp"] += move["self_dp"]

    #HP and DP have a minimum of 0 (to avoid having negative numbers)
    player["hp"] = max(0, player["hp"])
    player["dp"] = max(0, player["dp"])
    opponent["hp"] = max(0, opponent["hp"])
    opponent["dp"] = max(0, opponent["dp"])


def determine_advantage(player_type, opponent_type):
    """determines and applies the type advantage."""
    player_advantage = TYPE_ADVANTAGE[player_type] == opponent_type
    opponent_advantage = TYPE_ADVANTAGE[opponent_type] == player_type

    player_dp = DEFAULT_DP + (5 if player_advantage else 0)
    opponent_dp = DEFAULT_DP + (5 if opponent_advantage else 0)

    return player_dp, opponent_dp


def use_special_item(player, opponent, item):
    """uses the special item granted based on the movement rule for ant 1."""
    if item == "berry":
        print("You used a berry! +10 HP")
        player["hp"] += 10
    elif item == "double bomb":
        print("You used a double bomb! -10 HP opponent, +5 HP player")
        opponent["hp"] -= 10
        player["hp"] += 5
    elif item == "Mystery thingymabob":
        effect = random.choice(["hp+5", "dp+2", "hp-10", "dp+1"])
        if effect == "hp+5":
            print("Mystery thingymabob! +5 HP")
            player["hp"] += 5
        elif effect == "dp+2":
            print("Mystery thingymabob! +2 DP")
            player["dp"] += 2
        elif effect == "hp-10":
            print("Mystery thingymabob! -10 HP")
            player["hp"] -= 10
        elif effect == "dp+1":
            print("Mystery thingymabob! +1 DP")
            player["dp"] += 1


def pokemon_game():
    """the langton's ant pokemon battle game."""
    print("\nwelcome to the langton's ant battle game!")
    print("available pokemon types: fire, water, grass")

    #player's pokemon selection
    player_type = None
    while player_type not in POKEMON_TYPES:
        player_type = input("choose your pokemon type (fire, water, grass): ").strip().lower()
        if player_type not in POKEMON_TYPES:
            print("that's not a valid choice... please choose again!")

    opponent_type = random.choice(POKEMON_TYPES)
    print(f"Your opponent chose {opponent_type} type!")

    #setting the starting HP and DP with the type advantages
    player = {"hp": DEFAULT_HP, "dp": DEFAULT_DP}
    opponent = {"hp": DEFAULT_HP, "dp": DEFAULT_DP}
    player["dp"], opponent["dp"] = determine_advantage(player_type, opponent_type)

    #granting the player a special item based on their ant 1's movement rule
    special_items = {1: "berry", 2: "double bomb", 3: "mystery thingymabob"}
    item = special_items.get(ant1_movement_rule, "berry")
    print(f"you recieved a special item...: {item}")

    #player can use the special item at the start of the game before the battle starts
    use_item = input("do you want to use your special item? if you choose no, you cannot use the item later... (yes/no): ").strip().lower()
    if use_item == "yes":
        use_special_item(player, opponent, item)

    #select the move sets
    move_sets = {
        "fire": FIRE_MOVES,
        "water": WATER_MOVES,
        "grass": GRASS_MOVES,
    }
    player_moves = move_sets[player_type]
    opponent_moves = move_sets[opponent_type]

    #the limits to the amount of times you can use each move
    move_limits = {
        "immolate": 1, "water blast": 1, "seed rain": 1,
        "burn": 2, "kindle": 2, "bubble burst": 2, "leech": 2, "leaf storm": 2,
        "splash": 3,
    }

    #battle loop
    while player["hp"] > 0 and opponent["hp"] > 0:
        print(f"\nyour HP: {player['hp']} | opponent HP: {opponent['hp']}")
        print(f"your DP: {player['dp']} | opponent DP: {opponent['dp']}")

        #player's turn
        print("your moves:")
        available_moves = [
            (i + 1, move)
            for i, move in enumerate(player_moves.keys())
            if move_limits.get(move, 0) > 0
        ]
        if not available_moves:
            print("you have no more moves left! you lose!")
            return

        for idx, (i, move) in enumerate(available_moves):
            print(f"{i}: {move} (uses left: {move_limits[move]})")

        player_choice = None
        while player_choice not in [x[0] for x in available_moves]:
            try:
                player_choice = int(input("choose your move: "))
            except ValueError:
                continue

        move_name = next(move for i, move in available_moves if i == player_choice)
        move = player_moves[move_name]
        move_limits[move_name] -= 1
        print(f"You used {move_name}!")
        apply_damage(player, opponent, move)

        #check the opponent's status
        if opponent["hp"] <= 0:
            print("you won the battle! :D")
            return

        #opponent's turn
        available_opponent_moves = [
            move for move in opponent_moves.keys()
            if move_limits.get(move, 0) > 0
        ]
        if not available_opponent_moves:
            print("opponent has no moves left! you win!:D")
            return

        opponent_move_name = random.choice(available_opponent_moves)
        move = opponent_moves[opponent_move_name]
        move_limits[opponent_move_name] -= 1
        print(f"Opponent used {opponent_move_name}!")
        apply_damage(opponent, player, move)

        #check player status
        if player["hp"] <= 0:
            print("you lost the battle!")
            return

#langtons ant helper functions
def initialize_grid(grid_size):
    return [[BLACK for _ in range(grid_size)] for _ in range(grid_size)]


def draw_grid(screen, grid, cell_size):
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            pygame.draw.rect(screen, grid[x][y], pygame.Rect(y * cell_size, x * cell_size, cell_size, cell_size))


def draw_ant(screen, ant, cell_size):
    pygame.draw.rect(
        screen,
        ant["color"],
        pygame.Rect(ant["y"] * cell_size, ant["x"] * cell_size, cell_size, cell_size)
    )


def create_menu():
    global simulation_done, ant1_movement_rule

    print("welcome to langton's ant!")
    print("customize the simulation:")
    num_ants = int(input("enter the number of ants (1-4): "))
    if not (1 <= num_ants <= MAX_ANTS):
        print("not a valid number of ants... setting numbers of ants to default (1).")
        num_ants = 1

    colors = []
    for i in range(num_ants):
        hex_color = input(f"enter the hex color for ant {i+1} (example: #3BF4FB): ")
        try:
            colors.append(tuple(int(hex_color[j:j + 2], 16) for j in (1, 3, 5)))
        except ValueError:
            print(f"not a valid color for ant {i+1}, setting to the default color (white).")
            colors.append(WHITE)

    grid_size = int(input("enter the grid size in pixels (the default is 500): "))
    if grid_size <= 0:
        print("not a valid grid size (the default is 500).")
        grid_size = DEFAULT_GRID_SIZE

    steps = int(input("enter the number of steps for each ant: "))
    if steps <= 0:
        print("not a valid number of steps... setting to the default steps (1000).")
        steps = DEFAULT_STEPS

    movements = []
    print("\nselect movement rules for each ant:")
    print("1: classic mode")
    print("2: double trouble")
    print("3: customize your own")
    for i in range(num_ants):
        mode = int(input(f"choose mode for ant {i+1} (1-3): "))
        if mode == 1:
            movement = {"blank": (90, 1), "colored": (-90, 1)}
        elif mode == 2:
            movement = {"blank": (-90, 2), "colored": (90, 4)}
        elif mode == 3:
            blank_turn = int(input("at a blank square, turn (90, -90, 180, -180, 270, -270, 360, or -360): "))
            blank_steps = int(input("move forward (a positive integer): "))
            colored_turn = int(input("at a colored square, turn (90, -90, 180, -180, 270, -270, 360, or -360): "))
            colored_steps = int(input("move forward (positive integer): "))
            movement = {"blank": (blank_turn, blank_steps), "colored": (colored_turn, colored_steps)}
        else:
            print(f"not a valid mode for ant {i+1}... setting to the default (classic mode).")
            movement = {"blank": (90, 1), "colored": (-90, 1)}

        if i == 0:
            ant1_movement_rule = mode  #storing the movement rule for ant 1
        movements.append(movement)

    return num_ants, colors, grid_size, steps, movements


def main():
    global simulation_done

    num_ants, colors, grid_size, steps, movements = create_menu()

    cell_size = 10
    pixel_grid_size = grid_size // cell_size

    pygame.init()
    screen = pygame.display.set_mode((grid_size, grid_size))
    pygame.display.set_caption("Langton's Ant")
    clock = pygame.time.Clock()

    grid = initialize_grid(pixel_grid_size)

    ants = []
    for i in range(num_ants):
        ants.append({
            "x": pixel_grid_size // 2,
            "y": pixel_grid_size // 2,
            "dir": 0,
            "color": colors[i],
            "rules": movements[i]
        })

    directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # up, right, down, left

    for _ in range(steps):
        for ant in ants:
            x, y, dir = ant["x"], ant["y"], ant["dir"]
            rules = ant["rules"]

            if grid[x][y] == BLACK:
                grid[x][y] = ant["color"]
                turn, forward_steps = rules["blank"]
            else:
                grid[x][y] = BLACK
                turn, forward_steps = rules["colored"]

            turn_index = (turn // 90) % 4
            ant["dir"] = (dir + turn_index) % 4

            dx, dy = directions[ant["dir"]]
            for _ in range(forward_steps):
                ant["x"] = (ant["x"] + dx) % pixel_grid_size
                ant["y"] = (ant["y"] + dy) % pixel_grid_size

            draw_grid(screen, grid, cell_size)
            draw_ant(screen, ant, cell_size)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            clock.tick(60)

    simulation_done = True
    print("the simulation has finished... returning to the menu.")
    pokemon_game()


if __name__ == "__main__":
    main()
