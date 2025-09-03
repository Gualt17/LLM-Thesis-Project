import pygame

class Shoot:
    def __init__(self, x, y, bullet_speed=50):
        self.rect = pygame.Rect(x, y, 4, 10)
        self.bullet_speed = bullet_speed
        self.active = True
        self.color = (0, 255, 0)

    def update(self):
        self.rect.y -= self.bullet_speed
        if self.rect.bottom < 0:
            self.active = False

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

class EnemyShot:
    def __init__(self, x, y, enemy_bullet_speed=50):
        self.rect = pygame.Rect(x, y, 4, 10)
        self.enemy_bullet_speed = enemy_bullet_speed
        self.active = True
        self.color = (255, 255, 0)

    def update(self):
        self.rect.y += self.enemy_bullet_speed
        if self.rect.top > pygame.display.get_surface().get_height():
            self.active = False

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)