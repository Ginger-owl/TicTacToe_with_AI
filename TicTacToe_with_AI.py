# base variables
import random
import time
import math

ON: bool = True

KNOWN_PARAMETERS: list = ["user", "easy", "medium", "hard"]


class Player:
    def __init__(self, letter):
        self.letter: str = letter


class HumanPlayer(Player):
    def __init__(self, letter):
        super().__init__(letter)

    def makes_a_move(self, board) -> int:
        """Checks the prompt and either asks again or returns position (int) for updating board"""
        if board.count_empty_cells() > 7:
            print(
        """Choose the position to move!
        You need to input two numbers from 1 to 3 with whitespace between
        First number for rows, second for columns
        Numeration begins from the upper-left corner (1 1)""")

        prompt = input(f"Player {board.now_moves}\nEnter the coordinates: ")
        if len(prompt) < 3 or prompt.find(" ") != 1:
            print("You should enter numbers!")
            return self.makes_a_move(board)
        else:
            r, c = prompt.split()

        if not r.isdigit() or not c.isdigit():
            print("You should enter numbers!")
            return self.makes_a_move(board)

        position = (int(r) - 1) * 3 + (int(c) - 1)

        if 0 > position or position > 8:
            print("Coordinates should be from 1 to 3!")
            return self.makes_a_move(board)

        if board.board[position] != " ":
            print("This cell is occupied! Choose another one!")
            return self.makes_a_move(board)
        else:
            return position


# AI's
class EasyBotPlayer(Player):
    def __init__(self, letter):
        super().__init__(letter)

    def random_choice(self, board) -> int:
        """Chooses randomly available cell for a move"""
        while True:
            i = random.randrange(0, 9, 1)

            if board.board[i] == " ":
                break
        return i

    def makes_a_move(self, board) -> int:
        """Returns position number(as int) as the current move"""
        print("Making move level \"easy\"")
        return self.random_choice(board)


class MediumBotPlayer(EasyBotPlayer):
    def __init__(self, letter):
        super().__init__(letter)

    def makes_a_move(self, board, n=3) -> int:
        """Search for position(int) that either wins the game or prevents losing, if nothing found picks randomly"""
        print("Making move level \"medium\"")

        # check rows
        for sign in board.now_moves, board.now_waits:
            for i in range(n):
                if board.board[3 * i] == sign and board.board[3 * i + 1] == sign and board.board[3 * i + 2] == " ":
                    return 3 * i + 2

                if board.board[3 * i] == sign and board.board[3 * i + 1] == " " and board.board[3 * i + 2] == sign:
                    return 3 * i + 1

                if board.board[3 * i] == " " and board.board[3 * i + 1] == sign and board.board[3 * i + 2] == sign:
                    return 3 * i

                # check cols
                if board.board[i] == sign and board.board[i + 3] == sign and board.board[i + 6] == " ":
                    return i + 6

                if board.board[i] == sign and board.board[i + 3] == " " and board.board[i + 6] == sign:
                    return i + 3

                if board.board[i] == " " and board.board[i + 3] == sign and board.board[i + 6] == sign:
                    return i

        # check diagonals
            if board.board[4] == sign:
                if board.board[0] == sign and board.board[8] == " ":
                    return 8

                if board.board[0] == " " and board.board[8] == sign:
                    return 0

                if board.board[6] == sign and board.board[2] == " ":
                    return 2

                if board.board[6] == " " and board.board[2] == sign:
                    return 6

            elif board.board[4] == " " and (
                    board.board[0] == sign and board.board[8] == sign
                    or board.board[6] == sign and board.board[2] == sign):
                return 4
        choice = self.random_choice(board)
        return choice


class HardBotPlayer(EasyBotPlayer):
    def __init__(self, letter):
        super().__init__(letter)

    def minimax(self, board, player):
        """Calculates the best available position on the board, based on the minimax algorithm """
        max_player = self.letter  # yourself
        other_player = "O" if player == "X" else "X"

        # first we want to check if the previous move is a winner
        if board.winner == other_player:
            if other_player == max_player:
                return {'position': None, 'score': 1 * (board.count_empty_cells() + 1)}
            else:
                return {'position': None, 'score': -1 * (board.count_empty_cells() + 1)}
        elif not board.has_empty_cells():
            return {'position': None, 'score': 0}

        if player == max_player:
            best = {'position': None, 'score': -math.inf}  # each score should maximize
        else:
            best = {'position': None, 'score': math.inf}  # each score should minimize
        for possible_move in board.available_moves():
            board.update_results(possible_move, player)

            sim_score = self.minimax(board, other_player)  # simulate a game after making that move

            # undo move
            board.update_results(possible_move, " ")
            board.winner = None

            sim_score['position'] = possible_move  # this represents the move optimal next move
            if player == max_player:  # X is max player
                if sim_score['score'] > best['score']:
                    best = sim_score
            else:
                if sim_score['score'] < best['score']:
                    best = sim_score
        return best

    def makes_a_move(self, board) -> int:
        """Returns position number(as int) as the current move"""
        if len(board.available_moves()) == 9:
            position = self.random_choice(board)
        else:
            position = self.minimax(board, self.letter)['position']
        return position


