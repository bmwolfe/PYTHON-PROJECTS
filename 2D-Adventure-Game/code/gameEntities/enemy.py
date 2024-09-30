import pygame
import json
import os
from os.path import join
from random import randint
from math import sqrt
from mechanics.combat import update_health_json

class Enemy:
    def __init__(self, sprite_sheet_path, idle_sprite_sheet_path, 
                 attack_sheet_path, death_sheet_path, hurt_sheet_path, health, 
                 position, zoom_factor, enemy_id="enemy1"):
        self.zoom_factor = zoom_factor

        self.sprite_sheet = pygame.image.load(join('sprites', sprite_sheet_path)).convert_alpha()
        self.idle_sprite_sheet = pygame.image.load(join('sprites', idle_sprite_sheet_path)).convert_alpha()
        self.attack_sheet = pygame.image.load(join('sprites', attack_sheet_path)).convert_alpha()
        self.death_sheet = pygame.image.load(join('sprites', death_sheet_path)).convert_alpha()
        self.hurt_sheet = pygame.image.load(join('sprites', hurt_sheet_path)).convert_alpha()

        self.num_attack_frames = 7
        self.current_attack_frame = 0
        self.attack_speed = 0.15
        self.attacking = False

        self.health = health

        # Frame settings
        self.frame_width = 96
        self.frame_height = 42
        self.num_frames = 8
        self.frames = self.extract_frames(self.sprite_sheet)
        self.idle_frames = self.extract_frames(self.idle_sprite_sheet)
        self.death_frames = self.extract_frames(self.death_sheet)
        self.attack_frames = self.extract_frames(self.attack_sheet)

        # Enemy attributes
        self.x, self.y = position
        self.current_frame = 0
        self.speed = 1
        self.chase_speed = 2
        self.chase_distance = 150  
        self.animation_speed = 0.1
        self.moving = False
        self.direction = None
        self.facing_left = False
        self.is_near_player = False

        self.is_dead = False
        self.death_frame_index = 0
        self.death_animation_done = False

        self.attack_range = 50 
        self.attack_cooldown = 2  
        self.last_attack_time = 0  

        self.enemy_id = enemy_id
        self.json_file = f'{self.enemy_id}.json'
        self.load_from_json(position)

        self.dx, self.dy = 0, 0 

        self.rect = pygame.Rect(self.x, self.y, 54, 64)
        self.generate_json()

    def extract_frames(self, sprite_sheet):
        sheet_width, sheet_height = sprite_sheet.get_size()

        frames = []
        for i in range(self.num_frames):
            x = i * self.frame_width
            if x + self.frame_width <= sheet_width and self.frame_height <= sheet_height:
                frame = sprite_sheet.subsurface(pygame.Rect(x, 0, self.frame_width, self.frame_height))
                scaled_frame = pygame.transform.scale(frame, (int(self.frame_width * self.zoom_factor), int(self.frame_height * self.zoom_factor)))
                frames.append(scaled_frame)
        return frames

    def handle_horizontal_collisions(self, walls):
        for wall in walls:
            if self.rect.colliderect(wall):
                if self.dx > 0: 
                    self.rect.right = wall.left
                    self.x = self.rect.x
                elif self.dx < 0: 
                    self.rect.left = wall.right
                    self.x = self.rect.x

                self.dx = 0
                self.moving = False

    def handle_vertical_collisions(self, walls):
        for wall in walls:
            if self.rect.colliderect(wall):
                if self.dy > 0: 
                    self.rect.bottom = wall.top
                    self.y = self.rect.y
                elif self.dy < 0: 
                    self.rect.top = wall.bottom
                    self.y = self.rect.y

                self.dy = 0
                self.moving = False

    def distance_to_player(self, player):
        return sqrt((self.x - player.x) ** 2 + (self.y - player.y) ** 2)

    def chase_player(self, walls, players, player):
        if self.attacking:
            return

        self.moving = True
        self.current_frame += self.animation_speed
        if self.current_frame >= self.num_frames:
            self.current_frame = 0

        # Calculate direction and speed
        if self.x < player.x - 30:
            self.dx = self.chase_speed
            self.facing_left = False
        elif self.x > player.x + 30:
            self.dx = -self.chase_speed
            self.facing_left = True
        else:
            self.dx = 0
            self.moving = False

        if self.y < player.y + 10:
            self.dy = self.chase_speed
        elif self.y > player.y:
            self.dy = -self.chase_speed
        else:
            self.dy = 0
            self.moving = False

        # Move the enemy
        self.x += self.dx
        self.rect.x = self.x
        self.handle_horizontal_collisions(walls)

        self.y += self.dy
        self.rect.y = self.y
        self.handle_vertical_collisions(walls)

    def attack_player(self, player):
        current_time = pygame.time.get_ticks() / 1000 
        if current_time - self.last_attack_time >= self.attack_cooldown:
            self.attacking = True  
            self.current_attack_frame = 0
            player.health -= 10  
            update_health_json(player) 
            self.last_attack_time = current_time

    def detect_nearby_player(self, walls, players):
        closest_player = None
        closest_distance = float('inf')
        
        for player in players:
            if player.health > 0:
                distance = self.distance_to_player(player)
                if distance < closest_distance:
                    closest_distance = distance
                    closest_player = player

        if closest_player:
            if closest_distance < self.attack_range:
                self.attack_player(closest_player)
            elif closest_distance < self.chase_distance:
                self.is_near_player = True
                self.chase_player(walls, players, closest_player) 
            else:
                self.is_near_player = False
                self.dx, self.dy = 0, 0

    def move_in_direction(self, walls):
        if not self.is_dead:
            self.dx, self.dy = 0, 0

            if self.direction == 'up':
                self.dy = -self.speed
            elif self.direction == 'down':
                self.dy = self.speed
            elif self.direction == 'left':
                self.dx = -self.speed
            elif self.direction == 'right':
                self.dx = self.speed

            self.x += self.dx
            self.rect.x = self.x
            self.handle_horizontal_collisions(walls)

            self.y += self.dy
            self.rect.y = self.y
            self.handle_vertical_collisions(walls)

    def choose_new_direction(self):
        if not self.is_dead and not self.is_near_player:
            next_move = randint(0, 3)
            if next_move == 0:
                self.direction = 'up'
                self.dy = -self.speed
            elif next_move == 1:
                self.direction = 'down'
                self.dy = self.speed
            elif next_move == 2:
                self.direction = 'left'
                self.facing_left = True
                self.dx = -self.speed
            elif next_move == 3:
                self.direction = 'right'
                self.facing_left = False
                self.dx = self.speed

    def load_from_json(self, default_position):
        if os.path.exists(self.json_file):
            with open(self.json_file, 'r') as file:
                data = json.load(file)
                self.alive = data.get("alive", True)
                self.id = data.get("id")
                self.x = data.get("position", {}).get("x", default_position[0])
                self.y = data.get("position", {}).get("y", default_position[1])
                self.speed = data.get("stats", {}).get("speed", 3)
                self.health = data.get("stats", {}).get("health", 100) 
        else:
            self.x, self.y = default_position
            self.speed = 3
            self.health = 100 

        self.rect = pygame.Rect(self.x, self.y, 54, 64)

    def generate_json(self):
        enemy_data = {
            "alive": "true",
            "id": self.enemy_id,
            "position": {
                "x": self.x,
                "y": self.y
            },
            "stats": {
                "speed": self.speed,
                "health": 100
            }
        }

        with open(self.json_file, 'w') as file:
            json.dump(enemy_data, file, indent=4)

    def update(self, walls, players):
        if self.health <= 0 and not self.is_dead:
            self.is_dead = True
            self.current_frame = 0 

        if self.is_dead:
            if self.play_death_animation():
                return True 
        else:
            if self.attacking:
                self.current_attack_frame += self.attack_speed
                if int(self.current_attack_frame) >= len(self.attack_frames):
                    self.attacking = False 
                    self.current_attack_frame = 0 
            else:
                alive_players = [player for player in players if player.health > 0]

                if alive_players:
                    self.detect_nearby_player(walls, alive_players) 
                else:
                    self.dx, self.dy = 0, 0 
                    self.is_near_player = False

                if not self.is_near_player:
                    if not self.moving:
                        self.current_frame += self.animation_speed
                        if self.current_frame >= self.num_frames:
                            self.current_frame = 0

                        # Choose a new direction occasionally
                        if randint(0, 100) < 5:
                            self.moving = True
                            if not self.direction or randint(0, 100) < 20:
                                self.choose_new_direction()

                    if self.moving:
                        self.move_in_direction(walls)
                        self.current_frame += self.animation_speed
                        if self.current_frame >= self.num_frames:
                            self.current_frame = 0
                        # Occasionally stop moving
                        if randint(0, 100) < 5:
                            self.moving = False
                    else:
                        self.current_frame += self.animation_speed
                        if self.current_frame >= self.num_frames:
                            self.current_frame = 0

        self.generate_json() 

    def play_death_animation(self):
        self.current_frame += self.animation_speed
        if int(self.current_frame) >= len(self.death_frames):
            self.death_animation_done = True
        else:
            self.death_frame_index = int(self.current_frame) % len(self.death_frames)

        return self.death_animation_done

    def draw_health_bar(self, surface, camera_x, camera_y):
        bar_width = 50
        bar_height = 5
        
        health_percentage = self.health / 100
        
        health_color = (255, 0, 0) 
        
        bar_x = self.x - camera_x
        bar_y = self.y - camera_y - 10 
        
        pygame.draw.rect(surface, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        
        current_health_width = int(bar_width * health_percentage)
        pygame.draw.rect(surface, health_color, (bar_x, bar_y, current_health_width, bar_height))

    def draw(self, surface, camera_x, camera_y):
        if self.is_dead:
            current_frame_image = self.death_frames[self.death_frame_index]
        elif self.attacking:
            current_frame_image = self.attack_frames[int(self.current_attack_frame)]
        elif not self.moving:
            current_frame_image = self.idle_frames[int(self.current_frame) % len(self.idle_frames)]
        else:
            current_frame_image = self.frames[int(self.current_frame) % len(self.frames)]

        if self.facing_left:
            current_frame_image = pygame.transform.flip(current_frame_image, True, False)

        surface.blit(current_frame_image, (self.x - camera_x, self.y - camera_y))
        self.draw_health_bar(surface, camera_x - 120, camera_y - 65)