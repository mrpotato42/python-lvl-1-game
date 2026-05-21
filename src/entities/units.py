"""Specialized troop units (Warrior, Archer, Knight, Catapult) in Arrow Defense."""

from __future__ import annotations
import pygame
import math
import random
from typing import Literal, Any
from src.config import (
    STATS_WARRIOR, STATS_ARCHER, STATS_KNIGHT, STATS_CATAPULT,
    GRAVITY, GROUND_Y, COLOR_HEALTH_BAR_BG, COLOR_HEALTH_BAR_FILL
)
from src.entities.base_unit import Unit
from src.entities.projectile import Projectile

class Warrior(Unit):
    """Melee infantry unit: balanced health, speed, and attack power."""
    
    def __init__(self, x: float, team: Literal["friendly", "enemy"]) -> None:
        stats = STATS_WARRIOR
        super().__init__(
            x=x,
            team=team,
            max_health=stats.max_health,
            speed=stats.speed,
            damage=stats.damage,
            attack_range=stats.attack_range,
            cooldown=stats.cooldown,
            width=stats.width,
            height=stats.height,
            color=stats.color,
            name=stats.name,
        )

    def draw(self, surface: pygame.Surface) -> None:
        # We can inherit base draw, which draws a standard warrior with a sword.
        super().draw(surface)