class TicTacToe:

    def __init__(self):
        self.board: list = self.initialize_grid()
        self.now_moves: str = "X"
        self.now_waits: str = "O"
        self.winner = None

    # Grid managing
    @staticmethod
    def initialize_grid() -> list:
        """ Creates an initial grid, blank by default """
        return [' ' for _ in range(9)]

    def print_grid(self) -> None:
        """Prints current board"""
        print("---------")
        print(f"| {self.board[0]} {self.board[1]} {self.board[2]} |")
        print(f"| {self.board[3]} {self.board[4]} {self.board[5]} |")
        print(f"| {self.board[6]} {self.board[7]} {self.board[8]} |")
        print("---------")

    def update_results(self, position, sign) -> None:
        """ Updates a cell of a current board with a new element """
        i = position
        self.board[i] = sign
        self.is_winner(sign)
        return

    # Analytical part
    def is_winner(self, sign=None, n=3) -> bool:
        """  Checks whether there is a winning combination on a board """
        if sign is None:
            sign = self.now_moves
        for i in range(n):
            # check rows
            if self.board[i * 3] == sign and self.board[i * 3 + 1] == sign and self.board[i * 3 + 2] == sign:
                self.winner = sign
                return True
            # check cols
            if self.board[i] == sign and self.board[i + 3] == sign and self.board[i + 6] == sign:
                self.winner = sign
                return True

        # check diagonals
        if self.board[4] == sign:
            if self.board[0] == sign and self.board[8] == sign:
                self.winner = sign
                return True

            if self.board[2] == sign and self.board[6] == sign:
                self.winner = sign
                return True
        return False

    def has_empty_cells(self) -> bool:
        """ Scans for empty sells on a board, return True if found """
        return " " in self.board

    def count_empty_cells(self) -> int:
        """ Returns number of empty cells on the current board """
        return self.board.count(" ")

    def available_moves(self) -> list:
        """ Returns list of available positions on the board to make a move """
        return [index for index, sign in enumerate(self.board) if sign == " "]

    def game_finished(self) -> bool:
        """ Checks whether the game is finished and prints result """
        if self.is_winner():
            print(f"{self.winner} wins")
            return True

        if not self.has_empty_cells():
            print("Draw")
            return True

        if self.count_empty_cells() != 9:
            self.now_moves, self.now_waits = self.now_waits, self.now_moves
        return False


# GAME MANAGEMENT
def game(board, x_player, o_player):
    """ Runs the game, until the game is finished """
    """ Takes choice from the players, updates and prints board, analyzes results of the moves """
    board.print_grid()

    while not board.game_finished():
        if board.now_moves == "X":
            choice = x_player.makes_a_move(board)
        else:
            choice = o_player.makes_a_move(board)
        board.update_results(choice, board.now_moves)
        # adds waiting time for better ux now 0 seconds
        time.sleep(0.5)
        board.print_grid()


def start_game(x_player, o_player):
    """ Initializes the game and players, based on the provided command """

    board = TicTacToe()

    name_cls_dict = {
        "X": {"user": HumanPlayer("X"),
              "easy": EasyBotPlayer("X"),
              "medium": MediumBotPlayer("X"),
              "hard": HardBotPlayer("X")},
        "O": {"user": HumanPlayer("O"),
              "easy": EasyBotPlayer("O"),
              "medium": MediumBotPlayer("O"),
              "hard": HardBotPlayer("O")},

    }

    x_player = name_cls_dict["X"][x_player]
    o_player = name_cls_dict["O"][o_player]

    game(board, x_player, o_player)

def info():
    print("To start the game type: \"start X_player O_player\"")
    print("\"X_player\" moves first and plays for 'X'")
    print("\"O_player\" moves second and plays for 'O'")
    print("You nedd to type instead of \"X_player\ and \"O_player\"")
    print("\"user\" if you want to choose moves or")
    print("\"easy\", \"medium\" or \"hard\" to pick a bot to play")
    print("Example command: \"start user easy\"")
    print("To exit game type \"exit\"\n")


def menu_loop():
    """ Takes and deciphers commands and send notifications until command exit is provided """
    info()

    
    while ON:
        command = input("Input command: ").rstrip()

        if command == "exit":
            exit_game()
            return
        elif command[:5] == "start" and command.count(" ") == 2:
            _, x_player, o_player = command.split(" ")
            if x_player in KNOWN_PARAMETERS and o_player in KNOWN_PARAMETERS:
                start_game(x_player, o_player)
                return
        print("Bad parameters!")


def exit_game():
    """ Changes ON variable to break menu_loop and exit the program """
    global ON
    ON = False


if __name__ == "__main__":
    menu_loop()
