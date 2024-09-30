import pygame
import json
import os
from os.path import join

class Player:
    def __init__(self, sprite_sheet_path, hair_sheet_path, idle_sprite_sheet_path, 
                 idle_hair_sheet_path, attack_sheet_path, attack_hair_path, death_sheet_path, 
                 death_hair_sheet_path, position, zoom_factor, player_id="player1"):
        self.zoom_factor = zoom_factor

        # Load sprite sheets
        self.sprite_sheet = pygame.image.load(join('sprites', sprite_sheet_path)).convert_alpha()
        self.hair_sheet = pygame.image.load(join('sprites', hair_sheet_path)).convert_alpha()
        self.idle_sheet = pygame.image.load(join('sprites', idle_sprite_sheet_path)).convert_alpha()
        self.hair_idle_sheet = pygame.image.load(join('sprites', idle_hair_sheet_path)).convert_alpha()
        self.death_sheet = pygame.image.load(join('sprites', death_sheet_path)).convert_alpha()
        self.hair_death_sheet = pygame.image.load(join('sprites', death_hair_sheet_path)).convert_alpha()

        # Frame settings
        self.frame_width = 96
        self.frame_height = 42
        self.num_frames = 8
        self.frames = self.extract_frames(self.sprite_sheet)
        self.hair_frames = self.extract_frames(self.hair_sheet)
        self.idle_frames = self.extract_frames(self.idle_sheet)
        self.idle_hair_frames = self.extract_frames(self.hair_idle_sheet)
        self.death_frames = self.extract_frames(self.death_sheet)
        self.death_hair_frames = self.extract_frames(self.hair_death_sheet)

        self.death_animation_done = False
        self.death_frame_index = 0
        self.num_death_frames = 13
        self.animation_speed = 0.1

        # Attack animation setup
        self.attack_sheet = pygame.image.load(join('sprites', attack_sheet_path)).convert_alpha()
        self.attack_hair_sheet = pygame.image.load(join('sprites', attack_hair_path)).convert_alpha()
        self.num_attack_frames = 10
        self.attack_frames = self.extract_frames(self.attack_sheet, self.num_attack_frames)
        self.attack_hair = self.extract_frames(self.attack_hair_sheet, self.num_attack_frames)
        self.attacking = False
        self.current_attack_frame = 0
        self.attack_speed = 0.15
        self.isDead = True

        # Load data from file if it exists, else use default values
        self.player_id = player_id
        self.json_file = f'{self.player_id}.json'
        self.load_from_json(position)
        self.current_frame = 0
        self.frame_speed = 0.1
        self.facing_left = False
        self.moving = False
        self.lastRegen = 0
        self.currentTime = 0


        self.update_json()

    def load_from_json(self, default_position):
        if os.path.exists(self.json_file):
            with open(self.json_file, 'r') as file:
                data = json.load(file)
                self.x = data.get("position", {}).get("x", default_position[0])
                self.y = data.get("position", {}).get("y", default_position[1])
                self.speed = data.get("stats", {}).get("speed", 3)
                self.health = data.get("stats", {}).get("health", 100)
                if self.health > 0:
                    self.isDead = False
        else:
            self.x, self.y = default_position
            self.speed = 3
            self.health = 100

        self.rect = pygame.Rect(self.x, self.y, 54, 64)

    def extract_frames(self, sheet, num_frames=None):
        frames = []
        num_frames = num_frames or self.num_frames
        for i in range(num_frames):
            frame = sheet.subsurface(pygame.Rect(i * self.frame_width, 0, self.frame_width, self.frame_height))
            scaled_frame = pygame.transform.scale(frame, (int(self.frame_width * self.zoom_factor), int(self.frame_height * self.zoom_factor)))
            frames.append(scaled_frame)
        return frames

    def update_json(self):
        player_data = {
            "id": self.player_id,
            "position": {
                "x": self.x,
                "y": self.y
            },
            "stats": {
                "speed": self.speed,
                "health": self.health
            }
        }

        with open(self.json_file, 'w') as file:
            json.dump(player_data, file, indent=4)

    def respawn(self, position):
        self.x, self.y = position
        self.rect.x = self.x
        self.rect.y = self.y
        self.health = 50
        self.isDead = False
        self.current_frame = 0 
        self.death_animation_done = False
        self.update_json() 

    def update(self, keys, walls):
        if self.health > 0:
            self.moving = False
            self.dx, self.dy = 0, 0

            if not self.attacking:
                if keys[pygame.K_w] or keys[pygame.K_UP]:
                    self.dy = -self.speed
                    self.moving = True
                if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                    self.dy = self.speed
                    self.moving = True
                if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                    self.dx = -self.speed
                    self.facing_left = True
                    self.moving = True
                if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                    self.dx = self.speed
                    self.facing_left = False
                    self.moving = True

            self.x += self.dx
            self.rect.x = self.x
            self.handle_horizontal_collisions(walls)

            self.y += self.dy
            self.rect.y = self.y
            self.handle_vertical_collisions(walls)

            # Handle animations
            if not self.attacking:
                if self.moving:
                    self.current_frame += self.frame_speed
                    if self.current_frame >= self.num_frames:
                        self.current_frame = 0
                else:
                    self.current_frame += self.frame_speed
                    if self.current_frame >= len(self.idle_frames):
                        self.current_frame = 0
            else:
                self.current_attack_frame += self.attack_speed
                if self.current_attack_frame >= self.num_attack_frames:
                    self.current_attack_frame = 0
                    self.attacking = False

            self.currentTime = pygame.time.get_ticks() / 1000
            if self.currentTime > self.lastRegen + 5:
                if self.health > 0 and self.health < 100:
                    self.lastRegen = pygame.time.get_ticks() / 1000
                    self.health += 5
                    if self.health > 100:
                        self.health = 100
        else:
            self.play_death_animation()

        self.update_json()

    def handle_horizontal_collisions(self, walls):
        for wall in walls:
            if self.rect.colliderect(wall):
                if self.dx > 0:
                    self.rect.right = wall.left
                    self.x = self.rect.x
                if self.dx < 0:
                    self.rect.left = wall.right
                    self.x = self.rect.x

    def handle_vertical_collisions(self, walls):
        for wall in walls:
            if self.rect.colliderect(wall):
                if self.dy > 0:
                    self.rect.bottom = wall.top
                    self.y = self.rect.y
                if self.dy < 0:
                    self.rect.top = wall.bottom
                    self.y = self.rect.y

    def attack(self):
        if not self.attacking:
            self.attacking = True
            self.current_attack_frame = 0

    def draw_health_bar(self, surface, camera_x, camera_y):
        bar_width = 50
        bar_height = 5
        
        health_percentage = self.health / 100
        
        health_color = (135,206,250) 
        
        bar_x = self.x - camera_x
        bar_y = self.y - camera_y - 10 
        
        pygame.draw.rect(surface, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        
        current_health_width = int(bar_width * health_percentage)
        pygame.draw.rect(surface, health_color, (bar_x, bar_y, current_health_width, bar_height))

    def play_death_animation(self):
        self.isDead = True

        # Define the initial death sequence frames and looping frame portion
        initial_death_frames = 6  
        repeat_start_frame = initial_death_frames
        repeat_end_frame = len(self.death_frames) - 1 
        
        self.current_frame += self.animation_speed

        if int(self.current_frame) < initial_death_frames:
            self.death_frame_index = int(self.current_frame)
        else:
            self.death_frame_index = repeat_start_frame + \
                                    int(self.current_frame - initial_death_frames) % (repeat_end_frame - repeat_start_frame + 1)

        # If current_frame exceeds all death frames, stop the death animation
        if self.current_frame >= len(self.death_frames):
            self.death_animation_done = True

    def dim_background(self, surface):
        dim_surface = pygame.Surface(surface.get_size())
        dim_surface.set_alpha(128)
        dim_surface.fill((0, 0, 0))
        surface.blit(dim_surface, (0, 0))

    def display_death_message(self, surface, message, respawnInstructions, font, font2, screen_width, screen_height):
        text = font.render(message, True, (255, 255, 255))  # White text
        text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2))
        surface.blit(text, text_rect)
        text2 = font.render(respawnInstructions, True, (255, 255, 255))  # White text
        text_rect2 = text.get_rect(center=(screen_width // 2 - 120, screen_height // 2 + 100))
        surface.blit(text2, text_rect2)

    def draw(self, surface, camera_x, camera_y):
        if self.health > 0:
            if self.attacking:
                current_frame_image = self.attack_frames[int(self.current_attack_frame)]
                current_hair_image = self.attack_hair[int(self.current_attack_frame)]
            elif self.moving:
                current_frame_image = self.frames[int(self.current_frame)]
                current_hair_image = self.hair_frames[int(self.current_frame)]
            else:
                current_frame_image = self.idle_frames[int(self.current_frame)]
                current_hair_image = self.idle_hair_frames[int(self.current_frame)]
        else:
            if self.death_frame_index >= len(self.death_frames):
                self.death_frame_index = len(self.death_frames) - 1
            current_frame_image = self.death_frames[self.death_frame_index]
            current_hair_image = self.death_hair_frames[self.death_frame_index]

        if self.facing_left:
            current_frame_image = pygame.transform.flip(current_frame_image, True, False)
            current_hair_image = pygame.transform.flip(current_hair_image, True, False)

        adjusted_x = self.x - camera_x
        adjusted_y = self.y - camera_y

        surface.blit(current_frame_image, (adjusted_x, adjusted_y))
        surface.blit(current_hair_image, (adjusted_x, adjusted_y))
        
        if self.health > 0:
            self.draw_health_bar(surface, camera_x - 120, camera_y - 60)