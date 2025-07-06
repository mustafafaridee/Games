import pygame
import random

class Tile:
    def __init__(self, x, y, width=120, height=75):
        self.rect = pygame.Rect(x, y, width, height)
        self.active = True
        self.health = random.randint(1, 6)
        self.max_health = 6
        self.update_color()
        
    def update_color(self):
        if self.health == 6:
            self.color = (100, 180, 255)
        elif self.health == 5:
            self.color = (0, 150, 80)
        elif self.health == 4:
            self.color = (80, 160, 0)
        elif self.health == 3:
            self.color = (200, 200, 0)
        elif self.health == 2:
            self.color = (200, 120, 0)
        elif self.health == 1:
            self.color = (180, 0, 0)
        else:
            self.color = (128, 128, 128)
        
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

def create_tile_row(y_position, num_tiles=5, existing_tiles=[]):
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
                tiles.append(Tile(pos_x, pos_y))
    
    return tiles