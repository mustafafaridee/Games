import pygame
import random

class Tile:
    def __init__(self, x, y, width=95, height=70, health=1):  # Increased height from 60 to 70
        self.rect = pygame.Rect(x, y, width, height)
        self.active = True
        self.health = health
        self.color = (100, 100, 100)  # Neutral gray color
        
    def draw(self, screen):
        if self.active:
            # Draw tile background (no white outline)
            pygame.draw.rect(screen, self.color, self.rect)
            
            # Draw health number in center with pixelated font
            font = pygame.font.Font(None, 36)  # Larger, more pixelated font
            health_text = font.render(str(self.health), True, (255, 255, 255))
            text_rect = health_text.get_rect(center=self.rect.center)
            screen.blit(health_text, text_rect)
    
    def take_damage(self, damage=1):
        self.health -= damage
        if self.health <= 0:
            self.destroy()
        
    def destroy(self):
        self.active = False

def create_tiles_grid(round_number, existing_tiles=[]):
    """
    Create tiles in a 6-column grid with 10px gaps between tiles and 15px edge gaps.
    9 rows total before reaching player zone.
    Only spawn in back 2 rows (rows 0-1) with 25% chance per empty slot.
    """
    tiles = []
    
    # Grid configuration - 6 columns, 9 rows
    GRID_COLS = 6
    GRID_ROWS = 9
    GAP_BETWEEN_TILES = 10
    EDGE_GAP = 15
    SCREEN_WIDTH = 640
    
    # Calculate tile height for 9 rows to fit before player zone (750px available)
    # 750 = 9 * tile_height + 8 * gap_between_tiles + top_margin
    # 750 = 9 * tile_height + 8 * 10 + 10
    # 750 = 9 * tile_height + 90
    # tile_height = (750 - 90) / 9 = 73.33 -> round to 70 for better spacing
    TILE_WIDTH = 95
    TILE_HEIGHT = 70  # Increased from 60
    
    # Calculate starting position with larger edge gap
    start_x = EDGE_GAP
    start_y = 10  # Top margin
    
    # Calculate health range
    min_health = max(1, int(0.75 * round_number))
    max_health = max(1, round_number)
    
    # Only spawn in back 2 rows (rows 0 and 1)
    for row in range(2):
        for col in range(GRID_COLS):
            x = start_x + col * (TILE_WIDTH + GAP_BETWEEN_TILES)
            y = start_y + row * (TILE_HEIGHT + GAP_BETWEEN_TILES)
            
            # Check if position is occupied
            position_occupied = False
            for existing_tile in existing_tiles:
                if existing_tile.active and existing_tile.rect.x == x and existing_tile.rect.y == y:
                    position_occupied = True
                    break
            
            # 25% chance to spawn if position is free
            if not position_occupied and random.random() < 0.25:
                health = random.randint(min_health, max_health)
                tiles.append(Tile(x, y, TILE_WIDTH, TILE_HEIGHT, health=health))
    
    return tiles

def move_tiles_down(tiles):
    """Move all tiles down by one row (80px = 70px tile + 10px gap)"""
    for tile in tiles:
        tile.rect.y += 80  # Updated from 70 to 80

def get_grid_position(x, y):
    """Convert pixel coordinates to grid coordinates"""
    GAP_BETWEEN_TILES = 10
    EDGE_GAP = 15
    TILE_WIDTH = 95
    TILE_HEIGHT = 70  # Updated
    
    start_x = EDGE_GAP
    start_y = 10
    
    col = (x - start_x) // (TILE_WIDTH + GAP_BETWEEN_TILES)
    row = (y - start_y) // (TILE_HEIGHT + GAP_BETWEEN_TILES)
    
    return col, row

def is_valid_grid_position(col, row):
    """Check if grid position is valid (within bounds)"""
    return 0 <= col < 6 and 0 <= row < 9