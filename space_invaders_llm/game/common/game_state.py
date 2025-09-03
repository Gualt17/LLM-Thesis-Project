from enum import Enum

# ===== GAME STATE ===== #
class GameState(Enum):
    MENU = 0
    PLAYING = 1
    VICTORY = 2
    GAMEOVER = 3
    SETTINGS = 4
    # ... si può espandere per necessità