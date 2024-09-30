import pygame
import json

def base_move(self, enemies):
    attack_hitbox_width = 70 
    attack_hitbox_height = 50
    attack_damage = 20

    if not self.facing_left:
        hitbox = pygame.Rect(self.rect.right, self.rect.top, attack_hitbox_width, attack_hitbox_height)
    else:
        hitbox = pygame.Rect(self.rect.left - attack_hitbox_width, self.rect.top, attack_hitbox_width, attack_hitbox_height)

    # Check for collisions with enemies
    for enemy in enemies:
        if hitbox.colliderect(enemy.rect):
            enemy.health -= attack_damage
            # update_health_json(enemy)


# If further developed improve this function to simplify code in the player and enemy classes

def enemy_move(self, players):
    attack_hitbox_width = 70 
    attack_hitbox_height = 50
    attack_damage = 20

    if not self.facing_left:
        hitbox = pygame.Rect(self.rect.right, self.rect.top, attack_hitbox_width, attack_hitbox_height)
    else:
        hitbox = pygame.Rect(self.rect.left - attack_hitbox_width, self.rect.top, attack_hitbox_width, attack_hitbox_height)

    # Check for collisions with players
    for player in players:
        if hitbox.colliderect(player.rect):
            player.health -= attack_damage
            # update_health_json(player)

def update_health_json(entity):
    entity_data = {
        "alive": "true",
        "id": "enemy1",
        "position": {
            "x": entity.x,
            "y": entity.y
        },
        "stats": {
            "speed": 3,
            "health": entity.health
        }
    }
    
    with open(f'{"enemy1"}.json', 'w') as file:
        json.dump(entity_data, file, indent=4)
