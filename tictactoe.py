# Import modules
import os
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

    def get_square(self, sq_index):
        return self.squares[sq_index]

# Defining the main game
def main():
    # Initialize everything.
    pg.init()
    screen = pg.display.set_mode((600, 600), pg.SCALED)
    pg.display.set_caption("Tic-Tac-Toe")
    
    # Creating the background
    background = pg.Surface(screen.get_size())
    background = background.convert()

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
    
    while going:
        clock.tick(60)
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
                    # First find out the players whose turn is current one.
                    if p_turn % 2 == 0:
                        current_player = SquareType.CIRCLE
                        text_content = "Player 2 Turn"
                    else:
                        current_player = SquareType.CROSS
                        text_content = "Player 1 Turn"
                    p_turn += 1
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

        # Blit the update text onto background
        background.fill(pg.Color("white"))
        background.blit(text, textpos)

        # Update the sprites
        all_sprites.update()

        # Drawing the entire scene
        screen.blit(background, (0,0))
        all_sprites.draw(screen)
        pg.display.flip()


if __name__=="__main__":
    main()
