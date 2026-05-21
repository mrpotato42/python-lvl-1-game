"""Menu overlays (Main Menu, Pause, Game Over, Victory) for Arrow Defense."""

import pygame
from src.config import (
    COLOR_WHITE, COLOR_GRAY, COLOR_BLACK, COLOR_GOLD, TOWER_SIDE,
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BACKGROUND
)

class Menu:
    """Renders menu screen overlays and handles simple screen logic."""

    def __init__(self) -> None:
        pygame.font.init()
        # Clean modern typography
        self.font_title = pygame.font.SysFont("Segoe UI", 48, bold=True)
        self.font_subtitle = pygame.font.SysFont("Segoe UI", 22)
        self.font_body = pygame.font.SysFont("Segoe UI", 16)
        self.font_hint = pygame.font.SysFont("Segoe UI", 13)

    def draw_main_menu(self, surface: pygame.Surface, current_side: str) -> None:
        """Renders the Title Start Screen."""
        # Draw background color
        surface.fill(COLOR_BACKGROUND)

        # Draw aesthetic geometric grids in the background
        for x in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(surface, (30, 30, 45), (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(surface, (30, 30, 45), (0, y), (SCREEN_WIDTH, y), 1)

        # Draw decorative castle tower vector on the screen center-bottom
        tower_x = SCREEN_WIDTH // 2 - 50
        tower_y = SCREEN_HEIGHT - 300
        pygame.draw.rect(surface, (45, 45, 55), (tower_x, tower_y, 100, 300))
        pygame.draw.rect(surface, (30, 30, 35), (tower_x - 10, tower_y - 15, 120, 15))
        # Crenelations
        for i in range(4):
            pygame.draw.rect(surface, (30, 30, 35), (tower_x - 10 + i * 35, tower_y - 30, 20, 15))
        # Arch door
        pygame.draw.ellipse(surface, (10, 10, 15), (tower_x + 30, SCREEN_HEIGHT - 60, 40, 60))

        # Title shadow
        title_lbl_shadow = self.font_title.render("ARROW DEFENSE", True, (10, 10, 15))
        surface.blit(title_lbl_shadow, (SCREEN_WIDTH // 2 - title_lbl_shadow.get_width() // 2 + 3, 153))
        # Title
        title_lbl = self.font_title.render("ARROW DEFENSE", True, (0, 180, 255))
        surface.blit(title_lbl, (SCREEN_WIDTH // 2 - title_lbl.get_width() // 2, 150))

        # Subtitle
        sub_lbl = self.font_subtitle.render("Siege of the Tower", True, COLOR_GOLD)
        surface.blit(sub_lbl, (SCREEN_WIDTH // 2 - sub_lbl.get_width() // 2, 215))

        # Box panel for options
        box_w = 460
        box_h = 160
        box_x = (SCREEN_WIDTH - box_w) // 2
        box_y = 280
        box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        pygame.draw.rect(box_surf, (30, 30, 45, 230), (0, 0, box_w, box_h), border_radius=8)
        pygame.draw.rect(box_surf, (60, 60, 80, 255), (0, 0, box_w, box_h), 2, border_radius=8)
        surface.blit(box_surf, (box_x, box_y))

        # Start game action
        start_lbl = self.font_body.render("Press  [ ENTER ]  to Deploy & Start Defense", True, COLOR_WHITE)
        surface.blit(start_lbl, (SCREEN_WIDTH // 2 - start_lbl.get_width() // 2, box_y + 25))

        # Tower side selector action
        
        
        # Friendly fire warning / difficulty info
        info_lbl = self.font_body.render("Friendly Fire is ACTIVE: watch where you shoot!", True, (255, 100, 100))
        surface.blit(info_lbl, (SCREEN_WIDTH // 2 - info_lbl.get_width() // 2, box_y + 110))

        # Footer instructions
        footer_lbl = self.font_hint.render("W/S: Enter/Exit Balcony  |  A/D: Move  |  1-4: Recruit Troops  |  Mouse: Aim & Shoot", True, COLOR_GRAY)
        surface.blit(footer_lbl, (SCREEN_WIDTH // 2 - footer_lbl.get_width() // 2, SCREEN_HEIGHT - 50))

    def draw_pause_menu(self, surface: pygame.Surface) -> None:
        """Renders the transparent Pause overlay."""
        pause_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        # Semi-transparent dark overlay
        pause_surf.fill((15, 15, 25, 180))
        
        # Center panel
        panel_w = 350
        panel_h = 180
        px = (SCREEN_WIDTH - panel_w) // 2
        py = (SCREEN_HEIGHT - panel_h) // 2
        pygame.draw.rect(pause_surf, (30, 30, 45, 240), (px, py, panel_w, panel_h), border_radius=8)
        pygame.draw.rect(pause_surf, (60, 60, 80, 255), (px, py, panel_w, panel_h), 2, border_radius=8)
        
        surface.blit(pause_surf, (0, 0))

        # Text
        p_title = self.font_title.render("PAUSED", True, (0, 180, 255))
        surface.blit(p_title, (SCREEN_WIDTH // 2 - p_title.get_width() // 2, py + 25))

        p_resume = self.font_body.render("Press  [ ESC ]  to Resume Game", True, COLOR_WHITE)
        p_quit = self.font_body.render("Press  [ Q ]  to Quit to Main Menu", True, COLOR_GRAY)

        surface.blit(p_resume, (SCREEN_WIDTH // 2 - p_resume.get_width() // 2, py + 95))
        surface.blit(p_quit, (SCREEN_WIDTH // 2 - p_quit.get_width() // 2, py + 130))

    def draw_game_over(self, surface: pygame.Surface, victory: bool, wave: int) -> None:
        """Renders the End Game Victory/Defeat screen."""
        end_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Color base depending on outcome
        if victory:
            bg_color = (20, 40, 25, 200) # Transparent emerald
            title_text = "VICTORY"
            title_color = (50, 220, 100)
            desc_text = "Siege cleared! You defended the kingdom's tower."
        else:
            bg_color = (50, 15, 15, 200) # Transparent dark red
            title_text = "TOWER DESTROYED"
            title_color = (255, 60, 60)
            desc_text = "The tower has fallen to the enemy siege."

        end_surf.fill(bg_color)
        
        # Center panel
        panel_w = 480
        panel_h = 240
        px = (SCREEN_WIDTH - panel_w) // 2
        py = (SCREEN_HEIGHT - panel_h) // 2
        pygame.draw.rect(end_surf, (30, 30, 45, 240), (px, py, panel_w, panel_h), border_radius=8)
        pygame.draw.rect(end_surf, (60, 60, 80, 255), (px, py, panel_w, panel_h), 2, border_radius=8)

        surface.blit(end_surf, (0, 0))

        # Title
        t_lbl = self.font_title.render(title_text, True, title_color)
        surface.blit(t_lbl, (SCREEN_WIDTH // 2 - t_lbl.get_width() // 2, py + 25))

        # Description
        d_lbl = self.font_subtitle.render(desc_text, True, COLOR_WHITE)
        surface.blit(d_lbl, (SCREEN_WIDTH // 2 - d_lbl.get_width() // 2, py + 90))

        # Score
        w_lbl = self.font_body.render(f"Waves successfully defended: {wave}", True, COLOR_GOLD)
        surface.blit(w_lbl, (SCREEN_WIDTH // 2 - w_lbl.get_width() // 2, py + 135))

        # Restarts
        r_lbl = self.font_body.render("Press  [ ENTER ]  to Play Again", True, COLOR_WHITE)
        q_lbl = self.font_body.render("Press  [ Q ]  to Quit to Main Menu", True, COLOR_GRAY)
        
        surface.blit(r_lbl, (SCREEN_WIDTH // 2 - r_lbl.get_width() // 2, py + 175))
        surface.blit(q_lbl, (SCREEN_WIDTH // 2 - q_lbl.get_width() // 2, py + 200))
