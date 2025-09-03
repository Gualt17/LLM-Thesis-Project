import pygame

class Button:
    def __init__(self, x, y, width, height, text, 
                 color=(70, 70, 70), 
                 hover_color=(100, 100, 100), 
                 text_color=(255, 255, 255),
                 border_color=(255, 255, 255),
                 action=None,
                 font_name='Arial',
                 font_size=30):
        """
        Inizializza un bottone con:
        - x, y: posizione
        - width, height: dimensioni
        - text: testo da visualizzare
        - color: colore normale (default grigio scuro)
        - hover_color: colore al passaggio del mouse (default grigio chiaro)
        - text_color: colore del testo (default bianco)
        - border_color: colore del bordo (default bianco)
        - action: funzione da chiamare al click (opzionale)
        - font_name: nome del font (default Arial)
        - font_size: dimensione del font (default 30)
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_color = border_color
        self.action = action
        self.is_hovered = False
        self.font = pygame.font.SysFont(font_name, font_size)
        self.border_radius = 10

    def draw(self, surface):
        """Disegna il bottone sulla superficie"""
        # Colore principale
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)
        
        # Bordo
        pygame.draw.rect(surface, self.border_color, self.rect, 2, border_radius=self.border_radius)
        
        # Testo
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        """Controlla se il mouse è sopra il bottone"""
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def handle_event(self, event, pos):
        """
        Gestisce gli eventi del mouse per il bottone.
        Restituisce True se il bottone è stato cliccato.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pos):
                print(f"Bottone '{self.text}' cliccato!")  # Debug message
                if self.action:
                    self.action()
                return True
        return False