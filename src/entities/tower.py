"""Tower entity defending the player's side of the battlefield."""

import pygame
from src.config import (
    TOWER_MAX_HEALTH, TOWER_WIDTH, TOWER_HEIGHT,
    TOWER_BALCONY_Y, SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_TOWER, COLOR_TOWER_TRIM, TOWER_SIDE,
    COLOR_HEALTH_BAR_BG, COLOR_HEALTH_BAR_FILL
)

class Tower:
    """Represents the defensive tower that player must protect."""

    def __init__(self) -> None:
        self.max_health = TOWER_MAX_HEALTH
        self.health = TOWER_MAX_HEALTH
        self.width = TOWER_WIDTH
        self.height = TOWER_HEIGHT
        
        # Placement based on TOWER_SIDE
        if TOWER_SIDE == "left":
            self.x = 0.0
        else:
            self.x = float(SCREEN_WIDTH - self.width)
            
        self.y = float(SCREEN_HEIGHT - self.height)
        
        # Hit animation/damage visual feedback
        self.damage_flash_timer = 0

    def get_rect(self) -> pygame.Rect:
        """Returns the bounding box of the tower structure."""
        return pygame.Rect(
            int(self.x),
            int(self.y),
            self.width,
            self.height
        )

    def take_damage(self, amount: float) -> bool:
        """Inflicts damage on the tower. Returns True if destroyed."""
        self.health = max(0.0, self.health - amount)
        self.damage_flash_timer = 6  # Flash white for 6 frames
        return self.health <= 0

    def update(self) -> None:
        """Updates animation timers."""
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= 1

    def draw(self, surface: pygame.Surface) -> None:
        """Draws the defensive tower using styled medieval details (crenelations, arch door)."""
        rect = self.get_rect()
        
        # Base color/flash color
        color = COLOR_TOWER
        trim_color = COLOR_TOWER_TRIM
        if self.damage_flash_timer > 0:
            color = (255, 150, 150)  # Red flash
            trim_color = (255, 100, 100)

        # Draw main tower body
        pygame.draw.rect(surface, color, rect)
        
        # Draw vertical shadow/shading line on the side to give depth (3D cylinder/block effect)
        shadow_w = 20
        shadow_x = rect.right - shadow_w if TOWER_SIDE == "left" else rect.left
        shadow_rect = pygame.Rect(shadow_x, rect.top, shadow_w, rect.height)
        pygame.draw.rect(surface, (int(color[0]*0.7), int(color[1]*0.7), int(color[2]*0.7)), shadow_rect)

        # Draw Balcony (Platform on top where player stands)
        balcony_h = 15
        balcony_rect = pygame.Rect(rect.left - 10, rect.top - balcony_h, rect.width + 20, balcony_h)
        pygame.draw.rect(surface, trim_color, balcony_rect)

        # Draw Crenelations (battlements on the top railing)
        battlement_w = 20
        battlement_h = 18
        num_battlement = int(balcony_rect.width / battlement_w)
        for i in range(num_battlement):
            if i % 2 == 0:
                b_x = balcony_rect.left + i * battlement_w
                b_y = balcony_rect.top - battlement_h
                pygame.draw.rect(surface, trim_color, (b_x, b_y, battlement_w, battlement_h))

        # Draw Arched Door/Gate at the bottom
        door_w = 40
        door_h = 60
        door_x = rect.left + (rect.width - door_w) // 2
        door_y = rect.bottom - door_h
        
        # Door frame / interior
        pygame.draw.rect(surface, (15, 15, 20), (door_x, door_y, door_w, door_h))
        pygame.draw.ellipse(surface, (15, 15, 20), (door_x, door_y - door_w // 2, door_w, door_w))
        # Wooden door texture
        wood_color = (100, 60, 30)
        pygame.draw.rect(surface, wood_color, (door_x + 4, door_y + 2, door_w - 8, door_h - 2))
        pygame.draw.ellipse(surface, wood_color, (door_x + 4, door_y - (door_w - 8) // 2 + 2, door_w - 8, door_w - 8))
        
        # Iron hinges
        pygame.draw.line(surface, (50, 50, 55), (door_x + 4, door_y + 15), (door_x + 16, door_y + 15), 3)
        pygame.draw.line(surface, (50, 50, 55), (door_x + 4, door_y + 40), (door_x + 16, door_y + 40), 3)

        # Draw Stone textures on tower (random lines / bricks to look high quality)
        brick_color = (int(color[0]*0.9), int(color[1]*0.9), int(color[2]*0.9))
        for row in range(5):
            for col in range(2):
                bx = rect.left + 15 + col * 50
                by = rect.top + 50 + row * 80
                pygame.draw.rect(surface, brick_color, (bx, by, 30, 15), border_radius=1)

        # Health bar above crenelations
        bar_w = rect.width
        bar_h = 6
        bar_x = rect.left
        bar_y = rect.top - battlement_h - 15
        
        pygame.draw.rect(surface, COLOR_HEALTH_BAR_BG, (bar_x, bar_y, bar_w, bar_h))
        fill_w = int(bar_w * (self.health / self.max_health))
        pygame.draw.rect(surface, COLOR_HEALTH_BAR_FILL, (bar_x, bar_y, fill_w, bar_h))
