"""Main Game manager containing the core loop, wave spawning, and collision checks."""

from __future__ import annotations
import pygame
import random
import sys
from typing import Literal, Any
import src.config as cfg
from src.entities.player import Player
from src.entities.tower import Tower
from src.entities.base_unit import Unit
from src.entities.units import Warrior, Archer, Knight, Catapult
from src.entities.projectile import Projectile
from src.utils.particles import ParticleSystem
from src.ui.hud import HUD
from src.ui.menu import Menu
from src.physics.collision import distance

GameState = Literal["main_menu", "playing", "paused", "victory", "game_over"]

class Game:
    """Coordinates gameplay loops, updating pools of entities, and screen blits."""

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.clock = pygame.Clock()
        self.state: GameState = "main_menu"
        self.running = True
        
        # Core game entities
        self.player = Player()
        self.tower = Tower()
        self.units: list[Unit] = []
        self.projectiles: list[Projectile] = []
        self.particles = ParticleSystem()
        
        # UI overlays
        self.hud = HUD()
        self.menu = Menu()
        
        # Game State stats
        self.gold = cfg.INITIAL_WAVE_GOLD
        self.wave = 0
        self.wave_active = False
        
        # Wave spawner variables
        self.enemies_to_spawn: list[str] = []
        self.spawn_timer = 0
        self.spawn_cooldown = 120  # Spawn an enemy every 2 seconds
        self.next_wave_timer = 300  # Countdown time between waves (5s)
        self.next_wave_timer_max = 300
        
        # Total enemies spawned in current wave (waiting to spawn + currently alive)
        self.enemies_remaining = 0

        # Screen Shake effect
        self.shake_intensity = 0.0
        
        # Tracking earned gold list to avoid multiple rewards for the same unit
        self.dead_rewarded_units: set[Unit] = set()

    def reset_game(self) -> None:
        """Resets the game state back to wave 1."""
        self.player = Player()
        self.tower = Tower()
        self.units.clear()
        self.projectiles.clear()
        self.particles.clear()
        self.gold = cfg.INITIAL_WAVE_GOLD
        self.wave = 0
        self.wave_active = False
        self.enemies_to_spawn.clear()
        self.spawn_timer = 0
        self.next_wave_timer = 180  # 3 seconds for the very first wave
        self.next_wave_timer_max = 180
        self.enemies_remaining = 0
        self.shake_intensity = 0.0
        self.dead_rewarded_units.clear()
        self.state = "playing"

    def handle_side_toggle(self) -> None:
        """Toggles the side of the player tower."""
        if cfg.TOWER_SIDE == "left":
            cfg.TOWER_SIDE = "right"
        else:
            cfg.TOWER_SIDE = "left"
        cfg.TOWER_BALCONY_Y = cfg.SCREEN_HEIGHT - cfg.TOWER_HEIGHT

    def spawn_wave(self) -> None:
        """Fills the queue of enemies based on the wave number."""
        self.wave += 1
        self.wave_active = True
        self.spawn_timer = 0
        self.dead_rewarded_units.clear()
        
        # Define composition based on wave
        # Wave 1: basic warriors
        # Wave 2: warriors + archers
        # Wave 3: introduces knights
        # Wave 4: introduces catapults
        # Wave 5+: random scaling compositions
        if self.wave == 1:
            self.enemies_to_spawn = ["Warrior"] * 3
        elif self.wave == 2:
            self.enemies_to_spawn = ["Warrior", "Warrior", "Archer", "Warrior"]
        elif self.wave == 3:
            self.enemies_to_spawn = ["Warrior", "Knight", "Archer", "Warrior", "Archer"]
        elif self.wave == 4:
            self.enemies_to_spawn = ["Warrior", "Knight", "Archer", "Catapult", "Knight", "Warrior"]
        else:
            # Scaled wave composition
            warriors = random.randint(2, 4 + self.wave // 2)
            archers = random.randint(1, 3 + self.wave // 3)
            knights = random.randint(1, 1 + self.wave // 4)
            catapults = 1 if self.wave % 2 == 0 or self.wave >= 8 else 0
            
            self.enemies_to_spawn = (
                ["Warrior"] * warriors +
                ["Archer"] * archers +
                ["Knight"] * knights +
                ["Catapult"] * catapults
            )
            # Shuffle so they arrive in random order
            random.shuffle(self.enemies_to_spawn)
            
        self.enemies_remaining = len(self.enemies_to_spawn)

    def spawn_ally(self, troop_type: str) -> None:
        """Deducts gold and spawns a friendly unit at the tower's base."""
        # Find stats
        if troop_type == "Warrior":
            stats = cfg.STATS_WARRIOR
            unit_class = Warrior
        elif troop_type == "Archer":
            stats = cfg.STATS_ARCHER
            unit_class = Archer
        elif troop_type == "Knight":
            stats = cfg.STATS_KNIGHT
            unit_class = Knight
        elif troop_type == "Catapult":
            stats = cfg.STATS_CATAPULT
            unit_class = Catapult
        else:
            return

        if self.gold >= stats.cost:
            self.gold -= stats.cost
            
            # Spawn at the tower gate on the ground
            if cfg.TOWER_SIDE == "left":
                spawn_x = float(cfg.TOWER_WIDTH - 20)
            else:
                spawn_x = float(cfg.SCREEN_WIDTH - cfg.TOWER_WIDTH + 20)
                
            new_unit = unit_class(spawn_x, "friendly")
            # Set direct direction matching tower side
            new_unit.direction = 1 if cfg.TOWER_SIDE == "left" else -1
            self.units.append(new_unit)
            
            # Spawn summon spark effect
            self.particles.spawn_sparks(spawn_x, cfg.GROUND_Y - 20, amount=8)

    def spawn_enemy(self, troop_type: str) -> None:
        """Spawns an enemy unit at the opposite edge of the map."""
        if cfg.TOWER_SIDE == "left":
            # Spawn off-screen to the right
            spawn_x = float(cfg.SCREEN_WIDTH + 30)
        else:
            # Spawn off-screen to the left
            spawn_x = -30.0

        if troop_type == "Warrior":
            enemy = Warrior(spawn_x, "enemy")
        elif troop_type == "Archer":
            enemy = Archer(spawn_x, "enemy")
        elif troop_type == "Knight":
            enemy = Knight(spawn_x, "enemy")
        elif troop_type == "Catapult":
            enemy = Catapult(spawn_x, "enemy")
        else:
            return

        # Direction of enemy is towards the tower
        enemy.direction = -1 if cfg.TOWER_SIDE == "left" else 1
        self.units.append(enemy)

    def handle_events(self) -> None:
        """Processes keystrokes and game actions."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                if self.state == "main_menu":
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        self.reset_game()
                    elif event.key == pygame.K_t:
                        self.handle_side_toggle()
                        
                elif self.state == "playing":
                    if event.key == pygame.K_ESCAPE:
                        self.state = "paused"
                    # Spawn keys
                    elif event.key == pygame.K_1:
                        self.spawn_ally("Warrior")
                    elif event.key == pygame.K_2:
                        self.spawn_ally("Archer")
                    elif event.key == pygame.K_3:
                        self.spawn_ally("Knight")
                    elif event.key == pygame.K_4:
                        self.spawn_ally("Catapult")
                        
                elif self.state == "paused":
                    if event.key == pygame.K_ESCAPE:
                        self.state = "playing"
                    elif event.key == pygame.K_q:
                        self.state = "main_menu"
                        
                elif self.state in ("victory", "game_over"):
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        self.state = "main_menu"

    def handle_collisions(self) -> None:
        """Determines combat engagements and stops walking movement."""
        # Split active units into friendly and enemy pools
        friendlies = [u for u in self.units if u.team == "friendly" and u.state != "dying"]
        enemies = [u for u in self.units if u.team == "enemy" and u.state != "dying"]

        # 1. Update Friendly Unit target locks
        for f in friendlies:
            # Find the closest enemy in front of us
            closest_enemy = None
            min_dist = float('inf')
            
            for e in enemies:
                # Is the enemy in front of us?
                in_front = (cfg.TOWER_SIDE == "left" and e.x > f.x) or (cfg.TOWER_SIDE == "right" and e.x < f.x)
                if in_front:
                    dist_x = abs(e.x - f.x)
                    if dist_x < min_dist:
                        min_dist = dist_x
                        closest_enemy = e

            # Check if closest enemy is in attack range
            # Note: For range, we check distance between unit coordinate boxes.
            if closest_enemy and min_dist <= f.attack_range:
                f.target = closest_enemy
                f.state = "combat"
            else:
                # If we were in combat but target is gone or out of range, walk again
                if f.state == "combat":
                    f.state = "walking"
                    f.target = None

        # 2. Update Enemy Unit target locks
        for e in enemies:
            # Enemy can target:
            # A. The Player (if on ground, vulnerable, and in range)
            # B. Closest friendly unit
            # C. The Tower (if close enough)
            
            # Target check A: Player on ground
            player_in_range = False
            dist_player = float('inf')
            if not self.player.in_tower:
                in_front_p = (cfg.TOWER_SIDE == "left" and self.player.x < e.x) or (cfg.TOWER_SIDE == "right" and self.player.x > e.x)
                if in_front_p:
                    dist_player = abs(self.player.x - e.x)
                    if dist_player <= e.attack_range:
                        player_in_range = True

            # Target check B: Allied units
            closest_friendly = None
            min_dist = float('inf')
            for f in friendlies:
                in_front_f = (cfg.TOWER_SIDE == "left" and f.x < e.x) or (cfg.TOWER_SIDE == "right" and f.x > e.x)
                if in_front_f:
                    dist_x = abs(f.x - e.x)
                    if dist_x < min_dist:
                        min_dist = dist_x
                        closest_friendly = f

            # Target check C: Tower
            tower_in_range = False
            dist_tower = float('inf')
            if cfg.TOWER_SIDE == "left":
                # Tower spans x = 0 to TOWER_WIDTH
                if e.x > cfg.TOWER_WIDTH:
                    dist_tower = e.x - cfg.TOWER_WIDTH
                    if dist_tower <= e.attack_range:
                        tower_in_range = True
            else:  # right side tower
                # Tower spans x = SCREEN_WIDTH - TOWER_WIDTH to SCREEN_WIDTH
                tower_left_edge = cfg.SCREEN_WIDTH - cfg.TOWER_WIDTH
                if e.x < tower_left_edge:
                    dist_tower = tower_left_edge - e.x
                    if dist_tower <= e.attack_range:
                        tower_in_range = True

            # Prioritize target: closest object
            # Sort possibilities: Player, Friendly, Tower
            possibilities: list[tuple[float, Any, str]] = []
            if player_in_range:
                possibilities.append((dist_player, self.player, "player"))
            if closest_friendly and min_dist <= e.attack_range:
                possibilities.append((min_dist, closest_friendly, "unit"))
            if tower_in_range:
                possibilities.append((dist_tower, self.tower, "tower"))

            if possibilities:
                # Target the closest option
                possibilities.sort(key=lambda item: item[0])
                closest_target = possibilities[0][1]
                e.target = closest_target
                e.state = "combat"
            else:
                if e.state == "combat":
                    e.state = "walking"
                    e.target = None

    def update(self) -> None:
        """Ticks animation timers, processes waves, checks states, and moves physics."""
        if self.state != "playing":
            return

        # 1. Update screen shake
        if self.shake_intensity > 0.1:
            self.shake_intensity *= 0.88
        else:
            self.shake_intensity = 0.0

        # 2. Update entities
        self.tower.update()
        
        # Read keys and mouse position
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        self.player.update(keys, mouse_pos, mouse_pressed, self.tower)
        
        # Pull arrow/boulder projectiles spawned by player
        if self.player.projectiles_to_spawn:
            self.projectiles.extend(self.player.projectiles_to_spawn)
            self.player.projectiles_to_spawn.clear()

        # Update units
        for unit in self.units:
            unit.update(self.particles)
            
            # Pull projectiles spawned by archer/catapult units
            if isinstance(unit, (Archer, Catapult)):
                if unit.projectiles_to_spawn:
                    self.projectiles.extend(unit.projectiles_to_spawn)
                    unit.projectiles_to_spawn.clear()

        # Update Projectiles
        for p in self.projectiles:
            p.update(self.units, self.tower, self.particles)
            # Trigger screen shake on heavy catapult boulder impact
            if p.is_dead and p.type == "boulder":
                self.shake_intensity = 8.5

        # Filter dead projectiles
        self.projectiles = [p for p in self.projectiles if not p.is_dead]

        # Process unit deaths and economy rewards
        for unit in self.units:
            if unit.state == "dying" and unit not in self.dead_rewarded_units:
                self.dead_rewarded_units.add(unit)
                if unit.team == "enemy":
                    # Reward gold
                    reward = cfg.GOLD_PER_KILL.get(unit.name, 25)
                    self.gold += reward
                    # Spawn gold spark particles
                    self.particles.spawn_sparks(unit.x, unit.y - 15, amount=6)

        # Filter fully dead units (those whose death fade timer expired)
        self.units = [u for u in self.units if not (u.state == "dying" and u.death_timer <= 0)]

        # Update particles
        self.particles.update()

        # 3. Handle Combat engagements
        self.handle_collisions()

        # 4. Wave Spawner Logic
        if self.wave_active:
            # Active spawning
            if self.enemies_to_spawn:
                self.spawn_timer += 1
                if self.spawn_timer >= self.spawn_cooldown:
                    self.spawn_timer = 0
                    next_enemy_type = self.enemies_to_spawn.pop(0)
                    self.spawn_enemy(next_enemy_type)
            
            # Count currently remaining enemies (both alive and in queue)
            alive_enemies = sum(1 for u in self.units if u.team == "enemy")
            self.enemies_remaining = len(self.enemies_to_spawn) + alive_enemies
            
            # Check wave completed
            if self.enemies_remaining == 0:
                self.wave_active = False
                self.next_wave_timer = self.next_wave_timer_max
        else:
            # Cooldown between waves
            self.next_wave_timer -= 1
            if self.next_wave_timer <= 0:
                self.spawn_wave()

        # 5. Check Defeat Conditions
        if self.tower.health <= 0 or self.player.health <= 0:
            self.state = "game_over"

    def draw(self) -> None:
        """Renders all game layers to screen with optional camera shake."""
        # Renders the gameplay elements to a viewport surface first.
        # This makes implementing screen shake extremely easy by offset-blitting.
        view_surf = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
        view_surf.fill(cfg.COLOR_BACKGROUND)

        # Draw Sky/Horizon line details (mountains or trees)
        # Background horizon details
        horizon_y = cfg.GROUND_Y
        pygame.draw.rect(view_surf, (25, 25, 38), (0, 0, cfg.SCREEN_WIDTH, horizon_y))
        
        # Draw distant mountain vectors
        mountain_points1 = [(0, horizon_y), (150, horizon_y - 120), (350, horizon_y), (500, horizon_y - 160), (700, horizon_y), (850, horizon_y - 110), (cfg.SCREEN_WIDTH, horizon_y)]
        pygame.draw.polygon(view_surf, (22, 22, 32), mountain_points1)
        
        mountain_points2 = [(0, horizon_y), (80, horizon_y - 60), (220, horizon_y), (400, horizon_y - 80), (600, horizon_y), (880, horizon_y - 70), (cfg.SCREEN_WIDTH, horizon_y)]
        pygame.draw.polygon(view_surf, (25, 27, 38), mountain_points2)

        # Draw Ground
        pygame.draw.rect(view_surf, cfg.COLOR_GROUND, (0, horizon_y, cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT - horizon_y))
        pygame.draw.line(view_surf, (45, 50, 65), (0, horizon_y), (cfg.SCREEN_WIDTH, horizon_y), 3)

        # Draw Tower
        self.tower.draw(view_surf)

        # Draw active Projectiles
        for p in self.projectiles:
            p.draw(view_surf)

        # Draw active Particles
        self.particles.draw(view_surf)

        # Draw active Units (Sort units by Y so they render correctly, though they are all on the ground Y)
        # Sort so that dying units are in the background, living units in foreground
        sorted_units = sorted(self.units, key=lambda u: 0 if u.state == "dying" else 1)
        for unit in sorted_units:
            unit.draw(view_surf)

        # Draw Player
        self.player.draw(view_surf, self.particles)

        # Apply screen shake displacement onto main screen
        shake_x = 0
        shake_y = 0
        if self.shake_intensity > 0:
            shake_x = int(random.uniform(-self.shake_intensity, self.shake_intensity))
            shake_y = int(random.uniform(-self.shake_intensity, self.shake_intensity))

        # Blit gameplay surface to main screen with offset
        self.screen.blit(view_surf, (shake_x, shake_y))

        # HUD and menus are drawn directly to the screen (so they don't shake)
        if self.state == "playing":
            self.hud.draw(
                surface=self.screen,
                player_health=self.player.health,
                player_max_health=self.player.max_health,
                tower_health=self.tower.health,
                tower_max_health=self.tower.max_health,
                gold=self.gold,
                wave=self.wave,
                wave_active=self.wave_active,
                enemies_remaining=self.enemies_remaining,
                spawner_timer=self.next_wave_timer,
                spawner_timer_max=self.next_wave_timer_max,
            )
        elif self.state == "main_menu":
            self.menu.draw_main_menu(self.screen, cfg.TOWER_SIDE)
        elif self.state == "paused":
            # Still draw HUD behind overlay
            self.hud.draw(
                surface=self.screen,
                player_health=self.player.health,
                player_max_health=self.player.max_health,
                tower_health=self.tower.health,
                tower_max_health=self.tower.max_health,
                gold=self.gold,
                wave=self.wave,
                wave_active=self.wave_active,
                enemies_remaining=self.enemies_remaining,
                spawner_timer=self.next_wave_timer,
                spawner_timer_max=self.next_wave_timer_max,
            )
            self.menu.draw_pause_menu(self.screen)
        elif self.state == "game_over":
            self.menu.draw_game_over(self.screen, victory=False, wave=self.wave - 1)
        elif self.state == "victory":
            self.menu.draw_game_over(self.screen, victory=True, wave=self.wave)

    def run(self) -> None:
        """Launches the Pygame event queue and tick updates."""
        self.running = True
        while self.running:
            self.handle_events()
            if not self.running:
                break
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(cfg.FPS)
        pygame.quit()
