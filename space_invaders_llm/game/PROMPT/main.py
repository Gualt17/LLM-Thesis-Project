from settings_menu import Settings, SetMap
from game import Game

def main():
    while True:
        # Ottiene difficoltà e scelta mappa
        difficulty, map_choice = Settings()  
        
        if map_choice == "si":
            map_matrix = SetMap(difficulty) # inserimento manuale
            
            # Se l'utente preme Indietro, ricomincia il loop
            if map_matrix is None:
                continue
        else:
            map_matrix = None  # mappa generata automaticamente

        game = Game(difficulty, map_matrix)  # Passaggio difficoltà e mappa
        game.run()

if __name__ == "__main__":
    main()