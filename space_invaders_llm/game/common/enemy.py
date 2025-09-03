import pygame
import random

class Enemy:
    def __init__(self, x, y, asset_manager=None, enemy_speed=50):
        """
        Inizializza un nemico con:
        - x, y: posizione iniziale
        - asset_manager: riferimento all'AssetManager per caricare le immagini (opzionale)
        """
        self.rect = pygame.Rect(x, y, 50, 50)
        self.enemy_speed = enemy_speed  # velocità verticale (non più orizzontale)
        self.color = (255, 0, 0)  # Colore di fallback

        # Gestione immagine
        self.asset_manager = asset_manager
        self.image = None
        self.image_offset_x = 0
        self.image_offset_y = 0

        if self.asset_manager:
            self._load_enemy_image()

    def _load_enemy_image(self):
        enemy_types = ["enemy_type1.png", "enemy_type2.png", "enemy_type3.png"]
        try:
            img_name = random.choice(enemy_types)
            original_img = self.asset_manager.load_image(f"images/{img_name}")

            # Calcola il rapporto di scala mantenendo le proporzioni
            scale = min(self.rect.width / original_img.get_width(),
                        self.rect.height / original_img.get_height())
            new_width = int(original_img.get_width() * scale)
            new_height = int(original_img.get_height() * scale)

            self.image = pygame.transform.scale(original_img, (new_width, new_height))

            # Calcola offset per centrare l'immagine
            self.image_offset_x = (self.rect.width - new_width) // 2
            self.image_offset_y = (self.rect.height - new_height) // 2

        except Exception as e:
            print(f"Errore nel caricamento dell'immagine del nemico: {e}")
            self.image = None  # fallback

    def update(self):
        """Sposta il nemico in basso di una cella (50px)"""
        self.rect.y += self.enemy_speed

    def draw(self, surface):
        """Disegna il nemico sullo schermo"""
        if self.image:
            surface.blit(self.image,
                         (self.rect.x + self.image_offset_x,
                          self.rect.y + self.image_offset_y))
        else:
            pygame.draw.rect(surface, self.color, self.rect)
            pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
