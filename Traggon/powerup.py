import pygame
import random
from tiles import Tile

class Powerup(Tile):
    def __init__(self, x, y, powerup_type="fireball", width=120, height=75):
        # Set powerup_type first before calling parent init
        self.powerup_type = powerup_type
        
        # Initialize with health 1 so it gets destroyed on first hit
        super().__init__(x, y, width, height, max_difficulty=1)
        self.health = 1
        self.update_appearance()
        
    def update_appearance(self):
        # Override the color system for powerups
        if self.powerup_type == "fireball":
            self.color = (255, 255, 255)  # White
        # Add other powerup types here later
        
    def update_color(self):
        # Override parent method to use our custom appearance
        self.update_appearance()
        
    def draw(self, screen):
        if self.active:
            if self.powerup_type == "fireball":
                # Draw only a white circle, no rectangle
                center_x = self.rect.centerx
                center_y = self.rect.centery
                radius = min(self.rect.width, self.rect.height) // 3
                pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), radius)
    
    def take_damage(self, damage=1):
        # Powerups are consumed on hit
        self.destroy()
        return self.powerup_type  # Return the type of powerup collected
        
def create_powerup_row(y_position, num_tiles=5, existing_tiles=[], spawn_chance=0.05):
    """
    Create powerups with 5% spawn chance only on the back row
    """
    powerups = []
    tile_width = 120
    tile_height = 75
    gap = 10
    screen_width = 700
    
    available_width = screen_width - (2 * gap)
    space_per_tile = available_width // num_tiles
    
    for i in range(num_tiles):
        x = gap + (i * space_per_tile) + ((space_per_tile - tile_width) // 2)
        
        # Only spawn on the back row (first position)
        pos_x = x
        pos_y = y_position
        
        # Check if there's already a tile at this position
        position_occupied = False
        for existing_tile in existing_tiles:
            if existing_tile.active and existing_tile.rect.x == pos_x and existing_tile.rect.y == pos_y:
                position_occupied = True
                break
        
        # Only spawn if position is free and 5% chance
        if not position_occupied and random.random() < spawn_chance:
            powerups.append(Powerup(pos_x, pos_y, "fireball"))
    
    return powerups