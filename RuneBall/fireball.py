import pygame
import math

class Fireball:
    def __init__(self, x, y, target_x, target_y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.color = (255, 0, 0)
        self.speed = 6
        self.active = True
        self.returned = False
        
        # Store previous position for collision interpolation
        self.prev_x = x
        self.prev_y = y
        
        # SIMPLE FIX: Just prevent immediate re-hitting (1 frame protection)
        self.last_hit_object_id = None
        self.frames_since_hit = 0
        
        # Calculate direction vector
        dx = target_x - (x + 10)
        dy = target_y - (y + 10)
        distance = math.sqrt(dx**2 + dy**2)
        
        # Normalize and apply speed
        if distance > 0:
            self.vel_x = (dx / distance) * self.speed
            self.vel_y = (dy / distance) * self.speed
        else:
            self.vel_x = 0
            self.vel_y = -self.speed
    
    def update(self):
        if self.active:
            # Store previous position before moving
            self.prev_x = self.rect.x
            self.prev_y = self.rect.y
            
            # Move fireball
            self.rect.x += self.vel_x
            self.rect.y += self.vel_y
            
            # Update hit protection counter
            if self.frames_since_hit > 0:
                self.frames_since_hit -= 1
                if self.frames_since_hit <= 0:
                    self.last_hit_object_id = None  # Clear memory
            
            # Bounce off screen edges
            if self.rect.left <= 0:
                self.vel_x = abs(self.vel_x)
                self.rect.left = 0
            elif self.rect.right >= 640:
                self.vel_x = -abs(self.vel_x)
                self.rect.right = 640
                
            # Bounce off top edge
            if self.rect.top <= 0:
                self.vel_y = abs(self.vel_y)
                self.rect.top = 0
                
            # Return fireball if it hits player zone
            if self.rect.bottom >= 825:
                self.returned = True
                self.active = False
    
    def get_movement_line(self):
        """Return line segment representing fireball movement this frame"""
        return (self.prev_x + 10, self.prev_y + 10, self.rect.x + 10, self.rect.y + 10)
    
    def has_hit_object(self, obj):
        """Check if this is the object we just hit (1 frame protection)"""
        obj_id = id(obj)
        return obj_id == self.last_hit_object_id and self.frames_since_hit > 0
    
    def mark_object_as_hit(self, obj):
        """Mark this object as just hit (1 frame protection)"""
        obj_id = id(obj)
        self.last_hit_object_id = obj_id
        self.frames_since_hit = 1  # Only 1 frame protection
    
    def draw(self, screen):
        if self.active:
            pygame.draw.rect(screen, self.color, self.rect)
            
    def destroy(self):
        self.active = False