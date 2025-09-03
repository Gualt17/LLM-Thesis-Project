# STRATEGIA SULLE MOSSE DISPONIBILI
import numpy as np

class PromptBuilder:
    @staticmethod
    def build(game_matrix, lives, tot_moves):
        '''
            Simboli: 
            A: Alien,
            P: Player,
            v: Alien bullet,
            ^: Player bullet,
            0: Empty space
        '''
        rows, cols = game_matrix.shape
        aliens_left = np.count_nonzero(game_matrix == 'A')

        # Stato della partita
        status = ""
        if aliens_left == 0:
            status = "VICTORY"
        elif lives == 0:
            status = "GAMEOVER"

        # Trova la colonna del giocatore
        player_pos = np.argwhere(game_matrix == 'P')
        player_col = player_pos[0][1] if player_pos.size > 0 else -1  # -1 se non trovato

        # Controllo alieni e proiettili nella colonna
        if player_col != -1:
            col_data = game_matrix[:, player_col]
            alien_in_col = 'Yes' if 'A' in col_data else 'No'
            player_bullet_in_col = 'Yes' if '^' in col_data else 'No'
            alien_bullet_in_col = 'Yes' if 'v' in col_data else 'No'
        else:
            alien_in_col = 'Unknown'
            player_bullet_in_col = 'Unknown'
            alien_bullet_in_col = 'Unknown'

        # Logica di sparo e movimento
        available_moves = []
        
        # 1. Priorità: se c'è un alieno e nessun proiettile nella colonna, spara
        if alien_in_col == 'Yes' and player_bullet_in_col == 'No':
            available_moves.append("SHOOT (highest priority - alien in your column with no player bullet)")
        
        # 2. Se non ci sono alieni nella colonna, muoviti sotto un alieno
        if alien_in_col == 'No':
            # Trova tutte le colonne con alieni
            alien_cols = [col for col in range(cols) if 'A' in game_matrix[:, col]]
            if alien_cols:
                # Calcola la distanza dalla colonna dell'alieno più vicino
                closest_col = min(alien_cols, key=lambda x: abs(x - player_col))
                direction = "RIGHT" if closest_col > player_col else "LEFT"
                available_moves.append(f"MOVE {direction} (move under nearest alien at column {closest_col})")
        
        # 3. Se c'è un proiettile nemico nella colonna, schivalo all'ultimo momento
        if alien_bullet_in_col == 'Yes':
            # Determina se ci sono colonne adiacenti disponibili
            possible_directions = []
            if player_col > 0 and game_matrix[rows-1, player_col-1] == '0':
                possible_directions.append("LEFT")
            if player_col < cols-1 and game_matrix[rows-1, player_col+1] == '0':
                possible_directions.append("RIGHT")
            
            if possible_directions:
                available_moves.append(f"EVADE BULLET by moving {' or '.join(possible_directions)} (urgent - alien bullet in your column)")
            else:
                available_moves.append("NO EVASION POSSIBLE - bullet incoming and no space to move")

        # Se non ci sono mosse prioritarie, aggiungi mosse generiche
        if not available_moves:
            possible_directions = []
            if player_col > 0:
                possible_directions.append("LEFT")
            if player_col < cols-1:
                possible_directions.append("RIGHT")
            if possible_directions:
                available_moves.append(f"SAFE MOVE: you can move {' or '.join(possible_directions)}")
            available_moves.append("STAY (hold position)")

        # Conversione della matrice in lista di liste Python (versione pulita)
        python_matrix = [[str(cell) for cell in row] for row in game_matrix]

        # Prompt formattato
        prompt = f"""
Game Matrix ({rows}x{cols}) as Python list of list:
[
{',\n'.join('    ' + str(row) for row in python_matrix)}
]

Status: {status}
Lives: {lives}
Total Moves: {tot_moves}
Aliens left: {aliens_left}

Available moves (in priority order):
1. {available_moves[0] if len(available_moves) > 0 else 'No moves available'}
{''.join(f"{i+2}. {move}\n" for i, move in enumerate(available_moves[1:]))}

Recommended action: {available_moves[0] if available_moves else 'STAY'}
"""

        # Scrittura su file
        with open('matrix_and_prompt.txt', 'w', encoding='utf-8') as file:
            file.write("========== MATRIX GAME STATE ==========\n")
            for row in game_matrix:
                file.write(' '.join(row) + '\n')

            file.write("\n========== PROMPT ==========\n")
            file.write(prompt)
            
        return prompt