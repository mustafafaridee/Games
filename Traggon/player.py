import pygame

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 75)
        self.color = (255, 255, 0)
        self.speed = 5
        
    def update(self):
        if self.rect.x < 25:
            self.rect.x = 25
        if self.rect.x > 700 - 50 - 25:
            self.rect.x = 700 - 50 - 25
            
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)