"""HUD rendering module for Arrow Defense: Siege of the Tower."""

import pygame
from src.config import (
    COLOR_GOLD, COLOR_WHITE, COLOR_GRAY, COLOR_BLACK, COLOR_UI_PANEL,
    STATS_WARRIOR, STATS_ARCHER, STATS_KNIGHT, STATS_CATAPULT,
    COLOR_WARRIOR, COLOR_ARCHER, COLOR_KNIGHT, COLOR_CATAPULT,
    SCREEN_WIDTH, SCREEN_HEIGHT
)

class HUD:
    """Renders all heads-up display components during gameplay."""

    def __init__(self) -> None:
        pygame.font.init()
        # Clean typography hierarchy
        self.font_large = pygame.font.SysFont("Segoe UI", 28, bold=True)
        self.font_medium = pygame.font.SysFont("Segoe UI", 20, bold=True)
        self.font_small = pygame.font.SysFont("Segoe UI", 14)
        self.font_tiny = pygame.font.SysFont("Segoe UI", 11)

    def draw(
        self,
        surface: pygame.Surface,
        player_health: float,
        player_max_health: float,
        tower_health: float,
        tower_max_health: float,
        gold: int,
        wave: int,
        wave_active: bool,
        enemies_remaining: int,
        spawner_timer: int,
        spawner_timer_max: int,
    ) -> None:
        """Renders health bars, gold, wave info, recruitment hotbar, and controls."""
        
        # 1. Top Panel (Health, Gold, Wave info)
        top_bar_h = 60
        # Glassmorphism panel with opacity
        top_panel = pygame.Surface((SCREEN_WIDTH, top_bar_h), pygame.SRCALPHA)
        pygame.draw.rect(top_panel, (*COLOR_UI_PANEL, 200), (0, 0, SCREEN_WIDTH, top_bar_h))
        # Shadow bottom border
        pygame.draw.line(top_panel, (60, 60, 80, 150), (0, top_bar_h - 1), (SCREEN_WIDTH, top_bar_h - 1), 2)
        surface.blit(top_panel, (0, 0))

        # RENDER HEALTH: Player
        player_lbl = self.font_small.render("PLAYER HEALTH", True, COLOR_WHITE)
        surface.blit(player_lbl, (20, 8))
        # Draw player health bar
        p_bar_w = 180
        p_bar_h = 16
        pygame.draw.rect(surface, (50, 15, 15), (20, 26, p_bar_w, p_bar_h), border_radius=3)
        p_pct = max(0.0, player_health / player_max_health)
        pygame.draw.rect(surface, (0, 180, 255), (20, 26, int(p_bar_w * p_pct), p_bar_h), border_radius=3)
        pygame.draw.rect(surface, (100, 100, 120), (20, 26, p_bar_w, p_bar_h), 1, border_radius=3)

        # RENDER HEALTH: Tower
        tower_lbl = self.font_small.render("TOWER HEALTH", True, COLOR_WHITE)
        surface.blit(tower_lbl, (220, 8))
        t_bar_w = 200
        t_bar_h = 16
        pygame.draw.rect(surface, (50, 15, 15), (220, 26, t_bar_w, t_bar_h), border_radius=3)
        t_pct = max(0.0, tower_health / tower_max_health)
        pygame.draw.rect(surface, (50, 220, 100), (220, 26, int(t_bar_w * t_pct), t_bar_h), border_radius=3)
        pygame.draw.rect(surface, (100, 100, 120), (220, 26, t_bar_w, t_bar_h), 1, border_radius=3)

        # RENDER GOLD
        # Draw gold icon (gold coin)
        coin_x = 460
        coin_y = 30
        pygame.draw.circle(surface, COLOR_GOLD, (coin_x, coin_y), 10)
        pygame.draw.circle(surface, (200, 150, 0), (coin_x, coin_y), 10, 1)
        # Gold text
        gold_txt = self.font_medium.render(f"{gold}g", True, COLOR_GOLD)
        surface.blit(gold_txt, (coin_x + 18, coin_y - 12))

        # RENDER WAVE STATS
        wave_str = f"WAVE {wave}"
        wave_lbl = self.font_medium.render(wave_str, True, COLOR_WHITE)
        surface.blit(wave_lbl, (650, 15))

        if wave_active:
            status_str = f"Enemies: {enemies_remaining}"
            status_color = (255, 100, 100)
        else:
            # Preparing countdown
            sec = max(0, int(spawner_timer / 60))
            status_str = f"Next Wave: {sec}s"
            status_color = (255, 200, 0)
            
        status_lbl = self.font_small.render(status_str, True, status_color)
        surface.blit(status_lbl, (750, 18))

        # 2. Bottom Spawning Hotbar
        # Width: 4 units cards, each 110 wide, spacing 10
        hotbar_w = 490
        hotbar_h = 75
        hotbar_x = (SCREEN_WIDTH - hotbar_w) // 2
        hotbar_y = SCREEN_HEIGHT - hotbar_h - 15

        hb_panel = pygame.Surface((hotbar_w, hotbar_h), pygame.SRCALPHA)
        pygame.draw.rect(hb_panel, (*COLOR_UI_PANEL, 220), (0, 0, hotbar_w, hotbar_h), border_radius=8)
        pygame.draw.rect(hb_panel, (70, 70, 90, 180), (0, 0, hotbar_w, hotbar_h), 2, border_radius=8)
        surface.blit(hb_panel, (hotbar_x, hotbar_y))

        # Render each Unit Recruit Card
        unit_cards = [
            ("1", STATS_WARRIOR, COLOR_WARRIOR),
            ("2", STATS_ARCHER, COLOR_ARCHER),
            ("3", STATS_KNIGHT, COLOR_KNIGHT),
            ("4", STATS_CATAPULT, COLOR_CATAPULT),
        ]

        card_w = 105
        card_h = 60
        for i, (key, stats, color) in enumerate(unit_cards):
            cx = hotbar_x + 15 + i * (card_w + 10)
            cy = hotbar_y + 8

            # Check if affordable
            affordable = gold >= stats.cost
            
            # Card background
            card_bg = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            bg_color = (45, 45, 65, 255) if affordable else (25, 25, 30, 255)
            pygame.draw.rect(card_bg, bg_color, (0, 0, card_w, card_h), border_radius=5)
            # Accent outline
            border_color = (80, 200, 120, 255) if affordable else (100, 40, 40, 180)
            pygame.draw.rect(card_bg, border_color, (0, 0, card_w, card_h), 1, border_radius=5)
            surface.blit(card_bg, (cx, cy))

            # Number Key shortcut
            key_txt = self.font_medium.render(key, True, (0, 180, 255) if affordable else COLOR_GRAY)
            surface.blit(key_txt, (cx + 8, cy + 4))

            # Unit Name
            name_txt = self.font_small.render(stats.name, True, COLOR_WHITE if affordable else COLOR_GRAY)
            surface.blit(name_txt, (cx + 25, cy + 5))

            # Draw small colored colored node representing the unit visually
            pygame.draw.circle(surface, color, (cx + 15, cy + 40), 6)
            if not affordable:
                pygame.draw.line(surface, (250, 40, 40), (cx + 9, cy + 34), (cx + 21, cy + 46), 2)

            # Cost
            cost_txt = self.font_medium.render(f"{stats.cost}g", True, COLOR_GOLD if affordable else COLOR_GRAY)
            surface.blit(cost_txt, (cx + 35, cy + 30))

        # 3. Controls / Instructions Help Panel (Bottom-Left)
        help_panel_w = 210
        help_panel_h = 85
        hpx = 20
        hpy = SCREEN_HEIGHT - help_panel_h - 15

        help_panel = pygame.Surface((help_panel_w, help_panel_h), pygame.SRCALPHA)
        pygame.draw.rect(help_panel, (*COLOR_UI_PANEL, 170), (0, 0, help_panel_w, help_panel_h), border_radius=6)
        pygame.draw.rect(help_panel, (60, 60, 80, 100), (0, 0, help_panel_w, help_panel_h), 1, border_radius=6)
        surface.blit(help_panel, (hpx, hpy))

        lbl_controls = self.font_small.render("CONTROLS CHEAT SHEET", True, (0, 200, 255))
        surface.blit(lbl_controls, (hpx + 10, hpy + 6))
        
        lbl_move = self.font_tiny.render("Move: A / D (or Left / Right)", True, COLOR_WHITE)
        lbl_tower = self.font_tiny.render("Enter/Exit Tower: W / S", True, COLOR_WHITE)
        lbl_shoot = self.font_tiny.render("Shoot Bow: Left Click Hold & Drag", True, COLOR_WHITE)
        
        surface.blit(lbl_move, (hpx + 10, hpy + 26))
        surface.blit(lbl_tower, (hpx + 10, hpy + 43))
        surface.blit(lbl_shoot, (hpx + 10, hpy + 60))
