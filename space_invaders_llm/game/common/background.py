import pygame
from pathlib import Path

class Background:
    def __init__(self, screen_width, screen_height, image_path=None, default_color=(0, 0, 0)):
        """
        Inizializza lo sfondo con:
        - screen_width: larghezza dello schermo
        - screen_height: altezza dello schermo
        - image_path: percorso dell'immagine di sfondo (opzionale)
        - default_color: colore di fallback se l'immagine non viene caricata
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.default_color = default_color
        self.image = None
        
        if image_path:
            self.load_image(image_path)
    
    def load_image(self, image_path):
        """Carica e scala l'immagine di sfondo"""
        try:
            # Cerca il percorso partendo dalla radice del progetto
            project_root = Path(__file__).parent.parent.parent  # Adjust based on your structure
            full_path = project_root / image_path
            
            # Debug: stampa il percorso che sta cercando
            print(f"Trying to load background from: {full_path}")
            
            self.image = pygame.image.load(str(full_path))
            self.image = pygame.transform.scale(self.image, (self.screen_width, self.screen_height))
            print("Background loaded successfully!")
        except Exception as e:
            print(f"Errore nel caricamento dello sfondo: {e}")
            self.image = None
    
    def draw(self, surface):
        """Disegna lo sfondo sulla superficie"""
        if self.image:
            surface.blit(self.image, (0, 0))
        else:
            surface.fill(self.default_color)