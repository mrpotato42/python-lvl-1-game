"""Particle system for visual effects like blood, dust, sparks, trails, and explosions."""

import random
import pygame
from typing import Literal

# Particle Types
ParticleType = Literal["blood", "dust", "spark", "trail", "explosion"]

class Particle:
    """Represents a single visual particle in the system."""
    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        color: tuple[int, int, int],
        life: int,
        size: float,
        gravity: float = 0.0,
        fade_speed: float = 1.0,
    ) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.max_life = life
        self.life = life
        self.size = size
        self.gravity = gravity
        self.fade_speed = fade_speed

    def update(self) -> bool:
        """Updates the particle physics. Returns False if the particle is dead."""
        self.x += self.vx
        self.vy += self.gravity
        self.y += self.vy
        self.life -= 1
        return self.life > 0

    def draw(self, surface: pygame.Surface) -> None:
        """Draws the particle onto the surface with transparency based on life."""
        if self.life <= 0:
            return

        alpha = int((self.life / self.max_life) * 255)
        # Create a temporary surface to draw transparent shapes if needed
        # Or draw directly for speed with small sizes.
        size = max(1.0, self.size * (self.life / self.max_life))
        
        # Draw soft glowing circles for larger particles or quick rectangles/circles for small ones
        if size > 3:
            s = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (int(size), int(size)), int(size))
            surface.blit(s, (int(self.x - size), int(self.y - size)))
        else:
            # Quick direct circle
            try:
                # Color blending by hand or draw circle directly
                pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(size))
            except TypeError:
                pass


class ParticleSystem:
    """Manages active particles, updating and drawing them."""
    def __init__(self) -> None:
        self.particles: list[Particle] = []

    def clear(self) -> None:
        """Clears all active particles."""
        self.particles.clear()

    def update(self) -> None:
        """Updates all active particles and removes dead ones."""
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, surface: pygame.Surface) -> None:
        """Draws all active particles."""
        for p in self.particles:
            p.draw(surface)

    def spawn_blood(self, x: float, y: float, amount: int = 8) -> None:
        """Spawns red blood spray particles."""
        for _ in range(amount):
            vx = random.uniform(-2.0, 2.0)
            vy = random.uniform(-4.0, -1.0)
            life = random.randint(15, 30)
            size = random.uniform(2.0, 4.0)
            color = (random.randint(160, 220), random.randint(10, 30), random.randint(20, 40))
            self.particles.append(Particle(x, y, vx, vy, color, life, size, gravity=0.2))

    def spawn_dust(self, x: float, y: float, amount: int = 5) -> None:
        """Spawns gray dust particles when moving or walking."""
        for _ in range(amount):
            vx = random.uniform(-0.8, 0.8)
            vy = random.uniform(-0.5, -0.1)
            life = random.randint(20, 40)
            size = random.uniform(3.0, 6.0)
            color = (random.randint(90, 110), random.randint(90, 110), random.randint(95, 115))
            self.particles.append(Particle(x, y, vx, vy, color, life, size, gravity=-0.02))

    def spawn_sparks(self, x: float, y: float, amount: int = 6) -> None:
        """Spawns bright sparks for metal clashes."""
        for _ in range(amount):
            vx = random.uniform(-3.0, 3.0)
            vy = random.uniform(-3.0, 1.0)
            life = random.randint(10, 20)
            size = random.uniform(1.5, 3.0)
            color = (255, random.randint(180, 255), 100)
            self.particles.append(Particle(x, y, vx, vy, color, life, size, gravity=0.15))

    def spawn_trail(self, x: float, y: float, color: tuple[int, int, int], size: float = 2.0) -> None:
        """Spawns a fading trail particle behind a projectile."""
        # Trail particles have 0 velocity and just fade in place
        self.particles.append(Particle(x, y, 0.0, 0.0, color, 12, size, gravity=0.0))

    def spawn_explosion(self, x: float, y: float, radius: float) -> None:
        """Spawns an explosive flash with flying debris and smoke."""
        # Central flash
        for _ in range(12):
            vx = random.uniform(-4.0, 4.0)
            vy = random.uniform(-4.0, 4.0)
            life = random.randint(15, 25)
            size = random.uniform(5.0, 15.0)
            color = (255, random.randint(100, 180), random.randint(0, 50))
            self.particles.append(Particle(x, y, vx, vy, color, life, size, gravity=0.05))
        
        # Smoke cloud
        for _ in range(15):
            vx = random.uniform(-2.0, 2.0)
            vy = random.uniform(-3.0, 0.0)
            life = random.randint(30, 50)
            size = random.uniform(8.0, 20.0)
            color = (random.randint(60, 80), random.randint(60, 80), random.randint(65, 85))
            self.particles.append(Particle(x, y, vx, vy, color, life, size, gravity=-0.05))

        # Spark showers
        for _ in range(20):
            vx = random.uniform(-6.0, 6.0)
            vy = random.uniform(-6.0, -1.0)
            life = random.randint(15, 35)
            size = random.uniform(1.5, 3.0)
            color = (255, random.randint(180, 255), 50)
            self.particles.append(Particle(x, y, vx, vy, color, life, size, gravity=0.25))
