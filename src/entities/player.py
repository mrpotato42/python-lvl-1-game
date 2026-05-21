"""Player Archer entity in Arrow Defense."""

from __future__ import annotations
import pygame
import math
from typing import Literal, Any
from src.config import (
    PLAYER_MAX_HEALTH, PLAYER_SPEED, PLAYER_ARROW_DAMAGE,
    PLAYER_MAX_CHARGE, PLAYER_WIDTH, PLAYER_HEIGHT, COLOR_PLAYER,
    TOWER_SIDE, TOWER_WIDTH, TOWER_BALCONY_Y, GROUND_Y, SCREEN_WIDTH, GRAVITY,
    ARROW_SPEED_MULTIPLIER, COLOR_HEALTH_BAR_BG, COLOR_HEALTH_BAR_FILL
)
from src.entities.projectile import Projectile
from src.physics.trajectory import calculate_parabola

class Player:
    """Represents the player controlled Archer character."""

    def __init__(self) -> None:
        self.max_health = PLAYER_MAX_HEALTH
        self.health = PLAYER_MAX_HEALTH
        self.speed = PLAYER_SPEED
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        
        # Starting position is at the base of the tower
        if TOWER_SIDE == "left":
            self.x = float(TOWER_WIDTH + 30)
        else:
            self.x = float(SCREEN_WIDTH - TOWER_WIDTH - 30)
            
        self.y = float(GROUND_Y)
        self.in_tower = False
        
        # Firing mechanics
        self.is_charging = False
        self.charge_power = 0.0
        self.cooldown_timer = 0
        self.cooldown_max = 30  # 0.5s fire rate
        self.aim_angle = 0.0
        
        self.direction = 1 if TOWER_SIDE == "left" else -1
        self.damage_flash_timer = 0
        self.walk_cycle = 0.0
        
        # List of fired projectiles to spawn
        self.projectiles_to_spawn: list[Projectile] = []

    def get_rect(self) -> pygame.Rect:
        """Returns the bounding box of the player."""
        return pygame.Rect(
            int(self.x - self.width / 2),
            int(self.y - self.height),
            self.width,
            self.height
        )

    def take_damage(self, amount: float) -> bool:
        """Applies damage to the player. Returns True if dead."""
        self.health = max(0.0, self.health - amount)
        self.damage_flash_timer = 5  # Flash white
        return self.health <= 0

    def update(
        self,
        keys: Any,
        mouse_pos: tuple[int, int],
        mouse_pressed: tuple[bool, bool, bool],
        tower: Any,
    ) -> None:
        """Updates player physics, keyboard movement, mouse aiming, and projectile spawning."""
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= 1
            
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1

        # Check movement boundaries
        min_x = 0.0
        max_x = float(SCREEN_WIDTH)
        
        # Set bounds based on tower configuration and if player is in the tower
        if TOWER_SIDE == "left":
            if self.in_tower:
                # Can only move on the balcony
                min_x = 10.0
                max_x = float(TOWER_WIDTH - 10)
            else:
                # Can only move from tower base to right edge of screen
                min_x = float(TOWER_WIDTH + 15)
                max_x = float(SCREEN_WIDTH - 15)
        else:  # right side tower
            if self.in_tower:
                min_x = float(SCREEN_WIDTH - TOWER_WIDTH + 10)
                max_x = float(SCREEN_WIDTH - 10)
            else:
                min_x = 15.0
                max_x = float(SCREEN_WIDTH - TOWER_WIDTH - 15)

        # Handle controls
        dx = 0.0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = self.speed

        if dx != 0:
            self.x = max(min_x, min(max_x, self.x + dx))
            self.walk_cycle += 0.2
            if not self.is_charging:
                self.direction = 1 if dx > 0 else -1

        # Entering and exiting the tower using W and S
        # Player must be near the tower to enter
        near_tower = False
        if TOWER_SIDE == "left":
            near_tower = self.x <= TOWER_WIDTH + 50
        else:
            near_tower = self.x >= SCREEN_WIDTH - TOWER_WIDTH - 50

        if (keys[pygame.K_w] or keys[pygame.K_UP]) and not self.in_tower and near_tower:
            self.in_tower = True
            # Snap player onto balcony Y and center of balcony X
            self.y = float(TOWER_BALCONY_Y)
            if TOWER_SIDE == "left":
                self.x = float(TOWER_WIDTH / 2)
            else:
                self.x = float(SCREEN_WIDTH - TOWER_WIDTH / 2)
                
        elif (keys[pygame.K_s] or keys[pygame.K_DOWN]) and self.in_tower:
            self.in_tower = False
            self.y = float(GROUND_Y)
            # Spawn at tower base on ground
            if TOWER_SIDE == "left":
                self.x = float(TOWER_WIDTH + 30)
            else:
                self.x = float(SCREEN_WIDTH - TOWER_WIDTH - 30)

        # Mouse Aiming and Arrow Charging
        launch_x = self.x + self.direction * 10
        launch_y = self.y - self.height + 15
        
        # Angle from bow launch position to mouse
        dx_mouse = mouse_pos[0] - launch_x
        dy_mouse = mouse_pos[1] - launch_y
        self.aim_angle = math.atan2(-dy_mouse, dx_mouse)  # inverted y for pygame coordinate mapping

        # Determine face direction during aim
        if mouse_pos[0] > self.x:
            self.direction = 1
        else:
            self.direction = -1

        # Check charging state
        if mouse_pressed[0]:  # Left click held
            if self.cooldown_timer == 0:
                self.is_charging = True
                self.charge_power = min(PLAYER_MAX_CHARGE, self.charge_power + 0.5)
        else:
            # Release click
            if self.is_charging:
                self.fire_arrow(launch_x, launch_y)
                self.is_charging = False
                self.charge_power = 0.0

    def fire_arrow(self, launch_x: float, launch_y: float) -> None:
        """Launches a single arrow based on current aim angle and charge power."""
        # Convert angle and charge power to initial velocities
        speed = self.charge_power * ARROW_SPEED_MULTIPLIER * 25.0
        
        # Clamp velocity to a reasonable range
        vx = math.cos(self.aim_angle) * speed
        vy = -math.sin(self.aim_angle) * speed  # negative Y velocity travels upwards in Pygame

        arrow = Projectile(
            x=launch_x,
            y=launch_y,
            vx=vx,
            vy=vy,
            gravity=GRAVITY,
            damage=PLAYER_ARROW_DAMAGE,
            team="friendly",
            proj_type="arrow",
            launcher=self,
        )
        self.projectiles_to_spawn.append(arrow)
        self.cooldown_timer = self.cooldown_max

    def draw(self, surface: pygame.Surface, particles: Any) -> None:
        """Draws the player, aiming trajectory guide, and charge meter."""
        rect = self.get_rect()
        color = COLOR_PLAYER
        if self.damage_flash_timer > 0:
            color = (255, 255, 255)

        # Create a surface for transparency/shadows
        player_surf = pygame.Surface((rect.width + 20, rect.height + 20), pygame.SRCALPHA)
        
        # Shadow
        shadow_rect = pygame.Rect(10, rect.height + 5, rect.width, 6)
        pygame.draw.ellipse(player_surf, (10, 10, 15, 100), shadow_rect)

        # Body bounce animation
        bounce_y = 0.0
        if not self.in_tower and math.isclose(self.y, GROUND_Y) and self.walk_cycle > 0:
            bounce_y = math.sin(self.walk_cycle) * 3
            
        body_y = 10 + bounce_y
        body_h = rect.height - 10
        body_rect = pygame.Rect(10, body_y, rect.width, body_h)

        # Draw main tunic
        pygame.draw.rect(player_surf, (*color, 255), body_rect, border_radius=4)
        
        # Gold belt/trim
        pygame.draw.rect(player_surf, (230, 180, 20, 255), pygame.Rect(10, body_y + 16, rect.width, 4))

        # Head / Hood
        head_radius = int(rect.width / 2.5)
        head_center = (10 + int(rect.width / 2), int(body_y + 2))
        pygame.draw.circle(player_surf, (215, 180, 150, 255), head_center, head_radius)
        # Archer Hood (matching body color)
        pygame.draw.circle(player_surf, (*color, 255), (head_center[0], head_center[1] - 1), head_radius + 1, draw_top_left=True, draw_top_right=True)

        # Draw Bow
        bow_dir = self.direction
        bow_x = 10 + (rect.width // 2) + bow_dir * (rect.width // 2 - 2)
        bow_y = body_y + 14

        # Curved bow arc representation
        bow_rect = pygame.Rect(bow_x - 3 if bow_dir > 0 else bow_x - 5, bow_y - 12, 8, 24)
        pygame.draw.arc(player_surf, (130, 90, 50, 255), bow_rect, -math.pi/2, math.pi/2 if bow_dir > 0 else 3*math.pi/2, 2)
        
        # Draw Bowstring
        pull_offset = -int(self.charge_power / 2) if bow_dir > 0 else int(self.charge_power / 2)
        string_center = (bow_x + pull_offset, bow_y)
        pygame.draw.line(player_surf, (220, 220, 220, 255), (bow_x, bow_y - 10), string_center, 1)
        pygame.draw.line(player_surf, (220, 220, 220, 255), string_center, (bow_x, bow_y + 10), 1)

        # Draw loaded arrow if charging
        if self.is_charging:
            arrow_angle = self.aim_angle
            arrow_len = 16
            
            # Start of arrow is on pulled bowstring
            arrow_start_x = bow_x + pull_offset
            arrow_start_y = bow_y
            
            # End points out in direction of aim
            arrow_end_x = arrow_start_x + math.cos(arrow_angle) * arrow_len
            arrow_end_y = arrow_start_y - math.sin(arrow_angle) * arrow_len
            pygame.draw.line(player_surf, (240, 240, 250, 255), (arrow_start_x, arrow_start_y), (arrow_end_x, arrow_end_y), 2)
            pygame.draw.circle(player_surf, (230, 70, 70, 255), (int(arrow_start_x), int(arrow_start_y)), 2) # Fletching

        # Blit player
        surface.blit(player_surf, (rect.left - 10, rect.top - 10))

        # Draw visual health bar
        if self.health < self.max_health:
            bar_w = rect.width + 10
            bar_h = 4
            bar_x = rect.left - 5
            bar_y = rect.top - 10
            pygame.draw.rect(surface, COLOR_HEALTH_BAR_BG, (bar_x, bar_y, bar_w, bar_h))
            fill_w = int(bar_w * (self.health / self.max_health))
            pygame.draw.rect(surface, COLOR_HEALTH_BAR_FILL, (bar_x, bar_y, fill_w, bar_h))

        # Trajectory Preview (gorgeous dotted indicator)
        if self.is_charging:
            launch_x = self.x + self.direction * 10
            launch_y = self.y - self.height + 15
            
            speed = self.charge_power * ARROW_SPEED_MULTIPLIER * 25.0
            vx = math.cos(self.aim_angle) * speed
            vy = -math.sin(self.aim_angle) * speed
            
            pts = calculate_parabola(launch_x, launch_y, vx, vy, GRAVITY, GROUND_Y, steps=45)
            
            # Draw dotted lines
            for i in range(0, len(pts), 2):
                if i + 1 < len(pts):
                    pygame.draw.line(surface, (255, 180, 0), pts[i], pts[i+1], 2)
                    
            # Draw targeting circle at predicted impact
            if pts:
                impact = pts[-1]
                pygame.draw.circle(surface, (255, 100, 0), (int(impact[0]), int(impact[1])), 6, 1)
                pygame.draw.circle(surface, (255, 180, 0), (int(impact[0]), int(impact[1])), 2)

        # Firing Charge meter (bar drawn above player's head)
        if self.is_charging:
            meter_w = 40
            meter_h = 5
            meter_x = rect.left + (rect.width - meter_w) // 2
            meter_y = rect.top - 20
            
            # Border
            pygame.draw.rect(surface, (30, 30, 40), (meter_x, meter_y, meter_w, meter_h))
            
            # Percentage fill
            pct = self.charge_power / PLAYER_MAX_CHARGE
            fill_w = int(meter_w * pct)
            
            # Color shifts from green -> yellow -> orange/red as power peaks
            charge_color = (
                int(255 * pct),
                int(255 * (1.0 - pct / 2)),
                0
            )
            pygame.draw.rect(surface, charge_color, (meter_x, meter_y, fill_w, meter_h))
            pygame.draw.rect(surface, (255, 255, 255), (meter_x, meter_y, meter_w, meter_h), 1)
