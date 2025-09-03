"""
Space Invaders Game

Note aggiuntive:
    - Audio non presente in modalità prompt llm
"""

import pygame
import random
import time
import numpy as np
import os

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from common.game_state import GameState
from common.difficulty_settings import DIFFICULTY_SETTINGS
from common.player import Player
from common.enemy import Enemy
from common.shoot import Shoot, EnemyShot
from common.button import Button
from common.asset_manager import AssetManager

sys.path.append(str(Path(__file__).parent.parent.parent))
#from llm.prompt import PromptBuilder
from llm.prompt_liste_di_liste import PromptBuilder
from llm.client import LLMClient

# Configurazioni di velocità
ENEMY_SPEED = 50
PLAYER_BULLET_SPEED = 50
ENEMY_BULLET_SPEED = 50
ENEMY_SHOT_FREQUENCY = 20
PLAYER_SHOT_COOLDOWN = 0.5

# Numero di frame a cui si muove il gioco
FRAMES = 5

class Game:
    def __init__(self, difficulty, map_matrix=False):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()

        # TEST PASSAGGIO VALORI DEI MENU
        self.difficulty = difficulty
        self.map_matrix = map_matrix  # Memorizza la matrice della mappa (False per generazione casuale)

        self.difficulty_settings = DIFFICULTY_SETTINGS
        self._apply_difficulty_settings()

        self.assets = AssetManager()
        self.llm_client = LLMClient()
        self.current_action = None
        self.action_delay = 0.5  # Delay in secondi tra le azioni
        self.last_action_time = 0  # Tempo dell'ultima azione eseguita

        # Configurazione schermo
        self.cell_size = 50 
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Space Invaders")

        # Inizializzazione elementi del gioco
        self.background = self.assets.load_background("images/menu_background.jpg", (self.screen_width, self.screen_height))
        
        self._init_player()
        self.bullets = []
        self.lives = 3
        self.points = 0
        self.tot_moves = 0

        self.enemies = []
        self._init_enemies()
        self.enemy_shots = []
        self.enemy_shot_cooldown = 0
        self.enemy_shot_frequency = ENEMY_SHOT_FREQUENCY
        
        self.current_state = GameState.MENU
        self.current_command = "Nessuna mossa"
        self.game_started = False
        
        self._init_menu_buttons()
        self._init_result_buttons()
        
        self.clock = pygame.time.Clock()
        self.running = True

    def _apply_difficulty_settings(self):
        settings = self.difficulty_settings.get(self.difficulty.lower())

        if not settings:
            raise ValueError(f"Difficoltà non riconosciuta: {self.difficulty}")
        
        #print(f"Difficoltà: {self.difficulty}")

        # Impostazioni di display
        self.screen_width = settings["screen_width"]
        self.screen_height = settings["screen_height"]

        # Numero di nemici
        self.num_enemies = settings["num_enemies"]

    def _init_player(self):
        """Inizializza il giocatore"""
        self.player = Player(
            x=self.screen_width // 2 - 25,
            y=self.screen_height - 50,
            width=self.cell_size, height=self.cell_size,
            screen_width=self.screen_width,
            asset_manager=self.assets,
            cell_size = self.cell_size
        )
        self.player.cell_size = self.cell_size 
        self.player.screen_width = self.screen_width
        self.player.screen_height = self.screen_height

    def _init_menu_buttons(self):
        """Inizializza i bottoni del menu"""
        button_width, button_height = 200, 50
        center_x = self.screen_width // 2 - button_width // 2
        button_y_start = self.screen_height // 2 - (button_height + 20)
        
        self.menu_buttons = [
            Button(
                center_x, button_y_start, button_width, button_height,
                "Start",
                color=(50, 120, 50),
                hover_color=(70, 150, 70),
                text_color=(255, 255, 255),
                action=self.start_action
            ),
            Button(
                center_x, button_y_start + button_height + 40, button_width, button_height,
                "Quit",
                color=(120, 50, 50),
                hover_color=(150, 70, 70),
                text_color=(255, 255, 255),
                action=self.quit_action
            )
        ]

    def _init_result_buttons(self):
        """Inizializza i bottoni per i risultati (vittoria/sconfitta)"""
        button_width, button_height = 200, 50
        center_x = self.screen_width // 2 - button_width // 2
        button_y_start = self.screen_height // 2 - (button_height + 20)
        
        # Bottoni condivisi per VICTORY e GAMEOVER
        self.victory_buttons = [
            Button(
                center_x, button_y_start, button_width, button_height,
                "Play Again",
                color=(50, 120, 50),
                hover_color=(70, 150, 70),
                text_color=(255, 255, 255),
                action=self.reset_game
            ),
            Button(
                center_x, button_y_start + button_height + 40, button_width, button_height,
                "Quit",
                color=(120, 50, 50),
                hover_color=(150, 70, 70),
                text_color=(255, 255, 255),
                action=self.quit_action
            )
        ]
        
        self.gameover_buttons = [
            Button(
                center_x, button_y_start, button_width, button_height,
                "Retry",
                color=(50, 120, 50),
                hover_color=(70, 150, 70),
                text_color=(255, 255, 255),
                action=self.reset_game
            ),
            Button(
                center_x, button_y_start + button_height + 40, button_width, button_height,
                "Quit",
                color=(120, 50, 50),
                hover_color=(150, 70, 70),
                text_color=(255, 255, 255),
                action=self.quit_action
            )
        ]

    def _init_enemies(self):
        """Inizializza i nemici: usa la mappa manuale se disponibile, altrimenti genera casualmente"""
        self.enemies = []
        
        # Se è stata fornita una mappa manuale, usala
        if self.map_matrix is not None and isinstance(self.map_matrix, list):
            #print("Usando mappa manuale...")
            for row_idx, row in enumerate(self.map_matrix):
                for col_idx, cell in enumerate(row):
                    if cell == 1:  # 1 rappresenta un nemico nella mappa manuale
                        x = col_idx * self.cell_size
                        y = row_idx * self.cell_size
                        enemy = Enemy(x, y, self.assets)
                        self.enemies.append(enemy)
        else:
            # Altrimenti genera nemici casualmente
            #print("Generando nemici casualmente...")
            min_col = 2
            max_col = (self.screen_width // self.cell_size) - 3
            max_row = 2
            
            occupied_positions = set()
            
            while len(self.enemies) < self.num_enemies:
                row = random.randint(0, max_row)
                col = random.randint(min_col, max_col)
                pos = (col, row)
                
                if pos not in occupied_positions:
                    x = col * self.cell_size
                    y = row * self.cell_size
                    enemy = Enemy(x, y, self.assets)
                    self.enemies.append(enemy)
                    occupied_positions.add(pos)
        
        # Ordina i nemici per coordinata x
        self.enemies = sorted(self.enemies, key=lambda e: e.rect.x)

    def start_action(self):
        """Azione per il bottone Start - Inizia una nuova partita"""
        # Pulisce il file delle matrici
        open("matrix_and_prompt.txt", 'w').close()
        
         # Resetta tutte le variabili di gioco
        self.enemies.clear()
        self.bullets.clear()
        self.enemy_shots.clear()
        self.current_action = None  # Resetta l'azione corrente
        self.last_action_time = 0  # Resetta il timer delle azioni
        self.enemy_shot_cooldown = 0
        self.lives = 3  # Ripristina le vite
        self.points = 0
        self.tot_moves = 0
        
        # Reinizializza gli elementi del gioco
        self._init_enemies()
        self._init_player()
        self.player.reset()
        
        # Imposta lo stato di gioco
        self.current_state = GameState.PLAYING
        self.current_command = "Nessuna mossa"
        self.game_started = False
        
        print("Nuova partita iniziata!")

    def quit_action(self):
        """Azione per il bottone Quit"""
        self.running = False

    def reset_game(self):
        """Resetta completamente il gioco allo stato iniziale"""
        # Pulisce il file delle matrici
        open("matrix_and_prompt.txt", 'w').close()
        
        # Resetta tutte le variabili di gioco
        self.enemies.clear()
        self.bullets.clear()
        self.enemy_shots.clear()
        self.current_action = None  # Resetta l'azione corrente
        self.last_action_time = 0  # Resetta il timer delle azioni
        self.enemy_shot_cooldown = 0
        self.lives = 3  # Ripristina le vite
        self.points = 0
        self.tot_moves = 0
        
        # Reinizializza gli elementi del gioco
        self._init_enemies()
        self._init_player()
        self.player.reset()
        
        # Resetta lo stato del gioco
        self.current_state = GameState.PLAYING
        self.current_command = "Nessuna mossa"
        self.game_started = False
        
        print("Gioco completamente resettato!")

    def _advance_game_frame(self):
        """Avanza il gioco di un frame"""

        if self.tot_moves % 5 == 0:
            if not self.enemies:
                return
            
            for enemy in self.enemies:
                enemy.update()
            
        if self.enemies and self.enemy_shot_cooldown <= 0:
            shooter = random.choice(self.enemies)
            self.enemy_shots.append(EnemyShot(
                shooter.rect.centerx - 2,
                shooter.rect.bottom
            ))
            self.enemy_shot_cooldown = self.enemy_shot_frequency
        else:
            self.enemy_shot_cooldown -= 1
        
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.active:
                self.bullets.remove(bullet)
        
        for shot in self.enemy_shots[:]:
            shot.update()
            if not shot.active:
                self.enemy_shots.remove(shot)
        
        self._check_collisions()
        self._check_game_conditions()

    def _execute_action(self, action):
        """Esegue una singola azione"""
        if action == "LEFT":
            self.player.move_left()
        elif action == "RIGHT":
            self.player.move_right()
        elif action == "SHOOT":
            bullet = self.player.shoot()
            self.bullets.append(bullet)
        elif action == "STAY":
            pass
        else:
            print(f"Azione sconosciuta: {action}")
        
        self.current_command = action  # Aggiorna il comando corrente per il rendering
        
        print(f"Eseguita azione: {action}")
        print(f"Numero di azioni eseguite: {self.tot_moves}")
        print(f"Numero di vite rimanenti: {self.lives}")
        print(f"Punteggio attuale: {self.points}")
        print("\n\n")

    def _check_collisions(self):
        # Nuove liste filtrate
        nuovi_proiettili = []
        nuovi_nemici   = []

        # Scorri tutti i nemici e tienili in una lista finché non vengono colpiti
        for enemy in self.enemies:
            enemy_hit = False
            for bullet in self.bullets:
                if bullet.rect.colliderect(enemy.rect):
                    self.points += 100
                    enemy_hit = True
                    break
            if not enemy_hit:
                nuovi_nemici.append(enemy)

        # Scorri i proiettili e tienili finché non hanno colpito un nemico
        for bullet in self.bullets:
            hit_any = any(bullet.rect.colliderect(e.rect) for e in self.enemies)
            if not hit_any:
                nuovi_proiettili.append(bullet)

        # Aggiorna le liste
        self.enemies = nuovi_nemici
        self.bullets = nuovi_proiettili

        # Poi gestisci le collisioni tra colpi nemici e giocatore…
        for shot in self.enemy_shots[:]:
            if shot.rect.colliderect(self.player.rect):
                self.enemy_shots.remove(shot)
                self.lives -= 1
                if self.lives <= 0:
                    self.current_state = GameState.GAMEOVER
                break


    def _check_game_conditions(self):
        """Controlla le condizioni di vittoria/sconfitta"""
        if not self.enemies:
            self.current_state = GameState.VICTORY
            return
        
        player_line = self.player.rect.y
        for enemy in self.enemies:
            if enemy.rect.bottom >= player_line:
                self.current_state = GameState.GAMEOVER
                return

    def handle_events(self):
        """Gestisce tutti gli eventi del gioco"""
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.current_state == GameState.MENU:
                for button in self.menu_buttons:
                    if button.handle_event(event, mouse_pos):
                        continue
            
            elif self.current_state == GameState.VICTORY:
                for button in self.victory_buttons:
                    if button.handle_event(event, mouse_pos):
                        break
            
            elif self.current_state == GameState.GAMEOVER:
                for button in self.gameover_buttons:
                    if button.handle_event(event, mouse_pos):
                        break

    def render(self):
        mouse_pos = pygame.mouse.get_pos()

        # --- Sfondo --- #
        self.screen.blit(self.background, (0, 0))
        
        # --- Controlla hover bottoni --- #
        if self.current_state == GameState.MENU:
            for button in self.menu_buttons:
                button.check_hover(mouse_pos)
                button.draw(self.screen)
                
        elif self.current_state == GameState.PLAYING:
            # --- Griglia di debug --- #
            for x in range(0, self.screen_width, self.cell_size): # Linee verticali
                pygame.draw.line(self.screen, (50, 50, 50), (x, 0), (x, self.screen_height), 1)
            for y in range(0, self.screen_height, self.cell_size): # Linee orizzontali
                pygame.draw.line(self.screen, (50, 50, 50), (0, y), (self.screen_width, y), 1)

            font = pygame.font.SysFont(None, 32)

            # --- Testi --- #
            points_text = font.render(f"Punti: {self.points}", True, (255, 255, 255))
            lives_text = font.render(f"Vite: {self.lives}", True, (255, 255, 255))
            moves_text = font.render(f"Mosse: {self.tot_moves}", True, (255, 255, 255))

            # --- Calcola dimensioni unificate --- #
            max_width = max(points_text.get_width(), lives_text.get_width(), moves_text.get_width())
            box_width = max_width + 20
            box_height = points_text.get_height() + 10

            # --- Posizioni --- #
            box_x = self.screen_width - box_width - 10
            moves_box_y = self.screen_height - box_height - 10
            lives_box_y = moves_box_y - box_height - 10
            points_box_y = lives_box_y - box_height - 10

            # --- Riquadro Punti --- #
            pygame.draw.rect(self.screen, (0, 0, 0), (box_x, points_box_y, box_width, box_height), border_radius=8)
            pygame.draw.rect(self.screen, (255, 255, 255), (box_x, points_box_y, box_width, box_height), 2, border_radius=8)
            self.screen.blit(points_text, (box_x + 10, points_box_y + 5))

            # --- Riquadro Vite --- #
            pygame.draw.rect(self.screen, (0, 0, 0), (box_x, lives_box_y, box_width, box_height), border_radius=8)
            pygame.draw.rect(self.screen, (255, 255, 255), (box_x, lives_box_y, box_width, box_height), 2, border_radius=8)
            self.screen.blit(lives_text, (box_x + 10, lives_box_y + 5))

            # --- Riquadro Mosse --- #
            pygame.draw.rect(self.screen, (0, 0, 0), (box_x, moves_box_y, box_width, box_height), border_radius=8)
            pygame.draw.rect(self.screen, (255, 255, 255), (box_x, moves_box_y, box_width, box_height), 2, border_radius=8)
            self.screen.blit(moves_text, (box_x + 10, moves_box_y + 5))

            # --- Giocatore, Nemmici e Proiettili --- #
            self.player.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw(self.screen)
            for bullet in self.bullets:
                bullet.draw(self.screen)
            for shot in self.enemy_shots:
                shot.draw(self.screen)
        
        elif self.current_state == GameState.VICTORY:
            font = pygame.font.SysFont(None, 72)
            text = font.render("VICTORY!", True, (0, 200, 0))
            text_rect = text.get_rect(center=(self.screen_width//2, 150))
            self.screen.blit(text, text_rect)

            # ----- Punteggio ----- #
            score_text = font.render(f"Punti: {self.points}", True, (255, 255, 255))
            score_rect = score_text.get_rect(center=(self.screen_width//2, 230))
            self.screen.blit(score_text, score_rect)
            
            for button in self.victory_buttons:
                button.check_hover(mouse_pos)
                button.draw(self.screen)
        
        elif self.current_state == GameState.GAMEOVER:
            font = pygame.font.SysFont(None, 72)
            text = font.render("GAME OVER", True, (200, 0, 0))
            text_rect = text.get_rect(center=(self.screen_width//2, 150))
            self.screen.blit(text, text_rect)

            # ----- Punteggio ----- #
            score_text = font.render(f"Punti: {self.points}", True, (255, 255, 255))
            score_rect = score_text.get_rect(center=(self.screen_width//2, 230))
            self.screen.blit(score_text, score_rect)
            
            for button in self.gameover_buttons:
                button.check_hover(mouse_pos)
                button.draw(self.screen)
        
        pygame.display.flip()

    def create_game_matrix(self):
        """
        Crea una matrice che rappresenta lo stato attuale del gioco
        
        La matrice ha dimensioni (screen_height // cell_size) x (screen_width // cell_size)
        I valori nella matrice rappresentano:
        - 0: spazio vuoto
        - P: Player
        - A: Aliens
        - ^: Player's bullets
        - v: Alien's bullets
        """

        rows = self.screen_height // self.cell_size
        cols = self.screen_width // self.cell_size
        matrix = np.full((rows, cols), "0", dtype=str)
        
        # Aggiungi giocatore
        player_row = self.player.rect.y // self.cell_size
        player_col = self.player.rect.x // self.cell_size
        if 0 <= player_row < rows and 0 <= player_col < cols:
            matrix[player_row, player_col] = "P"
        
        # Aggiungi nemici
        for enemy in self.enemies:
            enemy_row = enemy.rect.y // self.cell_size
            enemy_col = enemy.rect.x // self.cell_size
            if 0 <= enemy_row < rows and 0 <= enemy_col < cols:
                matrix[enemy_row, enemy_col] = "A"
        
        # Aggiungi proiettili del giocatore
        for bullet in self.bullets:
            bullet_row = bullet.rect.y // self.cell_size
            bullet_col = bullet.rect.x // self.cell_size
            if 0 <= bullet_row < rows and 0 <= bullet_col < cols:
                matrix[bullet_row, bullet_col] = "^"
        
        # Aggiungi proiettili dei nemici
        for shot in self.enemy_shots:
            shot_row = shot.rect.y // self.cell_size
            shot_col = shot.rect.x // self.cell_size
            if 0 <= shot_row < rows and 0 <= shot_col < cols:
                matrix[shot_row, shot_col] = "v"
        
        return matrix

    def run(self):
        """Loop principale del gioco"""
        while self.running:
            current_time = time.time()
            self.handle_events()
            
            if self.current_state == GameState.PLAYING:
                self.render()
                
                # Se è passato il tempo del delay dall'ultima azione
                if current_time - self.last_action_time >= self.action_delay:
                    # Genera la matrice di gioco e ottieni il prompt
                    game_matrix = self.create_game_matrix()
                    print("Matrice di gioco generata...")
                    
                    prompt = PromptBuilder.build(game_matrix, self.lives, self.tot_moves)
                    print("Prompt generato...")

                    # Ottieni una singola azione dall'LLM
                    action = self.llm_client.get_next_move(prompt)
                    print(f"Azione ricevuta: {action}")
                    
                    # Esegui l'azione
                    if action:  # Solo se abbiamo una risposta valida
                        self.tot_moves += 1
                        self._execute_action(action)
                        self.last_action_time = current_time
                        self._advance_game_frame()
            
            self.render()
            self.clock.tick(60)  # Mantieni il gioco a 60 FPS

        pygame.quit()