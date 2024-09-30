import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ['SDL_VIDEO_CENTERED'] = '1'

import pygame
from os.path import join
from config import TILE_SIZE
import pytmx
from gameEntities.player import Player
from gameEntities.enemy import Enemy
from data.collisions import Collisions
from mechanics.combat import base_move
from random import randint

pygame.init()

# TODO: implement socket programming for multiplayer

WINDOW_WIDTH, WINDOW_HEIGHT = 1120, 640
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Building a Game')

baseMap = pygame.image.load(join('map', '2DAdventureGameV5.png')).convert_alpha()
foreground = pygame.image.load(join('map', '2DAdventureGameForegroundV2.png')).convert_alpha()
mapWidth, mapHeight = baseMap.get_size()
print(mapWidth)

clock = pygame.time.Clock()

walls = []
players = []
enemies = [] 
enemy_spawn_interval = 10000 
time_since_last_enemy = 0

player = Player( # TODO: add remaining sprites so players can choose a character
    'base_walk_strip8.png',
    'curlyhair_walk_strip8.png',
    'base_idle_strip9.png',
    'curlyhair_idle_strip9.png',
    'base_attack_strip10.png',
    'curlyhair_attack_strip10.png',
    'base_death_strip13.png',
    'curlyhair_death_strip13.png',
    (3500, 2000),
    zoom_factor=3
)
players.append(player)

# Add the initial enemy
initial_enemy = Enemy(
    'skeleton_walk_strip8.png', 
    'skeleton_idle_strip6.png', 
    'skeleton_attack_strip7.png',
    'skeleton_death_strip10.png',
    'skeleton_hurt_strip7.png',
    100, 
    (2200, 1000), 
    zoom_factor=3
)
enemies.append(initial_enemy)

camera_x, camera_y = 0, 0

map_width_tiles = mapWidth // TILE_SIZE 

collision_instance = Collisions(walls, TILE_SIZE, map_width_tiles)

# Ensure value is within the min and max range
def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))

def main():
    global time_since_last_enemy

    time = 0
    lastAttackTime = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        # Player attack logic
        if keys[pygame.K_o]:
            if not player.isDead:
                milliseconds = pygame.time.get_ticks()
                time = int(milliseconds / 1000)
                # player.attacking = True
                if time >= lastAttackTime + 1.25:
                    for enemy in enemies:
                        base_move(player, [enemy])
                        player.attack()
                        lastAttackTimeMilli = pygame.time.get_ticks()
                        lastAttackTime = int(lastAttackTimeMilli / 1000)

        if keys[pygame.K_r]:
            if player.isDead:
                player.respawn((3500, 2000))

        # Spawn new enemies
        time_since_last_enemy += clock.get_time()
        if len(enemies) < 4:
            if time_since_last_enemy >= enemy_spawn_interval:
                new_enemy = Enemy(
                    'skeleton_walk_strip8.png', 'skeleton_idle_strip6.png', 
                    'skeleton_attack_strip7.png', 'skeleton_death_strip10.png', 
                    'skeleton_hurt_strip7.png', 100, (randint(0, mapWidth), randint(0, mapHeight)), 3
                )
                enemies.append(new_enemy)
                time_since_last_enemy = 0

        player.update(keys, walls)

        for enemy in enemies[:]:  
            if enemy.update(walls, players):  
                enemies.remove(enemy)

        # Update camera position to follow player
        camera_x = clamp(player.x - WINDOW_WIDTH // 2, 0, mapWidth - WINDOW_WIDTH)
        camera_y = clamp(player.y - WINDOW_HEIGHT // 2, 0, mapHeight - WINDOW_HEIGHT)

        screen.fill((255, 255, 255)) 
        screen.blit(baseMap, (0, 0), pygame.Rect(camera_x, camera_y, WINDOW_WIDTH, WINDOW_HEIGHT))  # Draw the base map

        font = pygame.font.Font(None, 72)
        font2 = pygame.font.Font(None, 32)

        player.draw(screen, camera_x, camera_y)

        for enemy in enemies:
            enemy.draw(screen, camera_x, camera_y)

        screen.blit(foreground, (0, 0), pygame.Rect(camera_x, camera_y, WINDOW_WIDTH, WINDOW_HEIGHT))

        if player.isDead:
            player.dim_background(screen)
            player.display_death_message(screen, "You Died", "Press r to Respawn", font, font2, screen.get_width(), screen.get_height())

        pygame.display.update()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
