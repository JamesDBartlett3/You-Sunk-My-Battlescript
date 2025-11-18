import random
import os
import time

# ANSI color codes
COLOR_RESET = '\033[0m'
COLOR_RED = '\033[91m'  # Bright red for hits
COLOR_LIGHT_GRAY = '\033[37m'  # Light gray for ships
COLOR_DARK_BLUE = '\033[34m'  # Dark blue for water
COLOR_LIGHT_BLUE = '\033[94m'  # Light blue for misses
COLOR_GREEN = '\033[92m'  # Green for headers

class Ship:
    def __init__(self, name, size, ship_type):
        self.name = name
        self.size = size
        self.ship_type = ship_type  # Single letter: B, A, C, D, S
        self.positions = []
        self.hits = []
    
    def is_sunk(self):
        return len(self.hits) == self.size

class Board:
    def __init__(self, size=10):
        self.size = size
        self.grid = [['~' for _ in range(size)] for _ in range(size)]
        self.ships = []
        self.shots = set()
    
    def display(self, hide_ships=False):
        """Display the board. If hide_ships=True, don't show ship positions."""
        # Column headers (A-J)
        print('   ' + ' '.join([chr(ord('A') + i) for i in range(self.size)]))
        
        for i, row in enumerate(self.grid):
            # Row number (1-10)
            display_row = []
            for j, cell in enumerate(row):
                pos = (i, j)
                
                # Check if this position has been shot
                if pos in self.shots:
                    if cell == 'X':  # Hit
                        # Find the ship and display its type in red
                        ship_char = 'X'
                        for ship in self.ships:
                            if pos in ship.positions:
                                ship_char = ship.ship_type
                                break
                        display_row.append(f'{COLOR_RED}{ship_char}{COLOR_RESET}')
                    else:  # Miss (cell == 'O')
                        display_row.append(f'{COLOR_LIGHT_BLUE}O{COLOR_RESET}')
                elif hide_ships and cell == 'S':
                    # Hidden ship on opponent's board
                    display_row.append(f'{COLOR_DARK_BLUE}~{COLOR_RESET}')
                elif cell == 'S':
                    # Visible ship on own board - show in light gray
                    ship_char = 'S'
                    for ship in self.ships:
                        if pos in ship.positions:
                            ship_char = ship.ship_type
                            break
                    display_row.append(f'{COLOR_LIGHT_GRAY}{ship_char}{COLOR_RESET}')
                else:
                    # Unshot water - dark blue tilde
                    display_row.append(f'{COLOR_DARK_BLUE}~{COLOR_RESET}')
            
            print(f'{i+1:2} ' + ' '.join(display_row))
    
    def is_valid_placement(self, row, col, size, horizontal):
        """Check if ship placement is valid."""
        if horizontal:
            if col + size > self.size:
                return False
            for c in range(col, col + size):
                if self.grid[row][c] != '~':
                    return False
        else:
            if row + size > self.size:
                return False
            for r in range(row, row + size):
                if self.grid[r][col] != '~':
                    return False
        return True
    
    def place_ship(self, ship, row, col, horizontal):
        """Place a ship on the board."""
        positions = []
        if horizontal:
            for c in range(col, col + ship.size):
                self.grid[row][c] = 'S'
                positions.append((row, c))
        else:
            for r in range(row, row + ship.size):
                self.grid[r][col] = 'S'
                positions.append((r, col))
        
        ship.positions = positions
        self.ships.append(ship)
        return True
    
    def receive_shot(self, row, col):
        """Process a shot at the given coordinates."""
        if (row, col) in self.shots:
            return 'already_shot'
        
        self.shots.add((row, col))
        
        if self.grid[row][col] == 'S':
            self.grid[row][col] = 'X'  # Hit
            # Find which ship was hit
            for ship in self.ships:
                if (row, col) in ship.positions:
                    ship.hits.append((row, col))
                    if ship.is_sunk():
                        return f'sunk_{ship.name}'
                    return 'hit'
        else:
            self.grid[row][col] = 'O'  # Miss
            return 'miss'
    
    def all_ships_sunk(self):
        """Check if all ships are sunk."""
        return all(ship.is_sunk() for ship in self.ships)

