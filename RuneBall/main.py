import pygame, sys
from player import Player
from tiles import Tile, create_tiles_grid, move_tiles_down
from fireball import Fireball
from powerup import Powerup, create_powerup_grid
import math

pygame.init()

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('RuneBall')
clock = pygame.time.Clock()

def line_rect_intersection(x1, y1, x2, y2, rect):
    """Check if line segment intersects with rectangle"""
    if rect.collidepoint(x1, y1) or rect.collidepoint(x2, y2):
        return True
    
    left = rect.left
    right = rect.right
    top = rect.top
    bottom = rect.bottom
    
    edges = [
        (left, top, right, top),
        (right, top, right, bottom),
        (right, bottom, left, bottom),
        (left, bottom, left, top)
    ]
    
    for edge in edges:
        if line_line_intersection(x1, y1, x2, y2, edge[0], edge[1], edge[2], edge[3]):
            return True
    
    min_x, max_x = min(x1, x2), max(x1, x2)
    min_y, max_y = min(y1, y2), max(y1, y2)
    
    rect_min_x, rect_max_x = rect.left, rect.right
    rect_min_y, rect_max_y = rect.top, rect.bottom
    
    if (max_x >= rect_min_x and min_x <= rect_max_x and 
        max_y >= rect_min_y and min_y <= rect_max_y):
        return True
    
    return False

def line_line_intersection(x1, y1, x2, y2, x3, y3, x4, y4):
    """Check if two line segments intersect"""
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-10:
        return False
    
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
    
    return 0 <= t <= 1 and 0 <= u <= 1

def safe_bounce_position(fireball, tile, bounce_direction):
    """Calculate a safe position for fireball after bouncing"""
    if bounce_direction == "horizontal":
        if fireball.rect.centerx < tile.rect.centerx:
            # Ensure fireball is completely to the left of tile
            new_x = tile.rect.left - fireball.rect.width - 1
            new_y = fireball.rect.y
        else:
            # Ensure fireball is completely to the right of tile
            new_x = tile.rect.right + 1
            new_y = fireball.rect.y
    else:
        if fireball.rect.centery < tile.rect.centery:
            # Ensure fireball is completely above tile
            new_x = fireball.rect.x
            new_y = tile.rect.top - fireball.rect.height - 1
        else:
            # Ensure fireball is completely below tile
            new_x = fireball.rect.x
            new_y = tile.rect.bottom + 1
    
    return new_x, new_y

