import pygame
import random

class Tile:
    def __init__(self, x, y, width=120, height=75, max_difficulty=3):
        self.rect = pygame.Rect(x, y, width, height)
        self.active = True
        self.health = random.randint(1, min(max_difficulty, 10))  # Cap health based on difficulty (increased max)
        self.max_health = 10
        self.update_color()
        
    def update_color(self):
        if self.health == 10:
            self.color = (128, 128, 128)  # Grey
        elif self.health == 9:
            self.color = (139, 69, 79)    # Dark Pink (more red and darker)
        elif self.health == 8:
            self.color = (128, 0, 128)    # Twilight Purple (same darkness as ocean blue)
        elif self.health == 7:
            self.color = (0, 0, 255)      # Ocean Blue
        elif self.health == 6:
            self.color = (100, 180, 255)  # Light Blue
        elif self.health == 5:
            self.color = (0, 150, 80)     # Bluish Green
        elif self.health == 4:
            self.color = (80, 160, 0)     # Green
        elif self.health == 3:
            self.color = (200, 200, 0)    # Yellow
        elif self.health == 2:
            self.color = (200, 120, 0)    # Orange
        elif self.health == 1:
            self.color = (180, 0, 0)      # Red
        else:
            self.color = (255, 255, 255)  # White (health 0, safe tile)
        
    def draw(self, screen):
        if self.active:
            pygame.draw.rect(screen, self.color, self.rect)
    
    def take_damage(self, damage=1):
        self.health -= damage
        self.update_color()
        if self.health <= 0:
            self.destroy()
        
    def destroy(self):
        self.active = False

def create_tile_row(y_position, num_tiles=5, existing_tiles=[], difficulty=3):
    tiles = []
    tile_width = 120
    tile_height = 75
    gap = 10
    screen_width = 700
    
    available_width = screen_width - (2 * gap)
    space_per_tile = available_width // num_tiles
    
    for i in range(num_tiles):
        x = gap + (i * space_per_tile) + ((space_per_tile - tile_width) // 2)
        
        possible_positions = [
            (x, y_position),
            (x, y_position + tile_height + gap)
        ]
        
        for pos_x, pos_y in possible_positions:
            position_occupied = False
            for existing_tile in existing_tiles:
                if existing_tile.active and existing_tile.rect.x == pos_x and existing_tile.rect.y == pos_y:
                    position_occupied = True
                    break
            
            if not position_occupied and random.random() < 0.375:
                tiles.append(Tile(pos_x, pos_y, max_difficulty=difficulty))
    
    return tiles