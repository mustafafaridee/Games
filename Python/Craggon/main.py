import pygame, sys
from player import Player
from tiles import Tile, create_tile_row
from fireball import Fireball

pygame.init()

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 960
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption('Craggon')

clock = pygame.time.Clock()

def main():
    running = True
    player = Player(SCREEN_WIDTH // 2 - 25, SCREEN_HEIGHT - 100)
    
    tiles = create_tile_row(10, 5, [])
    
    fireballs = []
    can_shoot = True
    fireballs_per_shot = 5
    
    pending_fireballs = []
    spawn_delay = 10

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and can_shoot:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    
                    for i in range(fireballs_per_shot):
                        fireball_x = player.rect.x + player.rect.width // 2 - 15
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

        player.update()
        
        for pending in pending_fireballs[:]:
            pending['spawn_time'] -= 1
            if pending['spawn_time'] <= 0:
                fireballs.append(Fireball(pending['x'], pending['y'], pending['target_x'], pending['target_y']))
                pending_fireballs.remove(pending)
        
        for fireball in fireballs:
            if fireball.active and fireball.collision_cooldown == 0:
                collision_found = False
                closest_tile = None
                min_distance = float('inf')
                
                for tile in tiles:
                    if tile.active and fireball.rect.colliderect(tile.rect):
                        dx = fireball.rect.centerx - tile.rect.centerx
                        dy = fireball.rect.centery - tile.rect.centery
                        distance = (dx * dx + dy * dy) ** 0.5
                        
                        if distance < min_distance:
                            min_distance = distance
                            closest_tile = tile
                            collision_found = True
                
                if collision_found and closest_tile:
                    tile = closest_tile
                    tile.take_damage(1)
                    fireball.collision_cooldown = 10
                    
                    fireball_center_x = fireball.rect.centerx
                    fireball_center_y = fireball.rect.centery
                    tile_center_x = tile.rect.centerx
                    tile_center_y = tile.rect.centery
                    
                    overlap_x = min(fireball.rect.right - tile.rect.left, tile.rect.right - fireball.rect.left)
                    overlap_y = min(fireball.rect.bottom - tile.rect.top, tile.rect.bottom - fireball.rect.top)
                    
                    if overlap_x < overlap_y:
                        fireball.vel_x = -fireball.vel_x
                        
                        if fireball_center_x < tile_center_x:
                            new_x = tile.rect.left - fireball.rect.width - 1
                            new_y = fireball.rect.y
                        else:
                            new_x = tile.rect.right + 1
                            new_y = fireball.rect.y
                    else:
                        fireball.vel_y = -fireball.vel_y
                        
                        if fireball_center_y < tile_center_y:
                            new_x = fireball.rect.x
                            new_y = tile.rect.top - fireball.rect.height - 1
                        else:
                            new_x = fireball.rect.x
                            new_y = tile.rect.bottom + 1
                    
                    test_rect = pygame.Rect(new_x, new_y, fireball.rect.width, fireball.rect.height)
                    position_safe = True
                    
                    for check_tile in tiles:
                        if check_tile.active and check_tile != tile and test_rect.colliderect(check_tile.rect):
                            position_safe = False
                            break
                    
                    if position_safe:
                        fireball.rect.x = new_x
                        fireball.rect.y = new_y
        
        last_returned_x = None
        for fireball in fireballs[:]:
            fireball.update()
            if not fireball.active:
                if fireball.returned:
                    last_returned_x = fireball.rect.x
                fireballs.remove(fireball)

        if not can_shoot and len(fireballs) == 0 and len(pending_fireballs) == 0:
            can_shoot = True
            if last_returned_x is not None:
                new_player_x = last_returned_x - player.rect.width // 2 + 15
                if new_player_x < 25:
                    new_player_x = 25
                if new_player_x > 700 - 50 - 25:
                    new_player_x = 700 - 50 - 25
                player.rect.x = new_player_x
            
            tile_height = 75
            gap = 10
            
            for tile in tiles:
                tile.rect.y += tile_height + gap
            
            player_level = player.rect.y
            for tile in tiles:
                if tile.active and tile.rect.y >= player_level:
                    print("Game Over! A tile reached the player!")
                    running = False
                    break
            
            if running:
                tiles = [tile for tile in tiles if tile.rect.y < SCREEN_HEIGHT - 150]
                
                new_tiles = create_tile_row(10, 5, tiles)
                tiles.extend(new_tiles)

        screen.fill((0, 0, 0))

        for tile in tiles:
            tile.draw(screen)
            
        for fireball in fireballs:
            fireball.draw(screen)
            
        player.draw(screen)

        pygame.display.update()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()