class AI:
    def __init__(self, board_size=10):
        self.board_size = board_size
        self.last_hit = None
        self.target_mode = False
        self.potential_targets = []
        self.fired_shots = set()  # Track all shots fired by AI
    
    def get_shot(self, previous_result=None, last_shot=None):
        """AI logic for choosing next shot."""
        # Smart AI: If we got a hit, target adjacent cells
        if previous_result == 'hit' and last_shot:
            self.target_mode = True
            self.last_hit = last_shot
            # Add adjacent cells to potential targets
            row, col = last_shot
            adjacent = [
                (row - 1, col), (row + 1, col),
                (row, col - 1), (row, col + 1)
            ]
            for pos in adjacent:
                if (0 <= pos[0] < self.board_size and 
                    0 <= pos[1] < self.board_size and 
                    pos not in self.potential_targets and
                    pos not in self.fired_shots):
                    self.potential_targets.append(pos)
        
        # If in target mode and we have potential targets, shoot at them
        if self.target_mode and self.potential_targets:
            target = self.potential_targets.pop(0)
            # Skip if already fired at this position
            while target in self.fired_shots and self.potential_targets:
                target = self.potential_targets.pop(0)
            if target not in self.fired_shots:
                self.fired_shots.add(target)
                return target
        
        # Random shot
        self.target_mode = False
        while True:
            row = random.randint(0, self.board_size - 1)
            col = random.randint(0, self.board_size - 1)
            target = (row, col)
            if target not in self.fired_shots:
                self.fired_shots.add(target)
                return target

def clear_screen():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def setup_ships(board, is_ai=False):
    """Set up ships on the board."""
    ships_to_place = [
        Ship("Aircraft Carrier", 5, 'A'),
        Ship("Battleship", 4, 'B'),
        Ship("Cruiser", 3, 'C'),
        Ship("Destroyer", 2, 'D'),
        Ship("Submarine", 3, 'S'),
    ]
    
    if is_ai:
        # AI places ships randomly
        for ship in ships_to_place:
            placed = False
            while not placed:
                row = random.randint(0, board.size - 1)
                col = random.randint(0, board.size - 1)
                horizontal = random.choice([True, False])
                
                if board.is_valid_placement(row, col, ship.size, horizontal):
                    board.place_ship(ship, row, col, horizontal)
                    placed = True
    else:
        # Player places ships manually
        print("\n=== SHIP PLACEMENT ===\n")
        for ship in ships_to_place:
            placed = False
            while not placed:
                clear_screen()
                board.display()
                print(f"\nPlacing {ship.name} (size {ship.size})")
                
                try:
                    row_input = input("Enter starting row (1-10): ")
                    row = int(row_input) - 1  # Convert to 0-indexed
                    
                    col_input = input("Enter starting column (A-J): ").strip().upper()
                    if col_input not in 'ABCDEFGHIJ' or len(col_input) != 1:
                        print("Invalid column! Use a letter from A to J")
                        input("Press Enter to continue...")
                        continue
                    col = ord(col_input) - ord('A')  # Convert to 0-indexed
                    
                    orientation = input("Horizontal or Vertical? (h/v): ").lower()
                    
                    if orientation not in ['h', 'v']:
                        print("Invalid orientation! Use 'h' or 'v'")
                        input("Press Enter to continue...")
                        continue
                    
                    horizontal = (orientation == 'h')
                    
                    if not (0 <= row < board.size and 0 <= col < board.size):
                        print("Invalid coordinates!")
                        input("Press Enter to continue...")
                        continue
                    
                    if board.is_valid_placement(row, col, ship.size, horizontal):
                        board.place_ship(ship, row, col, horizontal)
                        placed = True
                    else:
                        print("Invalid placement! Ship doesn't fit or overlaps.")
                        input("Press Enter to continue...")
                
                except ValueError:
                    print("Invalid input! Please enter numbers.")
                    input("Press Enter to continue...")