class Knight(Unit):
    """Heavy melee unit with high health, high damage, but slow speed.

    Takes reduced damage due to armor.
    """

    def __init__(self, x: float, team: Literal["friendly", "enemy"]) -> None:
        stats = STATS_KNIGHT
        super().__init__(
            x=x,
            team=team,
            max_health=stats.max_health,
            speed=stats.speed,
            damage=stats.damage,
            attack_range=stats.attack_range,
            cooldown=stats.cooldown,
            width=stats.width,
            height=stats.height,
            color=stats.color,
            name=stats.name,
        )
        self.armor_absorption = 0.35  # Takes 35% less damage

    def take_damage(self, amount: float) -> bool:
        # Apply armor reduction
        reduced_damage = amount * (1.0 - self.armor_absorption)
        return super().take_damage(reduced_damage)

    def draw(self, surface: pygame.Surface) -> None:
        """Draws a heavily armored Knight with a steel helmet, chestplate, and shield."""
        rect = self.get_rect()
        color = self.color
        if self.damage_flash_timer > 0:
            color = (255, 255, 255)
            
        alpha = 255
        if self.state == "dying":
            alpha = int((self.death_timer / self.death_duration) * 255)

        unit_surf = pygame.Surface((rect.width + 20, rect.height + 20), pygame.SRCALPHA)
        
        # Shadow
        shadow_rect = pygame.Rect(10, rect.height + 5, rect.width, 6)
        pygame.draw.ellipse(unit_surf, (10, 10, 15, int(alpha * 0.4)), shadow_rect)

        # Body - Knight is bulkier
        bounce_y = 0.0
        if self.state == "walking":
            bounce_y = math.sin(self.walk_cycle) * 2
            
        body_y = 10 + bounce_y
        body_h = rect.height - 10
        body_rect = pygame.Rect(10, body_y, rect.width, body_h)
        
        # Draw shiny iron armor
        pygame.draw.rect(unit_surf, (*color, alpha), body_rect, border_radius=5)
        # Gold/yellow trim
        trim_color = (210, 180, 40)
        pygame.draw.rect(unit_surf, (*trim_color, alpha), pygame.Rect(10, body_y + 10, rect.width, 4))

        # Head / Steel Helmet
        head_radius = int(rect.width / 2.3)
        head_center = (10 + int(rect.width / 2), int(body_y + 2))
        pygame.draw.circle(unit_surf, (120, 120, 130, alpha), head_center, head_radius)
        # Helmet plume (red feather on top)
        plume_color = (230, 40, 40)
        pygame.draw.circle(unit_surf, (*plume_color, alpha), (head_center[0], head_center[1] - head_radius - 2), 4)
        
        # Shield (drawn in front of the knight)
        shield_dir = self.direction
        shield_w = 12
        shield_h = 22
        shield_x = 10 + (rect.width // 2) + shield_dir * (rect.width // 2 - 4) - (shield_w // 2)
        shield_y = body_y + 12
        shield_rect = pygame.Rect(shield_x, shield_y, shield_w, shield_h)
        
        # Draw wooden/steel shield with cross emblem
        pygame.draw.rect(unit_surf, (80, 80, 90, alpha), shield_rect, border_radius=3)
        emblem_color = (190, 30, 30) if self.team == "enemy" else (30, 120, 190)
        # Cross on shield
        pygame.draw.line(unit_surf, (*emblem_color, alpha), (shield_x + shield_w // 2, shield_y + 3), (shield_x + shield_w // 2, shield_y + shield_h - 3), 2)
        pygame.draw.line(unit_surf, (*emblem_color, alpha), (shield_x + 2, shield_y + shield_h // 2), (shield_x + shield_w - 2, shield_y + shield_h // 2), 2)

        # Sword hand if fighting
        if self.state == "combat":
            swing_dir = self.direction
            arm_start = (10 + int(rect.width / 2) - swing_dir * 4, int(body_y + 14))
            angle = self.attack_anim_progress * math.pi / 2.5
            arm_length = 16
            arm_end = (
                arm_start[0] + swing_dir * math.cos(angle - 0.2) * arm_length,
                arm_start[1] - math.sin(angle - 0.2) * arm_length
            )
            pygame.draw.line(unit_surf, (100, 100, 110, alpha), arm_start, arm_end, 4)
            # Big heavy sword
            sword_end = (
                arm_end[0] + swing_dir * math.cos(angle + 0.4) * 16,
                arm_end[1] - math.sin(angle + 0.4) * 16
            )
            pygame.draw.line(unit_surf, (240, 240, 250, alpha), arm_end, sword_end, 4)

        surface.blit(unit_surf, (rect.left - 10, rect.top - 10))

        # Health bar
        if self.state != "dying" and self.health < self.max_health:
            bar_w = rect.width + 10
            bar_h = 4
            bar_x = rect.left - 5
            bar_y = rect.top - 10
            pygame.draw.rect(surface, COLOR_HEALTH_BAR_BG, (bar_x, bar_y, bar_w, bar_h))
            fill_w = int(bar_w * (self.health / self.max_health))
            pygame.draw.rect(surface, COLOR_HEALTH_BAR_FILL, (bar_x, bar_y, fill_w, bar_h))


class Archer(Unit):
    """Ranged unit: shoots arrows using parabolic trajectory calculation.

    Fires projectile towards target.
    """

    def __init__(self, x: float, team: Literal["friendly", "enemy"]) -> None:
        stats = STATS_ARCHER
        super().__init__(
            x=x,
            team=team,
            max_health=stats.max_health,
            speed=stats.speed,
            damage=stats.damage,
            attack_range=stats.attack_range,
            cooldown=stats.cooldown,
            width=stats.width,
            height=stats.height,
            color=stats.color,
            name=stats.name,
        )
        self.projectiles_to_spawn: list[Projectile] = []

    def perform_attack(self, particles: Any) -> None:
        """Overrides melee attack to fire a parabolic arrow instead."""
        if not self.target:
            return

        # Archer shoots an arrow.
        # Launch point is near the shoulder/bow position
        launch_x = self.x + self.direction * (self.width / 2)
        launch_y = self.y - self.height + 15
        
        # Calculate target point: center-height of the target unit, or top of tower
        # Add a bit of random offset to make arrows look natural and miss sometimes
        spread_x = random.uniform(-15.0, 15.0)
        target_x = self.target.x + spread_x
        
        # Target Y depends on if target is a tower, unit, or player
        if hasattr(self.target, "height"):
            target_y = self.target.y - self.target.height / 2
        else:
            # Tower / general entity
            target_y = self.target.y + 100 # target higher up the tower body

        # Horizontal travel time (t) in frames. Let's base it on distance.
        dist_x = abs(target_x - launch_x)
        # Base horizontal speed
        h_speed = 6.5
        t = dist_x / h_speed
        if t < 10:
            t = 10
            
        vx = (target_x - launch_x) / t
        
        # Vy calculation using kinematic formula: y = y0 + vy*t + 0.5*g*t^2
        # Solving for vy: vy = (y - y0 - 0.5*g*t^2) / t
        vy = (target_y - launch_y - 0.5 * GRAVITY * (t ** 2)) / t

        # Create arrow projectile
        arrow = Projectile(
            x=launch_x,
            y=launch_y,
            vx=vx,
            vy=vy,
            gravity=GRAVITY,
            damage=self.damage,
            team=self.team,
            proj_type="arrow",
            launcher=self,
        )
        self.projectiles_to_spawn.append(arrow)
        self.attack_anim_progress = 0.5  # bow recoil

    def draw(self, surface: pygame.Surface) -> None:
        """Draws an Archer in green/forest clothing holding a wooden bow."""
        rect = self.get_rect()
        color = self.color
        if self.damage_flash_timer > 0:
            color = (255, 255, 255)
            
        alpha = 255
        if self.state == "dying":
            alpha = int((self.death_timer / self.death_duration) * 255)

        unit_surf = pygame.Surface((rect.width + 20, rect.height + 20), pygame.SRCALPHA)
        
        # Shadow
        shadow_rect = pygame.Rect(10, rect.height + 5, rect.width, 6)
        pygame.draw.ellipse(unit_surf, (10, 10, 15, int(alpha * 0.4)), shadow_rect)

        # Body (slender)
        bounce_y = 0.0
        if self.state == "walking":
            bounce_y = math.sin(self.walk_cycle) * 3
            
        body_y = 10 + bounce_y
        body_h = rect.height - 10
        body_rect = pygame.Rect(10, body_y, rect.width, body_h)
        
        pygame.draw.rect(unit_surf, (*color, alpha), body_rect, border_radius=3)

        # Leather quiver on back
        quiver_rect = pygame.Rect(6, body_y + 10, 5, 14)
        pygame.draw.rect(unit_surf, (120, 80, 40, alpha), quiver_rect)
        # Small arrows in quiver
        pygame.draw.line(unit_surf, (240, 240, 240, alpha), (8, body_y + 10), (8, body_y + 5), 2)

        # Head / Hood
        head_radius = int(rect.width / 2.4)
        head_center = (10 + int(rect.width / 2), int(body_y + 2))
        pygame.draw.circle(unit_surf, (200, 170, 140, alpha), head_center, head_radius)
        # Hood overlay (green)
        pygame.draw.circle(unit_surf, (*color, alpha), (head_center[0], head_center[1] - 1), head_radius + 1, draw_top_left=True, draw_top_right=True)

        # Bow (weapon)
        bow_dir = self.direction
        bow_x = 10 + (rect.width // 2) + bow_dir * (rect.width // 2 + 1)
        bow_y = body_y + 16
        
        # If in combat, bow is drawn
        if self.state == "combat":
            # Curved bow arc
            bow_rect = pygame.Rect(bow_x - 3 if bow_dir > 0 else bow_x - 5, bow_y - 12, 8, 24)
            # Draw bow wood
            pygame.draw.arc(unit_surf, (130, 90, 50, alpha), bow_rect, -math.pi/2, math.pi/2 if bow_dir > 0 else 3*math.pi/2, 2)
            # String (drawn pulled back)
            pull_offset = -5 if bow_dir > 0 else 5
            string_center = (bow_x + pull_offset, bow_y)
            pygame.draw.line(unit_surf, (220, 220, 220, alpha), (bow_x, bow_y - 10), string_center, 1)
            pygame.draw.line(unit_surf, (220, 220, 220, alpha), string_center, (bow_x, bow_y + 10), 1)
        else:
            # Carry bow on shoulder/back
            pygame.draw.line(unit_surf, (130, 90, 50, alpha), (10, body_y + 6), (10 + rect.width, body_y + 18), 2)

        surface.blit(unit_surf, (rect.left - 10, rect.top - 10))

        # Health bar
        if self.state != "dying" and self.health < self.max_health:
            bar_w = rect.width + 10
            bar_h = 4
            bar_x = rect.left - 5
            bar_y = rect.top - 10
            pygame.draw.rect(surface, COLOR_HEALTH_BAR_BG, (bar_x, bar_y, bar_w, bar_h))
            fill_w = int(bar_w * (self.health / self.max_health))
            pygame.draw.rect(surface, COLOR_HEALTH_BAR_FILL, (bar_x, bar_y, fill_w, bar_h))


class Catapult(Unit):
    """Slow, heavy vehicle that fires large stone boulders causing AoE splash damage."""

    def __init__(self, x: float, team: Literal["friendly", "enemy"]) -> None:
        stats = STATS_CATAPULT
        super().__init__(
            x=x,
            team=team,
            max_health=stats.max_health,
            speed=stats.speed,
            damage=stats.damage,
            attack_range=stats.attack_range,
            cooldown=stats.cooldown,
            width=stats.width,
            height=stats.height,
            color=stats.color,
            name=stats.name,
        )
        self.projectiles_to_spawn: list[Projectile] = []

    def perform_attack(self, particles: Any) -> None:
        """Launches a massive boulder along a high arc."""
        if not self.target:
            return

        # Catapult launches a stone boulder.
        # Launch point is the tip of the throwing arm
        arm_dir = self.direction
        launch_x = self.x + arm_dir * 10
        launch_y = self.y - self.height + 10

        target_x = self.target.x + random.uniform(-25.0, 25.0)  # less accurate
        if hasattr(self.target, "height"):
            target_y = self.target.y - 10
        else:
            target_y = self.target.y + 150

        # Slow lob: Horizontal travel time (t) in frames.
        dist_x = abs(target_x - launch_x)
        # Slow horizontal speed makes a high satisfying lob
        h_speed = 4.0
        t = dist_x / h_speed
        if t < 20:
            t = 20
            
        vx = (target_x - launch_x) / t
        vy = (target_y - launch_y - 0.5 * GRAVITY * (t ** 2)) / t

        boulder = Projectile(
            x=launch_x,
            y=launch_y,
            vx=vx,
            vy=vy,
            gravity=GRAVITY,
            damage=self.damage,
            team=self.team,
            proj_type="boulder",
            launcher=self,
        )
        self.projectiles_to_spawn.append(boulder)
        self.attack_anim_progress = 1.0  # arm flicked forward

    def draw(self, surface: pygame.Surface) -> None:
        """Draws a mechanical wooden catapult on wheels with a tension arm."""
        rect = self.get_rect()
        color = self.color
        if self.damage_flash_timer > 0:
            color = (255, 255, 255)
            
        alpha = 255
        if self.state == "dying":
            alpha = int((self.death_timer / self.death_duration) * 255)

        unit_surf = pygame.Surface((rect.width + 20, rect.height + 20), pygame.SRCALPHA)
        
        # Shadow
        shadow_rect = pygame.Rect(10, rect.height + 5, rect.width, 8)
        pygame.draw.ellipse(unit_surf, (10, 10, 15, int(alpha * 0.45)), shadow_rect)

        # Catapult Base (wooden frame)
        base_h = 14
        base_y = rect.height - base_h
        base_rect = pygame.Rect(10, base_y, rect.width, base_h)
        pygame.draw.rect(unit_surf, (*color, alpha), base_rect, border_radius=2)
        # Iron bands on frame
        pygame.draw.rect(unit_surf, (70, 70, 75, alpha), pygame.Rect(20, base_y, 4, base_h))
        pygame.draw.rect(unit_surf, (70, 70, 75, alpha), pygame.Rect(10 + rect.width - 14, base_y, 4, base_h))

        # Wheels (two large circular wheels)
        wheel_radius = 8
        wheel_y = rect.height + 2
        # Front Wheel
        pygame.draw.circle(unit_surf, (30, 30, 35, alpha), (22, wheel_y), wheel_radius)
        pygame.draw.circle(unit_surf, (130, 90, 50, alpha), (22, wheel_y), wheel_radius - 2)
        pygame.draw.circle(unit_surf, (60, 60, 65, alpha), (22, wheel_y), 2)
        # Rear Wheel
        pygame.draw.circle(unit_surf, (30, 30, 35, alpha), (10 + rect.width - 12, wheel_y), wheel_radius)
        pygame.draw.circle(unit_surf, (130, 90, 50, alpha), (10 + rect.width - 12, wheel_y), wheel_radius - 2)
        pygame.draw.circle(unit_surf, (60, 60, 65, alpha), (10 + rect.width - 12, wheel_y), 2)

        # Tension Uprights (vertical structural supports)
        upright_w = 6
        upright_h = rect.height - base_h - 10
        upright_x = 10 + rect.width // 2 - upright_w // 2
        pygame.draw.rect(unit_surf, (*color, alpha), pygame.Rect(upright_x, base_y - upright_h, upright_w, upright_h))

        # Throwing Arm & Cup
        # The throwing arm rotates based on attack progress
        arm_dir = self.direction
        arm_base_x = upright_x + upright_w // 2
        arm_base_y = base_y - 2
        
        # Calculate angle of the throwing arm
        if self.state == "combat":
            # Pulling back: 0.0 -> 0.7, Firing flick: 0.7 -> 1.0
            if self.attack_anim_progress < 0.7:
                # Arm is pulled back (leaning backwards)
                angle = -arm_dir * (0.2 + (self.attack_anim_progress / 0.7) * 0.6)
            else:
                # Arm is released/flicking forward (leaning forwards)
                ratio = (self.attack_anim_progress - 0.7) / 0.3
                angle = arm_dir * (-0.8 + ratio * 1.4)
        else:
            # Idle/Walking position (slightly leaning back)
            angle = -arm_dir * 0.3

        # Draw arm line
        arm_len = rect.height - 12
        arm_tip_x = arm_base_x + math.sin(angle) * arm_len
        arm_tip_y = arm_base_y - math.cos(angle) * arm_len
        pygame.draw.line(unit_surf, (100, 60, 30, alpha), (arm_base_x, arm_base_y), (arm_tip_x, arm_tip_y), 4)

        # Draw Cup at the end of the arm
        cup_r = 6
        pygame.draw.circle(unit_surf, (50, 50, 55, alpha), (int(arm_tip_x), int(arm_tip_y)), cup_r)
        pygame.draw.circle(unit_surf, (100, 60, 30, alpha), (int(arm_tip_x), int(arm_tip_y)), cup_r - 2)

        # Draw Boulder in the cup if loading (cooldown timer is low, or state is walking, or drawing before flick)
        # Catapult has boulder inside cup except when just fired
        if self.state != "combat" or self.attack_anim_progress < 0.8:
            pygame.draw.circle(unit_surf, (110, 110, 120, alpha), (int(arm_tip_x), int(arm_tip_y - 3)), 4)

        surface.blit(unit_surf, (rect.left - 10, rect.top - 10))

        # Health bar
        if self.state != "dying" and self.health < self.max_health:
            bar_w = rect.width + 10
            bar_h = 4
            bar_x = rect.left - 5
            bar_y = rect.top - 10
            pygame.draw.rect(surface, COLOR_HEALTH_BAR_BG, (bar_x, bar_y, bar_w, bar_h))
            fill_w = int(bar_w * (self.health / self.max_health))
            pygame.draw.rect(surface, COLOR_HEALTH_BAR_FILL, (bar_x, bar_y, fill_w, bar_h))
