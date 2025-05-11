from enum import Enum


class Player(Enum):
    PLAYER = 1
    AI = 2


class Colors:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    PINK = (255, 182, 193)
    BLUE = (173, 216, 230)
    GRAY = (200, 200, 200)
    RED = (255, 0, 0)
    BUTTON_COLOR = (100, 100, 255)
    BUTTON_HOVER = (150, 150, 255)
    PLAYER_LINE_COLOR = (0, 0, 0)
    AI_LINE_COLOR = (50, 50, 200)
    BONUS_COLOR = (255, 215, 0)


BUTTON_BACK_SIZE = (250, 70)
CONFIRM_DIALOG_SIZE = (500, 300)
