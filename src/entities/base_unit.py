"""Base Unit class for troops in Arrow Defense."""

from __future__ import annotations
import pygame
import math
from typing import Literal, Any
from src.config import GROUND_Y, COLOR_HEALTH_BAR_BG, COLOR_HEALTH_BAR_FILL

# Combat States
UnitState = Literal["walking", "combat", "dying"]

class Unit:
    """Base class for all troops (friendly and enemy)."""

    def __init__(
        self,
        x: float,
        team: Literal["friendly", "enemy"],
        max_health: float,
        speed: float,
        damage: float,
        attack_range: float,
        cooldown: int,
        width: int,
        height: int,
        color: tuple[int, int, int],
        name: str,
    ) -> None:
        # Position is defined as center X and bottom Y (standing on ground).
        self.x = x
        self.y = float(GROUND_Y)
        self.team = team
        self.max_health = max_health
        self.health = max_health
        self.speed = speed
        self.damage = damage
        self.attack_range = attack_range
        self.cooldown = cooldown
        self.width = width
        self.height = height
        self.color = color
        self.name = name

        # Direction: friendly goes right (1), enemy goes left (-1) (assuming tower is on the left by default)
        # Note: direction is adjusted dynamically in game.py based on global settings.
        self.direction = 1 if team == "friendly" else -1

        self.state: UnitState = "walking"
        self.cooldown_timer = 0
        self.target: Any = None  # Can be Unit, Player, or Tower

        # Death and damage feedback
        self.death_timer = 0
        self.death_duration = 30  # 0.5s fadeout
        self.damage_flash_timer = 0
        
        # Animation variables
        self.walk_cycle = 0.0
        self.attack_anim_progress = 0.0  # From 0.0 to 1.0 during attack swing

    def get_rect(self) -> pygame.Rect:
        """Returns the bounding box of the unit for collision tests."""
        return pygame.Rect(
            int(self.x - self.width / 2),
            int(self.y - self.height),
            self.width,
            self.height
        )

    def take_damage(self, amount: float) -> bool:
        """Applies damage to the unit. Returns True if the unit died."""
        if self.state == "dying":
            return False
        
        self.health = max(0.0, self.health - amount)
        self.damage_flash_timer = 5  # Flash white for 5 frames
        
        if self.health <= 0:
            self.state = "dying"
            self.death_timer = self.death_duration
            return True
        return False

    def update(self, particles: Any) -> None:
        """Updates unit states, cooldowns, and coordinates."""
        if self.state == "dying":
            self.death_timer -= 1
            return

        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= 1

        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1

        # Combat state check
        if self.state == "combat":
            # If target is dead or no longer exists, return to walking
            if self.target is None or getattr(self.target, "health", 0) <= 0:
                self.state = "walking"
                self.target = None
                self.attack_anim_progress = 0.0
            else:
                self.update_combat(particles)
        elif self.state == "walking":
            self.update_walking(particles)

    def update_walking(self, particles: Any) -> None:
        """Moves the unit forward and updates walking animations."""
        self.x += self.speed * self.direction * 1.0
        self.walk_cycle += 0.15
        
        # Spawn subtle walking dust particles occasionally
        if particles and (pygame.time.get_ticks() % 10 == 0):
            particles.spawn_dust(self.x, self.y, amount=1)

    def update_combat(self, particles: Any) -> None:
        """Performs attack timer updates and actions."""
        # Attack animation swing progress
        if self.cooldown_timer > 0:
            # Settle animation back to rest
            self.attack_anim_progress = max(0.0, self.attack_anim_progress - 0.05)
        else:
            # We are ready to attack! Start the swing
            self.attack_anim_progress += 0.2
            if self.attack_anim_progress >= 1.0:
                self.perform_attack(particles)
                self.cooldown_timer = self.cooldown


    def perform_attack(self, particles: Any) -> None:
        """Deals damage to target. Overridden by Archers/Catapults for projectiles."""
        if self.target:
            self.target.take_damage(self.damage)
            if particles:
                # Spawn blood or spark particles at combat contact point
                contact_x = (self.x + self.target.x) / 2
                contact_y = self.y - self.height / 2
                particles.spawn_blood(contact_x, contact_y, amount=6)
                particles.spawn_sparks(contact_x, contact_y, amount=4)
            self.attack_anim_progress = 0.8  # bounce back after impact

    def draw(self, surface: pygame.Surface) -> None:
        """Draws the unit using vector primitives, health bar, and animations."""
        rect = self.get_rect()
        
        # Determine alpha and color override if dying/flashing
        color = self.color
        if self.damage_flash_timer > 0:
            color = (255, 255, 255)
            
        alpha = 255
        if self.state == "dying":
            alpha = int((self.death_timer / self.death_duration) * 255)

        # Create a surface for transparency support
        unit_surf = pygame.Surface((rect.width + 20, rect.height + 20), pygame.SRCALPHA)
        
        # Draw shadows (dark oval under feet)
        shadow_rect = pygame.Rect(10, rect.height + 5, rect.width, 6)
        pygame.draw.ellipse(unit_surf, (10, 10, 15, int(alpha * 0.4)), shadow_rect)

        # Core Unit shape (Body)
        # We will draw a stylish medieval warrior vector
        # Leg walking bounce
        bounce_y = 0.0
        if self.state == "walking":
            bounce_y = math.sin(self.walk_cycle) * 3
            
        body_y = 10 + bounce_y
        body_h = rect.height - 10
        body_rect = pygame.Rect(10, body_y, rect.width, body_h)
        
        # Draw the body with rounded edges
        pygame.draw.rect(unit_surf, (*color, alpha), body_rect, border_radius=4)
        
        # Draw details depending on team (team flag or chest color)
        team_color = (60, 200, 100) if self.team == "friendly" else (240, 50, 80)
        chest_rect = pygame.Rect(12, body_y + 12, rect.width - 4, 8)
        pygame.draw.rect(unit_surf, (*team_color, alpha), chest_rect)

        # Draw Head / Helmet
        head_radius = int(rect.width / 2.5)
        head_center = (10 + int(rect.width / 2), int(body_y + 2))
        pygame.draw.circle(unit_surf, (200, 170, 140, alpha), head_center, head_radius) # Skin
        # Helmet trim
        helmet_rect = pygame.Rect(10 + int(rect.width/2 - head_radius), int(body_y - head_radius + 2), head_radius * 2, head_radius)
        pygame.draw.rect(unit_surf, (150, 150, 160, alpha), helmet_rect, border_top_left_radius=4, border_top_right_radius=4)

        # Visual attack indicator (simple sword arm swing)
        if self.state == "combat":
            swing_dir = self.direction
            # Arm rotation representation
            arm_start = (10 + int(rect.width / 2), int(body_y + 15))
            angle = self.attack_anim_progress * math.pi / 2.5
            arm_length = 18
            arm_end = (
                arm_start[0] + swing_dir * math.cos(angle - 0.5) * arm_length,
                arm_start[1] - math.sin(angle - 0.5) * arm_length
            )
            pygame.draw.line(unit_surf, (220, 220, 230, alpha), arm_start, arm_end, 4) # Arm
            # Sword head
            sword_end = (
                arm_end[0] + swing_dir * math.cos(angle + 0.5) * 12,
                arm_end[1] - math.sin(angle + 0.5) * 12
            )
            pygame.draw.line(unit_surf, (240, 240, 255, alpha), arm_end, sword_end, 3) # Blade

        # Blit the unit surface to main surface
        surface.blit(unit_surf, (rect.left - 10, rect.top - 10))

        # Health bar (if alive and not fully healthy)
        if self.state != "dying" and self.health < self.max_health:
            bar_w = rect.width + 10
            bar_h = 4
            bar_x = rect.left - 5
            bar_y = rect.top - 10
            
            # Background
            pygame.draw.rect(surface, COLOR_HEALTH_BAR_BG, (bar_x, bar_y, bar_w, bar_h))
            # Fill
            fill_w = int(bar_w * (self.health / self.max_health))
            pygame.draw.rect(surface, COLOR_HEALTH_BAR_FILL, (bar_x, bar_y, fill_w, bar_h))
