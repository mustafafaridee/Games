import pygame, sys
from player import Player
from tiles import Tile, create_tile_row
from fireball import Fireball
from powerup import Powerup, create_powerup_row

pygame.init()

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 960
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption('Traggon')

clock = pygame.time.Clock()

def main():
    running = True
    player = Player(SCREEN_WIDTH // 2 - 25, SCREEN_HEIGHT - 100)
    
    # Difficulty system
    round_number = 1
    difficulty = 3
    fireballs_per_shot = 3  # Start with 3 fireballs
    
    tiles = create_tile_row(10, 5, [], difficulty)
    powerups = create_powerup_row(10, 5, tiles)  # Create powerups after tiles
    
    fireballs = []
    can_shoot = True
    
    pending_fireballs = []
    spawn_delay = 10
    
    # Emergency skip system
    fireball_timer = 0
    EMERGENCY_SKIP_TIME = 300  # 5 seconds at 60 FPS

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    
                    # Check if clicking on player during emergency skip
                    if not can_shoot and fireball_timer >= EMERGENCY_SKIP_TIME:
                        if player.rect.collidepoint(mouse_x, mouse_y):
                            # Emergency skip: destroy all fireballs and go to next round
                            fireballs.clear()
                            pending_fireballs.clear()
                            fireball_timer = 0
                            print("Emergency skip activated!")
                            # Force next round
                            can_shoot = True
                            
                            # Increment round and update difficulty
                            round_number += 1
                            if round_number % 5 == 1 and round_number > 1:
                                difficulty += 1
                                print(f"Difficulty increased to {difficulty}!")
                            
                            tile_height = 75
                            gap = 10
                            
                            # Move tiles and powerups down
                            for tile in tiles:
                                tile.rect.y += tile_height + gap
                            for powerup in powerups:
                                powerup.rect.y += tile_height + gap
                            
                            player_level = player.rect.y
                            # Check if any tile has reached the player level
                            for tile in tiles:
                                if tile.active and tile.rect.y >= player_level:
                                    print("Game Over! A tile reached the player!")
                                    running = False
                                    break
                            
                            if running:
                                # Remove tiles and powerups that have moved off screen
                                tiles = [tile for tile in tiles if tile.rect.y < SCREEN_HEIGHT - 150]
                                powerups = [powerup for powerup in powerups if powerup.rect.y < SCREEN_HEIGHT - 150]
                                
                                # Create new tiles and powerups
                                all_objects = tiles + powerups
                                new_tiles = create_tile_row(10, 5, all_objects, difficulty)
                                new_powerups = create_powerup_row(10, 5, tiles + new_tiles)
                                
                                tiles.extend(new_tiles)
                                powerups.extend(new_powerups)
                            continue
                    
                    # Normal shooting
                    if can_shoot:
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
                        fireball_timer = 0  # Reset timer when shooting

        player.update()
        
        # Update fireball timer if fireballs are active
        if not can_shoot and (len(fireballs) > 0 or len(pending_fireballs) > 0):
            fireball_timer += 1
        
        for pending in pending_fireballs[:]:
            pending['spawn_time'] -= 1
            if pending['spawn_time'] <= 0:
                fireballs.append(Fireball(pending['x'], pending['y'], pending['target_x'], pending['target_y']))
                pending_fireballs.remove(pending)
        
        # Check fireball collisions with tiles and powerups
        for fireball in fireballs:
            if fireball.active and fireball.collision_cooldown == 0:
                collision_found = False
                closest_object = None
                min_distance = float('inf')
                
                # Check collisions with tiles
                for tile in tiles:
                    if tile.active and fireball.rect.colliderect(tile.rect):
                        dx = fireball.rect.centerx - tile.rect.centerx
                        dy = fireball.rect.centery - tile.rect.centery
                        distance = (dx * dx + dy * dy) ** 0.5
                        
                        if distance < min_distance:
                            min_distance = distance
                            closest_object = tile
                            collision_found = True
                
                # Check collisions with powerups
                for powerup in powerups:
                    if powerup.active and fireball.rect.colliderect(powerup.rect):
                        dx = fireball.rect.centerx - powerup.rect.centerx
                        dy = fireball.rect.centery - powerup.rect.centery
                        distance = (dx * dx + dy * dy) ** 0.5
                        
                        if distance < min_distance:
                            min_distance = distance
                            closest_object = powerup
                            collision_found = True
                
                if collision_found and closest_object:
                    # Handle powerup collection
                    if isinstance(closest_object, Powerup):
                        powerup_type = closest_object.take_damage(1)
                        if powerup_type == "fireball":
                            fireballs_per_shot += 1
                            print(f"Fireball powerup collected! Now shooting {fireballs_per_shot} fireballs!")
                        fireball.collision_cooldown = 10
                        # Fireball continues through powerups without bouncing
                    
                    # Handle tile collision
                    elif isinstance(closest_object, Tile):
                        tile = closest_object
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
            fireball_timer = 0  # Reset timer when round ends normally
            if last_returned_x is not None:
                new_player_x = last_returned_x - player.rect.width // 2 + 15
                if new_player_x < 25:
                    new_player_x = 25
                if new_player_x > 700 - 50 - 25:
                    new_player_x = 700 - 50 - 25
                player.rect.x = new_player_x
            
            # Increment round and update difficulty
            round_number += 1
            if round_number % 5 == 1 and round_number > 1:
                difficulty += 1
                print(f"Difficulty increased to {difficulty}!")
            
            tile_height = 75
            gap = 10
            
            # Move tiles and powerups down
            for tile in tiles:
                tile.rect.y += tile_height + gap
            for powerup in powerups:
                powerup.rect.y += tile_height + gap
            
            player_level = player.rect.y
            # Check if any tile has reached the player level
            for tile in tiles:
                if tile.active and tile.rect.y >= player_level:
                    print("Game Over! A tile reached the player!")
                    running = False
                    break
            
            if running:
                # Remove tiles and powerups that have moved off screen
                tiles = [tile for tile in tiles if tile.rect.y < SCREEN_HEIGHT - 150]
                powerups = [powerup for powerup in powerups if powerup.rect.y < SCREEN_HEIGHT - 150]
                
                # Create new tiles and powerups
                all_objects = tiles + powerups
                new_tiles = create_tile_row(10, 5, all_objects, difficulty)
                new_powerups = create_powerup_row(10, 5, tiles + new_tiles)
                
                tiles.extend(new_tiles)
                powerups.extend(new_powerups)

        screen.fill((20, 20, 60))

        # Draw tiles
        for tile in tiles:
            tile.draw(screen)
        
        # Draw powerups
        for powerup in powerups:
            powerup.draw(screen)
            
        # Draw fireballs
        for fireball in fireballs:
            fireball.draw(screen)

        # Draw player with emergency skip indicator (draw last so it's on top)
        if not can_shoot and fireball_timer >= EMERGENCY_SKIP_TIME:
            # Flash the player to indicate emergency skip is available
            if (fireball_timer // 10) % 2 == 0:  # Flash every 10 frames
                player_flash_color = (255, 255, 0)  # Yellow flash
                pygame.draw.rect(screen, player_flash_color, player.rect)
                # Add a glowing border effect
                pygame.draw.rect(screen, (255, 255, 255), player.rect, 3)  # White border
            else:
                player.draw(screen)
                # Still show border when not flashing
                pygame.draw.rect(screen, (255, 255, 0), player.rect, 2)  # Yellow border
        else:
            player.draw(screen)

        pygame.display.update()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()