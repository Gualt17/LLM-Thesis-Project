import pygame
import time
from common.shoot import Shoot

class Player:
    def __init__(self, x, y, width, height, screen_width, asset_manager, cell_size,
                 shot_cooldown=0.5, bullet_speed=50):
        """
            Inizializza il giocatore con:
            - x, y: posizione iniziale
            - width, height: dimensioni del rettangolo di collisione
            - screen_width: larghezza dello schermo
            - asset_manager: riferimento all'AssetManager per caricare le immagini
        """
        
        self.rect = pygame.Rect(x, y, width, height)
        self.screen_width = screen_width
        self.screen_height = 0

        self.asset_manager = asset_manager

        self.original_x = x
        self.cell_size = cell_size

        self.bullet_speed = bullet_speed
        self.last_shot_time = 0
        self.shoot_cooldown = shot_cooldown
        
        
        # Inizializzazione immagine del giocatore
        self.image = self._load_player_image(width, height)
        self.color = (0, 128, 255)  # Colore di fallback

    def _load_player_image(self, width, height):
        """
            Carica e ridimensiona l'immagine del giocatore + fallback
        """

        try:
            original_img = self.asset_manager.load_image("images/player.png")
            
            # Calcola il rapporto di scala mantenendo le proporzioni
            scale = min(width/original_img.get_width(), height/original_img.get_height())
            new_width = int(original_img.get_width() * scale)
            new_height = int(original_img.get_height() * scale)
            
            img = pygame.transform.scale(original_img, (new_width, new_height))
            
            # Offset per centrare l'immagine
            self.image_offset_x = (width - new_width) // 2
            self.image_offset_y = (height - new_height) // 2
            
            return img
        except Exception as e: # Fallback
            print(f"Errore nel caricamento dell'immagine del player: {e}")
            surf = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.polygon(surf, self.color, [
                (width//2, 0), 
                (0, height),
                (width, height)
            ])
            return surf

    def move_left(self):
        """
            Muove il giocatore a sinistra di una cella
        """

        self.rect.x = max(0, self.rect.x - self.cell_size)
        
    def move_right(self):
        """
            Muove il giocatore a destra di una cella
        """

        max_x = self.screen_width - self.rect.width
        self.rect.x = min(max_x, self.rect.x + self.cell_size)

    def shoot(self):
        """
            Crea un nuovo proiettile se il cooldown lo permette
        """

        current_time = time.time()
        if current_time - self.last_shot_time >= self.shoot_cooldown:
            self.last_shot_time = current_time
            bullet = Shoot(self.rect.centerx, self.rect.top - 50)
            bullet.speed = self.bullet_speed
            return bullet
        return None

    def draw(self, surface):
        """Disegna il giocatore sullo schermo"""
        if self.image:
            # Disegna l'immagine centrata nel rettangolo di collisione
            surface.blit(self.image, 
                       (self.rect.x + self.image_offset_x, 
                        self.rect.y + self.image_offset_y))
        else:
            # Fallback grafico
            pygame.draw.rect(surface, self.color, self.rect)
            pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
        
        # DEBUG: mostra il rettangolo di collisione
        if hasattr(self, 'debug_mode') and self.debug_mode:
            pygame.draw.rect(surface, (255, 0, 0), self.rect, 1)

    def reset(self):
        self.rect.x = self.original_x
        self.rect.y = self.screen_height - 50
        self.shoot_cooldown = 0
    