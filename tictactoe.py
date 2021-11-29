# Import modules
import os
import copy
import pygame as pg
from enum import Enum
from math import floor

if not pg.font:
    print("Warning, fonts disabled")
if not pg.mixer:
    print("Warning, sounds disabled")

# Defining directories.
main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, "data")

# Loading resources
def load_image(name, colorkey=None, scale=1):
    fullname = os.path.join(data_dir, name)
    image = pg.image.load(fullname)

    size = image.get_size()
    size = (size[0] * scale, size[1] * scale)
    image = pg.transform.scale(image, size)

    image = image.convert()
    if colorkey is None:
        if colorkey == -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, pg.RLEACCEL)

    return image, image.get_rect()

class SquareType(Enum):
    EMPTY = 0
    CROSS = 1
    CIRCLE = 2

# Class for a square sprite.
# Should be able to draw sprites by specifying the type and square index.
# square_index: starts from 0
class Square(pg.sprite.Sprite):
    """
        Sprite object of a square on the board.
        Has a shape type and the position where it's to be rendered.
    """
    def __init__(self, square_no, square_type):
        pg.sprite.Sprite.__init__(self)
        if square_type == SquareType.EMPTY:
            img_name = "empty.jpeg"
        elif square_type == SquareType.CIRCLE:
            img_name = "circle.png"
        elif square_type == SquareType.CROSS:
            img_name = "cross.jpeg"

        self.image, self.rect = load_image(img_name, -1)
        x_ind = floor(square_no / 3)
        y_ind = square_no % 3
        
        top = y_ind * 100 + 150
        left = x_ind * 100 + 150
        self.rect.topleft = top, left

class Move:
    """
        Represent a move using player type and square no.
    """
    def __init__(self, square_no, player_type):
        self.square_no = square_no
        self.player_type = player_type
    
    def get_move(self):
        return self.square_no, self.player_type

# Class for board game
class Board:
    """
        Represents the state of the board as the game progresses.
    """
    def __init__(self):
        self.squares = [SquareType.EMPTY for i in range(9)]
        self.winner = None

    def set_square(self, sq_index, sq_type):
        self.squares[sq_index] = sq_type

    def is_won(self):
        """
            Checking if we reached a win state in the game.
        """
        ans = False  
        #Check the individual rows
        for i in range(3):
            if self.squares[i*3] == self.squares[i*3 + 1] == self.squares[i*3 + 2]:
                if self.squares[i*3] != SquareType.EMPTY:
                    ans = True

                    #Assign the winner
                    if self.squares[i*3] == SquareType.CIRCLE:
                        self.winner = "Circle"
                    else:
                        self.winner = "Cross"
                    break
        
        #Check the individual columns
        for i in range(3):
            if self.squares[0*3 + i] == self.squares[1*3 + i] == self.squares[2*3 + i]:
                if self.squares[0*3 + i] != SquareType.EMPTY:
                    ans = True
                    
                    #Assign the winner
                    if self.squares[0*3 + i] == SquareType.CIRCLE:
                        self.winner = "Circle"
                    else:
                        self.winner = "Cross"
                
                    break

        #Check the two diagonals
        for i in range(3):
            # Principal diagonal
            if self.squares[0] == self.squares[4] == self.squares[8]:
                if self.squares[0] != SquareType.EMPTY:
                    ans = True

                    #Assign the winner
                    if self.squares[0] == SquareType.CIRCLE:
                        self.winner = "Circle"
                    else:
                        self.winner = "Cross"
                    break

            # Secondary diagonal
            if self.squares[2] == self.squares[4] == self.squares[6]:
                if self.squares[2] != SquareType.EMPTY:
                    ans = True

                    #Assign the winner
                    if self.squares[2] == SquareType.CIRCLE:
                        self.winner = "Circle"
                    else:
                        self.winner = "Cross"
                    break

        return ans

    def is_full(self):
        """
            Checks if the board is already full or not.
        """
        ans = True
        for i in range(9):
            if self.squares[i] == SquareType.EMPTY:
                ans = False
                break
        return ans

    def empty_positions(self):
        """
            Return a list of empty positions on the board.
        """
        ans = []
        for i in range(9):
            if self.squares[i] == SquareType.EMPTY:
                ans.append(i)
        return ans

    def get_square(self, sq_index):
        return self.squares[sq_index]

    def get_board_state(self):
        """
            Return the current state of our board.
        """
        b_state = self.squares.copy()

def new_board_state(board_state, player_move):
    """
        Return a new board object based on given board state and Move object.
    """
    new_board = copy.deepcopy(board_state)
    square_no, player_type = player_move.get_move()
    new_board.set_square(square_no, player_type)
    return new_board

