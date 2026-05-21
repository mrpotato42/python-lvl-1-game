"""Configuration and constants for the Arrow Defense: Siege of the Tower game."""

from typing import Literal

# Screen and Performance Settings
SCREEN_WIDTH: int = 1024
SCREEN_HEIGHT: int = 768
FPS: int = 60

# Gameplay Configuration
# Can be "left" or "right". The player tower will be spawned on this side.
TOWER_SIDE: Literal["left", "right"] = "left"

# Physics Settings
GRAVITY: float = 0.45  # Pixels / frame^2

# Ground Level
GROUND_Y: int = 650

# Visual Palette (Rich aesthetics - Dark Mode / Fantasy Palette)
COLOR_BACKGROUND: tuple[int, int, int] = (20, 20, 30)       # Deep slate blue
COLOR_GROUND: tuple[int, int, int] = (30, 35, 45)           # Dark rocky gray
COLOR_TOWER: tuple[int, int, int] = (60, 65, 80)            # Slate stone
COLOR_TOWER_TRIM: tuple[int, int, int] = (40, 45, 55)       # Dark slate trim
COLOR_PLAYER: tuple[int, int, int] = (0, 200, 255)          # Cyan archer
COLOR_FRIENDLY: tuple[int, int, int] = (50, 220, 120)       # Forest green/emerald (allies)
COLOR_ENEMY: tuple[int, int, int] = (255, 60, 100)          # Crimson red (enemies)

# Unit Palette for detailed vector art
COLOR_WARRIOR: tuple[int, int, int] = (100, 180, 255)
COLOR_ARCHER: tuple[int, int, int] = (150, 230, 150)
COLOR_KNIGHT: tuple[int, int, int] = (220, 220, 240)
COLOR_CATAPULT: tuple[int, int, int] = (180, 110, 50)

# UI Colors
COLOR_GOLD: tuple[int, int, int] = (255, 215, 0)            # Gold
COLOR_WHITE: tuple[int, int, int] = (245, 245, 250)
COLOR_GRAY: tuple[int, int, int] = (120, 120, 130)
COLOR_BLACK: tuple[int, int, int] = (10, 10, 15)
COLOR_UI_PANEL: tuple[int, int, int] = (35, 35, 50)         # Semi-transparent dark panel
COLOR_HEALTH_BAR_BG: tuple[int, int, int] = (60, 20, 20)
COLOR_HEALTH_BAR_FILL: tuple[int, int, int] = (50, 220, 100)

# Projectile stats
ARROW_SPEED_MULTIPLIER: float = 0.05
BOULDER_SPEED_MULTIPLIER: float = 0.04

# Unit Data Structures (Typed)
class UnitStats:
    """Class to hold stats for a specific unit type."""
    def __init__(
        self,
        name: str,
        max_health: float,
        speed: float,
        damage: float,
        attack_range: float,
        cooldown: int,  # in frames
        cost: int,
        width: int,
        height: int,
        color: tuple[int, int, int],
    ) -> None:
        self.name = name
        self.max_health = max_health
        self.speed = speed
        self.damage = damage
        self.attack_range = attack_range
        self.cooldown = cooldown
        self.cost = cost
        self.width = width
        self.height = height
        self.color = color

# Stats for each Troop Type
STATS_WARRIOR = UnitStats(
    name="Warrior",
    max_health=120.0,
    speed=1.5,
    damage=15.0,
    attack_range=30.0,
    cooldown=45,  # ~0.75 seconds at 60fps
    cost=50,
    width=24,
    height=40,
    color=COLOR_WARRIOR,
)

STATS_ARCHER = UnitStats(
    name="Archer",
    max_health=70.0,
    speed=1.2,
    damage=10.0,  # damage per arrow
    attack_range=350.0,
    cooldown=90,  # 1.5 seconds
    cost=75,
    width=22,
    height=38,
    color=COLOR_ARCHER,
)

STATS_KNIGHT = UnitStats(
    name="Knight",
    max_health=250.0,
    speed=0.8,
    damage=25.0,
    attack_range=35.0,
    cooldown=60,  # 1 second
    cost=150,
    width=28,
    height=44,
    color=COLOR_KNIGHT,
)

STATS_CATAPULT = UnitStats(
    name="Catapult",
    max_health=100.0,
    speed=0.5,
    damage=60.0,  # High AoE splash damage
    attack_range=500.0,
    cooldown=240,  # 4 seconds
    cost=250,
    width=45,
    height=35,
    color=COLOR_CATAPULT,
)

# Wave settings
INITIAL_WAVE_GOLD: int = 150
GOLD_PER_KILL: dict[str, int] = {
    "Warrior": 70,
    "Archer": 15,
    "Knight": 150,
    "Catapult": 200,
}

# Tower stats
TOWER_MAX_HEALTH: float = 1000.0
TOWER_WIDTH: int = 120
TOWER_HEIGHT: int = 450
TOWER_BALCONY_Y: int = SCREEN_HEIGHT - TOWER_HEIGHT  # y = 318

# Player stats
PLAYER_MAX_HEALTH: float = 150.0
PLAYER_SPEED: float = 3.0
PLAYER_ARROW_DAMAGE: float = 25.0
PLAYER_MAX_CHARGE: float = 20.0
PLAYER_WIDTH: int = 24
PLAYER_HEIGHT: int = 40
