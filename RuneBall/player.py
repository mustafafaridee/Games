import pygame

class Player:
    def __init__(self, x, y):
        # Scaled down player size to be more appropriate to tiles
        self.rect = pygame.Rect(x, y, 35, 50)  # Smaller than 80x60 tiles
        self.color = (255, 255, 0)
        self.speed = 5
        
    def update(self):
        # Update bounds for new screen width (640px)
        if self.rect.x < 25:
            self.rect.x = 25
        if self.rect.x > 640 - 35 - 25:  # Updated for new player width
            self.rect.x = 640 - 35 - 25
            
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)