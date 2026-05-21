"""Main entrypoint of the Arrow Defense: Siege of the Tower game."""

import pygame
import src.config as cfg
from src.game import Game

def main() -> None:
    """Initializes Pygame, sets window properties, and starts the main loop."""
    pygame.init()
    
    # Set window title and clean game icon representation
    pygame.display.set_caption("Arrow Defense: Siege of the Tower")
    
    # Create the game window surface
    screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
    
    # Initialize and start game
    game = Game(screen)
    game.run()

if __name__ == "__main__":
    main()