def play_game():
    """Main game loop."""
    clear_screen()
    print("=" * 50)
    print("BATTLESHIP - Player vs AI".center(50))
    print("=" * 50)
    
    # Initialize boards
    player_board = Board()
    ai_board = Board()
    ai = AI()
    
    # Setup phase
    print("\n🚢 Welcome to Battleship! 🚢")
    print("\nYou'll place 5 ships:")
    print("  - Aircraft Carrier (5)")
    print("  - Battleship (4)")
    print("  - Cruiser (3)")
    print("  - Submarine (3)")
    print("  - Destroyer (2)")
    
    placement_choice = input("\nManual placement or Random? (m/r): ").lower()
    if placement_choice == 'r':
        print("Randomly placing your ships...")
        setup_ships(player_board, is_ai=True)
    else:
        input("\nPress Enter to start placing your ships...")
        setup_ships(player_board, is_ai=False)
    
    setup_ships(ai_board, is_ai=True)
    
    # Game loop
    game_over = False
    player_turn = True
    last_ai_shot = None
    last_ai_result = None
    last_turn_message = ""  # Store message about what happened last turn
    
    while not game_over:
        clear_screen()
        
        print("=" * 72)
        print(" " * 8 + "YOUR BOARD".center(23) + "ENEMY BOARD".center(46))
        print("=" * 72)
        
        # Prepare lines for both boards
        player_lines = []
        ai_lines = []
        
        # Create string representation of both boards with colors
        # Column headers in green
        player_lines.append('   ' + ' '.join([f"{COLOR_GREEN}{chr(ord('A') + i)}{COLOR_RESET}" for i in range(player_board.size)]))
        ai_lines.append('   ' + ' '.join([f"{COLOR_GREEN}{chr(ord('A') + i)}{COLOR_RESET}" for i in range(ai_board.size)]))
        
        for i in range(player_board.size):
            # Player board row
            player_row_cells = []
            for j, cell in enumerate(player_board.grid[i]):
                pos = (i, j)
                if pos in player_board.shots:
                    if cell == 'X':  # Hit
                        ship_char = 'X'
                        for ship in player_board.ships:
                            if pos in ship.positions:
                                ship_char = ship.ship_type
                                break
                        player_row_cells.append(f'{COLOR_RED}{ship_char}{COLOR_RESET}')
                    else:  # Miss
                        player_row_cells.append(f'{COLOR_LIGHT_BLUE}O{COLOR_RESET}')
                elif cell == 'S':
                    ship_char = 'S'
                    for ship in player_board.ships:
                        if pos in ship.positions:
                            ship_char = ship.ship_type
                            break
                    player_row_cells.append(f'{COLOR_LIGHT_GRAY}{ship_char}{COLOR_RESET}')
                else:
                    player_row_cells.append(f'{COLOR_DARK_BLUE}~{COLOR_RESET}')
            
            # Row number in green
            player_lines.append(f'{COLOR_GREEN}{i+1:2}{COLOR_RESET} ' + ' '.join(player_row_cells))
            
            # AI board row (hidden ships)
            ai_row_cells = []
            for j, cell in enumerate(ai_board.grid[i]):
                pos = (i, j)
                if pos in ai_board.shots:
                    if cell == 'X':  # Hit
                        ship_char = 'X'
                        # Only show ship type if the ship is sunk
                        for ship in ai_board.ships:
                            if pos in ship.positions:
                                if ship.is_sunk():
                                    ship_char = ship.ship_type
                                break
                        ai_row_cells.append(f'{COLOR_RED}{ship_char}{COLOR_RESET}')
                    else:  # Miss
                        ai_row_cells.append(f'{COLOR_LIGHT_BLUE}O{COLOR_RESET}')
                else:
                    ai_row_cells.append(f'{COLOR_DARK_BLUE}~{COLOR_RESET}')
            
            # Row number in green
            ai_lines.append(f'{COLOR_GREEN}{i+1:2}{COLOR_RESET} ' + ' '.join(ai_row_cells))
        
        # Print boards side by side with proper spacing
        # Need to calculate visible width (color codes don't count)
        for pl, al in zip(player_lines, ai_lines):
            # Remove ANSI codes to calculate visible width
            visible_pl = pl.replace(COLOR_RESET, '').replace(COLOR_RED, '').replace(COLOR_LIGHT_GRAY, '').replace(COLOR_DARK_BLUE, '').replace(COLOR_LIGHT_BLUE, '').replace(COLOR_GREEN, '')
            visible_width = len(visible_pl)
            # Add spacing to reach column 33 based on visible width
            spacing = ' ' * (33 - visible_width)
            print(" " * 8 + f"{pl}{spacing}{al}")
        
        print("\n" + "=" * 72)
        print(f"Legend: {COLOR_DARK_BLUE}~{COLOR_RESET} = Water, {COLOR_LIGHT_GRAY}A/B/C/D/S{COLOR_RESET} = Ship, {COLOR_RED}X{COLOR_RESET} = Hit, {COLOR_RED}A/B/C/D/S{COLOR_RESET} = Sunk, {COLOR_LIGHT_BLUE}O{COLOR_RESET} = Miss")
        print("=" * 72)
        
        # Display last turn message if there is one
        if last_turn_message:
            print(f"\n{last_turn_message}")
        
        if player_turn:
            print("\n🎯 YOUR TURN")
            try:
                shot_input = input("Enter target (e.g., A5, C10): ").strip().upper()
                
                if len(shot_input) < 2:
                    print("Invalid input! Please enter column letter (A-J) and row number (1-10).")
                    input("Press Enter to continue...")
                    continue
                
                col_letter = shot_input[0]
                row_num = shot_input[1:]
                
                if col_letter not in 'ABCDEFGHIJ':
                    print("Invalid column! Use a letter from A to J.")
                    input("Press Enter to continue...")
                    continue
                
                col = ord(col_letter) - ord('A')
                row = int(row_num) - 1
                
                if not (0 <= row < ai_board.size):
                    print("Invalid row! Use a number from 1 to 10.")
                    input("Press Enter to continue...")
                    continue
                
                # Show targeting message
                print(f"\n⏳ Running ballistic trajectory calculations for {col_letter}{row_num}... ", end='', flush=True)
                time.sleep(0.75)  # 0.75-second delay before firing
                print(f"🎯 FIRE!")
                time.sleep(2)  # 2-second delay before showing result

                result = ai_board.receive_shot(row, col)
                
                if result == 'already_shot':
                    print("❌ You already shot there!")
                    input("Press Enter to continue...")
                    continue
                
                # Create message for next turn display
                target_pos = f"{col_letter}{row_num}"
                if result == 'miss':
                    last_turn_message = f"💨 You fired at {target_pos} and missed!"
                    print("💨 MISS!")
                elif result == 'hit':
                    last_turn_message = f"💥 You fired at {target_pos} and hit!"
                    print("💥 HIT!")
                elif result.startswith('sunk_'):
                    ship_name = result.split('_')[1]
                    last_turn_message = f"💥💥 You fired at {target_pos} and sunk the enemy's {ship_name}!"
                    print(f"💥💥 HIT! You sunk the {ship_name}!")
                
                time.sleep(2)  # 2-second delay before next turn
                
                if ai_board.all_ships_sunk():
                    clear_screen()
                    print("\n" + "=" * 50)
                    print("🎉 CONGRATULATIONS! YOU WIN! 🎉".center(50))
                    print("=" * 50)
                    print("\nYou sunk all enemy ships!")
                    game_over = True
                else:
                    player_turn = False
            
            except ValueError:
                print("Invalid input! Please enter a valid coordinate (e.g., A5, C10).")
                input("Press Enter to continue...")
        
        else:
            print("\n🤖 AI'S TURN")
            
            shot = ai.get_shot(last_ai_result, last_ai_shot)
            
            # Convert to letter-number format for display
            col_letter = chr(ord('A') + shot[1])
            row_num = shot[0] + 1
            target_pos = f"{col_letter}{row_num}"
            
            print(f"\nAI is firing at {target_pos}...")
            time.sleep(2)  # 2-second delay before showing result
            
            result = player_board.receive_shot(shot[0], shot[1])
            
            # Keep shooting if already shot (shouldn't happen with good AI)
            while result == 'already_shot':
                shot = ai.get_shot(None, None)
                result = player_board.receive_shot(shot[0], shot[1])
            
            last_ai_shot = shot
            last_ai_result = result
            
            # Create message for next turn display
            if result == 'miss':
                last_turn_message = f"💨 AI fired at {target_pos} and missed!"
                print("💨 AI missed!")
            elif result == 'hit':
                last_turn_message = f"💥 AI fired at {target_pos} and hit your ship!"
                print("💥 AI hit your ship!")
            elif result.startswith('sunk_'):
                ship_name = result.split('_')[1]
                last_turn_message = f"💥💥 AI fired at {target_pos} and sunk your {ship_name}!"
                print(f"💥💥 AI sunk your {ship_name}!")
            
            time.sleep(2)  # 2-second delay before next turn
            
            if player_board.all_ships_sunk():
                clear_screen()
                print("\n" + "=" * 50)
                print("💀 GAME OVER - AI WINS 💀".center(50))
                print("=" * 50)
                print("\nThe AI sunk all your ships!")
                game_over = True
            else:
                player_turn = True
    
    # Show final boards
    print("\n=== FINAL BOARDS ===")
    print("\nYour Board:")
    player_board.display()
    print("\nEnemy Board:")
    ai_board.display(hide_ships=False)
    
    play_again = input("\nPlay again? (y/n): ").lower()
    if play_again == 'y':
        play_game()

if __name__ == "__main__":
    play_game()