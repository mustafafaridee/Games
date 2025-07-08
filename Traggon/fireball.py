import pygame
import math

class Fireball:
    def __init__(self, x, y, target_x, target_y):
        self.rect = pygame.Rect(x, y, 30, 30)
        self.color = (255, 0, 0)  # Red
        self.speed = 10
        self.active = True
        self.returned = False
        self.collision_cooldown = 0  # Add collision cooldown
        
        # Calculate direction vector
        dx = target_x - (x + 15)  # +15 to aim from fireball center
        dy = target_y - (y + 15)
        distance = math.sqrt(dx**2 + dy**2)
        
        # Normalize and apply speed
        if distance > 0:
            self.vel_x = (dx / distance) * self.speed
            self.vel_y = (dy / distance) * self.speed
        else:
            self.vel_x = 0
            self.vel_y = -self.speed  # Default upward if clicked on player
        
    def update(self):
        if self.active:
            self.rect.x += self.vel_x
            self.rect.y += self.vel_y
            
            # Decrease collision cooldown
            if self.collision_cooldown > 0:
                self.collision_cooldown -= 1
            
            # Bounce off left/right screen edges
            if self.rect.left <= 0 or self.rect.right >= 700:
                self.vel_x = -self.vel_x
                # Keep within bounds
                if self.rect.left <= 0:
                    self.rect.left = 0
                if self.rect.right >= 700:
                    self.rect.right = 700
                    
            # Bounce off top edge
            if self.rect.top <= 0:
                self.vel_y = -self.vel_y
                self.rect.top = 0
                
            # Return fireball if it hits bottom
            if self.rect.bottom >= 960:
                self.returned = True
                self.active = False
                
    def draw(self, screen):
        if self.active:
            pygame.draw.rect(screen, self.color, self.rect)
            
    def destroy(self):
        self.active = False