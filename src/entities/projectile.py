"""Projectile class handling arrows and catapult stones in Arrow Defense."""

from __future__ import annotations
import pygame
import math
from typing import Literal, Any
from src.config import COLOR_WHITE, COLOR_CATAPULT, GROUND_Y
from src.physics.collision import check_rect_collision, check_circle_collision

ProjectileType = Literal["arrow", "boulder"]

class Projectile:
    """Represents a flying projectile with gravity, rendering, and collision."""

    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        gravity: float,
        damage: float,
        team: Literal["friendly", "enemy"],
        proj_type: ProjectileType,
        launcher: Any = None,
    ) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.gravity = gravity
        self.damage = damage
        self.team = team
        self.type: ProjectileType = proj_type
        self.launcher = launcher
        self.is_dead = False

        # Visual and collision configurations
        if self.type == "arrow":
            self.radius = 2.0
            self.color = COLOR_WHITE
            self.trail_color = (200, 200, 255)
        else:  # boulder
            self.radius = 8.0
            self.color = COLOR_CATAPULT
            self.trail_color = (130, 80, 40)
            self.aoe_radius = 80.0  # Area-of-effect splash damage radius

        # Prevent instant self-hits
        self.lifetime_ticks = 0

    def update(self, units: list[Any], tower: Any, particles: Any) -> None:
        """Updates physics coordinates and checks collisions."""
        self.lifetime_ticks += 1
        
        # Apply physics
        self.x += self.vx
        self.vy += self.gravity
        self.y += self.vy

        # Spawn flight trail particles
        if particles and self.lifetime_ticks % 2 == 0:
            particles.spawn_trail(self.x, self.y, self.trail_color, size=2.0 if self.type == "arrow" else 5.0)

        # Ground impact check
        if self.y >= GROUND_Y:
            self.y = float(GROUND_Y)
            self.handle_impact(units, tower, particles)
            return

        # Collision check with units (Friendly Fire is ACTIVE!)
        # Any projectile can hit any unit, but we exclude the launcher for the first few ticks.
        for unit in units:
            if unit.state == "dying":
                continue
            
            # Avoid hitting the unit that fired it immediately after spawn
            if unit == self.launcher and self.lifetime_ticks < 10:
                continue

            rect = unit.get_rect()
            # We treat the projectile as a small circle.
            # Check if circle overlaps with unit rect
            hit = check_circle_collision(self.x, self.y, self.radius, rect.x, rect.y, rect.width, rect.height)
            
            if hit:
                self.handle_impact(units, tower, particles, target_hit=unit)
                return

        # Collision with Tower (only enemy projectiles can hit player's tower, or maybe anything can hit it,
        # but let's make it so only enemy projectiles damage the friendly tower for gameplay balance. Or friendly fire applies to tower too?
        # Let's say enemy projectiles damage player tower, and player's own projectiles do not damage their tower to be fair, 
        # or maybe they do? "Fuego Aliado: Los proyectiles pueden dañar a tus propias tropas" - says troops, not tower, 
        # so let's check: only enemy projectiles damage player tower.
        if self.team == "enemy" and tower:
            tower_rect = tower.get_rect()
            if check_circle_collision(self.x, self.y, self.radius, tower_rect.x, tower_rect.y, tower_rect.width, tower_rect.height):
                self.handle_impact(units, tower, particles, target_hit=tower)
                return

    def handle_impact(
        self,
        units: list[Any],
        tower: Any,
        particles: Any,
        target_hit: Any = None,
    ) -> None:
        """Deals damage upon collision and spawns visual effects."""
        self.is_dead = True

        if self.type == "arrow":
            # Direct hit
            if target_hit:
                target_hit.take_damage(self.damage)
                if particles:
                    particles.spawn_blood(self.x, self.y, amount=8)
            else:
                # Hit ground, spawn dust sparks
                if particles:
                    particles.spawn_dust(self.x, self.y, amount=4)
        
        elif self.type == "boulder":
            # Catapult boulder hits ground/target, cause AoE explosion
            if particles:
                particles.spawn_explosion(self.x, self.y, self.aoe_radius)

            # Apply area damage to all entities within distance
            # Splash damage is linear decay based on distance from epicenter
            for unit in units:
                if unit.state == "dying":
                    continue
                dist = math.sqrt((unit.x - self.x) ** 2 + ((unit.y - unit.height / 2) - self.y) ** 2)
                if dist < self.aoe_radius:
                    # Scale damage based on distance: full damage at center, zero at edge
                    damage_scale = 1.0 - (dist / self.aoe_radius)
                    actual_damage = self.damage * damage_scale
                    unit.take_damage(actual_damage)
                    if particles and actual_damage > 10:
                        particles.spawn_blood(unit.x, unit.y - unit.height / 2, amount=4)

            # Check if player tower is in splash radius (if team of projectile is enemy)
            if self.team == "enemy" and tower:
                t_rect = tower.get_rect()
                t_center_x = t_rect.x + t_rect.width / 2
                t_center_y = t_rect.y + t_rect.height / 2
                dist = math.sqrt((t_center_x - self.x) ** 2 + (t_center_y - self.y) ** 2)
                if dist < self.aoe_radius:
                    damage_scale = 1.0 - (dist / self.aoe_radius)
                    tower.take_damage(self.damage * damage_scale)

    def draw(self, surface: pygame.Surface) -> None:
        """Draws the projectile with rotation matching its velocity vector."""
        if self.is_dead:
            return

        if self.type == "arrow":
            # Calculate angle of flight based on velocity
            angle = math.atan2(-self.vy, self.vx)
            arrow_length = 20
            
            # Start and end coordinates
            start_x = self.x - math.cos(angle) * (arrow_length / 2)
            start_y = self.y + math.sin(angle) * (arrow_length / 2)
            end_x = self.x + math.cos(angle) * (arrow_length / 2)
            end_y = self.y - math.sin(angle) * (arrow_length / 2)

            # Draw shaft
            pygame.draw.line(surface, self.color, (start_x, start_y), (end_x, end_y), 2)
            
            # Draw fletching (feathers)
            fletch_x = start_x - math.cos(angle) * 3
            fletch_y = start_y + math.sin(angle) * 3
            pygame.draw.circle(surface, (230, 70, 70), (int(fletch_x), int(fletch_y)), 3)

        elif self.type == "boulder":
            # Draw a boulder with shaded vector circles
            # Main circle
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius))
            # Highlight shadow texture
            pygame.draw.circle(surface, (140, 85, 35), (int(self.x - 2), int(self.y - 2)), int(self.radius - 2))
            pygame.draw.circle(surface, (80, 50, 20), (int(self.x + 3), int(self.y + 3)), 3)
