import pygame
import random
from tiles import Tile

class Powerup(Tile):
    def __init__(self, x, y, powerup_type="fireball", width=95, height=70):  # Updated height
        self.powerup_type = powerup_type
        super().__init__(x, y, width, height, health=1)
        self.update_appearance()
        
    def update_appearance(self):
        if self.powerup_type == "fireball":
            self.color = (255, 255, 255)  # White
        
    def draw(self, screen):
        if self.active:
            if self.powerup_type == "fireball":
                # Draw white circle
                center_x = self.rect.centerx
                center_y = self.rect.centery
                radius = min(self.rect.width, self.rect.height) // 3
                pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), radius)
    
    def take_damage(self, damage=1):
        self.destroy()
        return self.powerup_type

def create_powerup_grid(round_number, existing_tiles=[], current_fireball_count=1):
    """
    Create powerups with updated 6-column grid dimensions and gaps.
    """
    powerups = []
    
    # Grid configuration - 6 columns with updated spacing
    GRID_COLS = 6
    GAP_BETWEEN_TILES = 10
    EDGE_GAP = 15
    TILE_WIDTH = 95
    TILE_HEIGHT = 70  # Updated height
    SCREEN_WIDTH = 640
    
    start_x = EDGE_GAP
    start_y = 10
    
    # Adjusted spawn chance for 6 columns instead of 7
    spawn_chance = 0.042
    
    # Only spawn in back 2 rows
    for row in range(2):
        for col in range(GRID_COLS):
            x = start_x + col * (TILE_WIDTH + GAP_BETWEEN_TILES)
            y = start_y + row * (TILE_HEIGHT + GAP_BETWEEN_TILES)  # Updated for new height
            
            # Check if position is occupied
            position_occupied = False
            for existing_tile in existing_tiles:
                if existing_tile.active and existing_tile.rect.x == x and existing_tile.rect.y == y:
                    position_occupied = True
                    break
            
            # Spawn powerup based on calculated chance
            if not position_occupied and random.random() < spawn_chance:
                powerups.append(Powerup(x, y, "fireball", TILE_WIDTH, TILE_HEIGHT))
    
    return powerups