def main():
    running = True
    
    PLAYER_ZONE_START = 750
    UI_ZONE_START = 825
    
    player = Player(SCREEN_WIDTH // 2 - 17, 775)
    
    round_number = 1
    fireballs_per_shot = 1
    
    tiles = create_tiles_grid(round_number, [])
    powerups = create_powerup_grid(round_number, tiles, fireballs_per_shot)
    
    fireballs = []
    can_shoot = True
    
    pending_fireballs = []
    spawn_delay = 10  # Decreased from 30 to original faster spawn delay
    
    fireball_timer = 0
    EMERGENCY_SKIP_TIME = 300

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    
                    if not can_shoot and fireball_timer >= EMERGENCY_SKIP_TIME:
                        if player.rect.collidepoint(mouse_x, mouse_y):
                            fireballs.clear()
                            pending_fireballs.clear()
                            fireball_timer = 0
                            
                            round_number += 1
                            move_tiles_down(tiles)
                            move_tiles_down(powerups)
                            
                            for tile in tiles:
                                if tile.active and tile.rect.bottom >= PLAYER_ZONE_START:
                                    running = False
                                    break
                            
                            if running:
                                tiles = [tile for tile in tiles if tile.rect.bottom < PLAYER_ZONE_START]
                                powerups = [powerup for powerup in powerups if powerup.rect.bottom < PLAYER_ZONE_START]
                                
                                all_objects = tiles + powerups
                                new_tiles = create_tiles_grid(round_number, all_objects)
                                new_powerups = create_powerup_grid(round_number, tiles + new_tiles, fireballs_per_shot)
                                
                                tiles.extend(new_tiles)
                                powerups.extend(new_powerups)
                            
                            can_shoot = True
                            continue
                    
                    if can_shoot and mouse_y < PLAYER_ZONE_START:
                        for i in range(fireballs_per_shot):
                            fireball_x = player.rect.x + player.rect.width // 2 - 10
                            fireball_y = player.rect.y
                            spawn_time = i * spawn_delay
                            pending_fireballs.append({
                                'x': fireball_x,
                                'y': fireball_y,
                                'target_x': mouse_x,
                                'target_y': mouse_y,
                                'spawn_time': spawn_time
                            })
                        
                        can_shoot = False
                        fireball_timer = 0

        player.update()
        
        if not can_shoot and (len(fireballs) > 0 or len(pending_fireballs) > 0):
            fireball_timer += 1
        
        for pending in pending_fireballs[:]:
            pending['spawn_time'] -= 1
            if pending['spawn_time'] <= 0:
                new_fireball = Fireball(pending['x'], pending['y'], pending['target_x'], pending['target_y'])
                fireballs.append(new_fireball)
                pending_fireballs.remove(pending)
        
        # UPDATE FIREBALLS FIRST
        for fireball in fireballs[:]:
            fireball.update()
        
        # THEN CHECK COLLISIONS
        for fireball_id, fireball in enumerate(fireballs):
            if fireball.active:
                line = fireball.get_movement_line()
                
                all_objects = tiles + powerups
                collided_objects = []
                
                for obj in all_objects:
                    if obj.active and not fireball.has_hit_object(obj):
                        rect_collision = fireball.rect.colliderect(obj.rect)
                        line_collision = line_rect_intersection(line[0], line[1], line[2], line[3], obj.rect)
                        
                        if rect_collision or line_collision:
                            dx = fireball.rect.centerx - obj.rect.centerx
                            dy = fireball.rect.centery - obj.rect.centery
                            distance = math.sqrt(dx*dx + dy*dy)
                            collided_objects.append((obj, distance))
                
                if collided_objects:
                    collided_objects.sort(key=lambda x: x[1])
                    closest_object = collided_objects[0][0]
                    
                    fireball.mark_object_as_hit(closest_object)
                    
                    if isinstance(closest_object, Powerup):
                        powerup_type = closest_object.take_damage(1)
                        if powerup_type == "fireball":
                            fireballs_per_shot += 1
                    
                    elif isinstance(closest_object, Tile):
                        tile = closest_object
                        tile.take_damage(2)  # Fireballs now do 2 damage
                        
                        overlap_left = fireball.rect.right - tile.rect.left
                        overlap_right = tile.rect.right - fireball.rect.left
                        overlap_top = fireball.rect.bottom - tile.rect.top
                        overlap_bottom = tile.rect.bottom - fireball.rect.top
                        
                        min_overlap_x = min(overlap_left, overlap_right)
                        min_overlap_y = min(overlap_top, overlap_bottom)
                        
                        if min_overlap_x < min_overlap_y:
                            fireball.vel_x = -fireball.vel_x
                            new_x, new_y = safe_bounce_position(fireball, tile, "horizontal")
                        else:
                            fireball.vel_y = -fireball.vel_y
                            new_x, new_y = safe_bounce_position(fireball, tile, "vertical")
                        
                        fireball.rect.x = max(0, min(new_x, 640 - fireball.rect.width))
                        fireball.rect.y = max(0, min(new_y, 825 - fireball.rect.height))
        
        # REMOVE INACTIVE FIREBALLS
        last_returned_x = None
        for fireball in fireballs[:]:
            if not fireball.active:
                if fireball.returned:
                    last_returned_x = fireball.rect.x
                fireballs.remove(fireball)

        if not can_shoot and len(fireballs) == 0 and len(pending_fireballs) == 0:
            can_shoot = True
            fireball_timer = 0
            if last_returned_x is not None:
                new_player_x = last_returned_x - player.rect.width // 2 + 10
                new_player_x = max(25, min(new_player_x, 640 - 35 - 25))
                player.rect.x = new_player_x
            
            round_number += 1
            move_tiles_down(tiles)
            move_tiles_down(powerups)
            
            for tile in tiles:
                if tile.active and tile.rect.bottom >= PLAYER_ZONE_START:
                    running = False
                    break
            
            if running:
                tiles = [tile for tile in tiles if tile.rect.bottom < PLAYER_ZONE_START]
                powerups = [powerup for powerup in powerups if powerup.rect.bottom < PLAYER_ZONE_START]
                
                all_objects = tiles + powerups
                new_tiles = create_tiles_grid(round_number, all_objects)
                new_powerups = create_powerup_grid(round_number, tiles + new_tiles, fireballs_per_shot)
                
                tiles.extend(new_tiles)
                powerups.extend(new_powerups)

        screen.fill((0, 0, 20))

        player_zone_rect = pygame.Rect(0, PLAYER_ZONE_START, SCREEN_WIDTH, 75)
        pygame.draw.rect(screen, (128, 128, 128), player_zone_rect)

        ui_zone_rect = pygame.Rect(0, UI_ZONE_START, SCREEN_WIDTH, 75)
        pygame.draw.rect(screen, (64, 64, 64), ui_zone_rect)

        for tile in tiles:
            tile.draw(screen)
        
        for powerup in powerups:
            powerup.draw(screen)
            
        for fireball in fireballs:
            fireball.draw(screen)

        if not can_shoot and fireball_timer >= EMERGENCY_SKIP_TIME:
            if (fireball_timer // 10) % 2 == 0:
                pygame.draw.rect(screen, (255, 255, 0), player.rect)
                pygame.draw.rect(screen, (255, 255, 255), player.rect, 3)
            else:
                player.draw(screen)
                pygame.draw.rect(screen, (255, 255, 0), player.rect, 2)
        else:
            player.draw(screen)

        try:
            font = pygame.font.Font("fonts/pixel.ttf", 24)
        except:
            font = pygame.font.SysFont("courier", 24, bold=True)
        
        score_text = font.render(f"Round: {round_number}", True, (255, 255, 255))
        screen.blit(score_text, (10, UI_ZONE_START + 10))
        
        fireball_text = font.render(f"Fireballs: {fireballs_per_shot}", True, (255, 255, 255))
        screen.blit(fireball_text, (10, UI_ZONE_START + 40))

        pygame.display.update()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()