# Defining the main game
def main():
    # Initialize everything.
    pg.init()
    screen = pg.display.set_mode((600, 600), pg.SCALED)
    pg.display.set_caption("Tic-Tac-Toe")
    
    # Creating the background
    background = pg.Surface(screen.get_size())
    background = background.convert()
    background.fill((170, 238, 187))

    # Create the text to be rendered.
    if pg.font:
        font = pg.font.Font(None, 64)
        text_content = "Player 1 Turn"
        text = font.render(text_content, True, (10,10,10))
        textpos = text.get_rect(centerx=background.get_width() / 2, y=10)
        background.blit(text, textpos)

    screen.blit(background, (0,0))
    pg.display.flip()
    clock = pg.time.Clock()

    all_sprites = pg.sprite.RenderPlain(())

    # Create a board object
    board = Board()
    #Counter for player turn
    p_turn = 0
    # Start the infinite loop
    going = True
    recent = False

    while going:
        clock.tick(60)

        # Check if there has been a recent play by CROSS, then AI will play the CIRCLE.
        if recent:
            current_player = SquareType.CIRCLE
            text_content = "Player 1 Turn"
            best_move, score = minimax(board, current_player)
            clicked_square, type_p = best_move.get_move()

            # After the square is clicked. update the board status and add a sprite to the list
            new_sprite = Square(clicked_square, current_player)
            all_sprites.add(new_sprite)
            # After that update the board status as well.
            board.set_square(clicked_square, current_player)
            # Check if we reached a win-state
            if board.is_won() == True:
                if board.winner == "Circle":
                    text_content = "Circle won"
                else:
                    text_content = "Cross won"
            # Update the text to be rendered
            text = font.render(text_content, True, (10,10,10))

            # Reset recent to False for AI to play the next turn.
            recent = False

        # Checking the event queue
        for event in pg.event.get():
            if event.type == pg.QUIT:
                going = False
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                going = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                pos = pg.mouse.get_pos()
                y_pos = floor((pos[0] - 150) / 100)
                x_pos = floor((pos[1] - 150) / 100)
                clicked_square = ((3 * x_pos) + y_pos)
                print("Clicked ", clicked_square)
                
                # Proceed forward if only clicked on a valid square
                if clicked_square >=0 and clicked_square < 9 and board.get_square(clicked_square) == SquareType.EMPTY:
                    # Human player is presumed to be a CROSS
                    current_player = SquareType.CROSS
                    text_content = "AI Turn" #"Player 2 Turn"
                        
                    # # Use the minimax function to get a new state.
                    # current_player = SquareType.CIRCLE
                    # best_move = minimax(board, current_player)
                    # clicked_square = best_move.get_move()[0]
                    # text_content = "Player 1 Turn"

                    # After the square is clicked. update the board status and add a sprite to the list
                    new_sprite = Square(clicked_square, current_player)
                    all_sprites.add(new_sprite)
                    # After that update the board status as well.
                    board.set_square(clicked_square, current_player)
                    # Check if we reached a win-state
                    if board.is_won() == True:
                        if board.winner == "Circle":
                            text_content = "Circle won"
                        else:
                            text_content = "Cross won"
                    # Update the text to be rendered
                    text = font.render(text_content, True, (10,10,10))

                    # Set recent to True for AI to play the next turn.
                    recent = True

        
        # Blit the update text onto background
        background.fill(pg.Color("white"))
        background.blit(text, textpos)

        # Update the sprites
        all_sprites.update()

        # Drawing the entire scene
        screen.blit(background, (0,0))
        all_sprites.draw(screen)
        pg.display.flip()


def minimax(board_state, player):
    """
        Return a score of -1, 0 or +1 depending on the board state.
        Also returns a legal move for the current player
    """

    # Check if the game is over 
    if board_state.is_won():
        if player == SquareType.CROSS:
            # Previous turn was of CIRCLE, i.e. Circle won
            return None, -1
        elif player == SquareType.CIRCLE:
            # Previous turn was of CROSS, i.e. Cross won
            return None, +1
    elif board_state.is_full():
        # Board is already full and noone won
        return None, 0


    # First case: Maximizing player
    if player == SquareType.CROSS:
        MAX_VAL = -10

        # For each empty position
        blanks = board_state.empty_positions()

        final_move = None
        # Make a new move object for each blank position.
        for square in blanks:
            move = Move(square, player)
            new_board = new_board_state(board_state, move)
            new_move, temp_val = minimax(new_board, SquareType.CIRCLE)

            if MAX_VAL <= temp_val:
                MAX_VAL = temp_val
                final_move = move

        return final_move, MAX_VAL

    # Second case: Minimizing player
    elif player == SquareType.CIRCLE:
        MIN_VAL = +10

        # For each empty position
        blanks = board_state.empty_positions()

        final_move = None
        # Make a new move object for each blank poisition
        for square in blanks:
            move = Move(square, player)
            new_board = new_board_state(board_state, move)
            new_move, temp_val = minimax(new_board, SquareType.CROSS)

            if MIN_VAL >= temp_val:
                MIN_VAL = temp_val
                final_move = move

        return final_move, MIN_VAL


if __name__=="__main__":
    main()
