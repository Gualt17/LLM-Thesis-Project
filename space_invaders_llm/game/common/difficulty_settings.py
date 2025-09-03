'''
    ATTENZIONE OGNI CELLA HA 50 PIXEL DI DIMENSIONE
    QUINDI OGNI RIGA PUO CONTENERE NEMICI = (SCREEEN_WIDTH/50) - 4 COLS (2 INIZIALI E 2 FINALI)
'''
DIFFICULTY_SETTINGS = {
    "facile": {
        "screen_width": 650,
        "screen_height": 500, #500
        "num_enemies": 9,
        "enemy_rows": 2,
        "enemy_shot_frequency": 30,
        "lives": 3
    },
    "media": {
        "screen_width": 850,
        "screen_height": 650,
        "num_enemies": 25,
        "enemy_rows": 2,
        "enemy_shot_frequency": 80,
        "lives": 3
    },
    "difficile": {
        "screen_width": 1050,
        "screen_height": 800,
        "num_enemies": 30,
        "enemy_rows": 3,
        "enemy_shot_frequency": 10,
        "lives": 3
    },
    "molto difficile": {
        "screen_width": 1250,
        "screen_height": 950,
        "num_enemies": 10,
        "enemy_rows": 4,
        "enemy_shot_frequency": 10,
        "lives": 1
    }
}