import pygame
import sys
from settings import *
from grid import Grid
from player import Player
from enemy import Enemy
from gamestate import GameState

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Fonts
        self.font_large = pygame.font.SysFont("Arial", 64, bold=True)
        self.font_small = pygame.font.SysFont("Consolas", 24, bold=True)
        
        self.state = "RUNNING" # RUNNING, GAMEOVER
        
        self.load()

    def load(self):
        self.gamestate = GameState(GRID_WIDTH, GRID_HEIGHT)
        self.grid = Grid(GRID_WIDTH, GRID_HEIGHT, TILE_SIZE)
        
        # Temp spawn points
        self.start_node = self.grid.nodes[1][1]
        self.enemy_node = self.grid.nodes[GRID_WIDTH-2][GRID_HEIGHT-2]
        
        self.player = Player(self.start_node, self.grid)
        self.enemy = Enemy(self.enemy_node, self.grid)

        self.debug_path = []
        self.state = "RUNNING"

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.events()
            self.update(dt)
            self.draw()
            
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.state == "GAMEOVER":
                        self.reset_game_loop(success=False)
                    else:
                        # R reset manually
                        self.reset_game_loop(success=False)

    def reset_game_loop(self, success=False):
        # Trigger Loop Reset Logic
        heatmap = self.gamestate.reset_loop(self.player.visited_nodes, success=success)
        
        if success:
            # New Level -> New Map
            self.grid.generate_map(level=self.gamestate.level)
        else:
             # Adapt Environment (Same Level)
            self.grid.adapt_to_history(heatmap)
        
        # Reset Entities
        self.player = Player(self.grid.nodes[1][1], self.grid)
        self.enemy = Enemy(self.grid.nodes[GRID_WIDTH-2][GRID_HEIGHT-2], self.grid)
        self.state = "RUNNING"

    def update(self, dt):
        if self.state == "GAMEOVER":
            return

        self.player.update(dt)
        self.enemy.update(dt, self.player.node, self.player.vel, self.gamestate.level, self.player.is_backtracking)
        
        # Check Win Condition (Portal)
        if self.player.node.is_portal:
            print("Loop Complete! Rewriting World...")
            self.reset_game_loop(success=True)
            
        # Check Fail Condition (Collision)
        # Using a distance check for simplicity or rect collision
        dist = self.player.pos.distance_to(self.enemy.pos)
        if dist < self.player.radius + self.enemy.radius:
            self.state = "GAMEOVER"
            print("FAILURE STATE")

    def draw(self):
        self.screen.fill(COLOR_BG)
        self.grid.draw(self.screen)
        
        # Draw Enemy Path (Visual Communication: "Optimal paths... dangerous")
        if self.enemy.path:
            points = [node.rect.center for node in self.enemy.path]
            # Add current enemy pos to start
            points.insert(0, (self.enemy.pos.x, self.enemy.pos.y))
            if len(points) > 1:
                pygame.draw.lines(self.screen, (200, 50, 50), False, points, 2)

        self.player.draw(self.screen)
        self.enemy.draw(self.screen)
        
        # --- UI / Contextual Text ---
        if self.state == "RUNNING":
            # Level / Loop UI
            level_text = self.font_small.render(f"LEVEL {self.gamestate.level}", True, COLOR_TEXT)
            self.screen.blit(level_text, (20, 20))
            
            # 1. Proximity Warning
            dist = self.player.pos.distance_to(self.enemy.pos)
            if dist < 300: # Close!
                text = self.font_small.render("MOVE!", True, (255, 50, 50))
                # Draw above player
                rect = text.get_rect(center=(self.player.pos.x, self.player.pos.y - 40))
                self.screen.blit(text, rect)
                
            # 2. Block Logic
            # If player is pressing keys (acc > 0) but not moving much (vel < threshold), they are blocked
            if self.player.acc.length() > 0 and self.player.vel.length() < 20:
                text = self.font_small.render("CAN NOT MOVE", True, (255, 200, 50))
                rect = text.get_rect(center=(self.player.pos.x, self.player.pos.y + 40))
                self.screen.blit(text, rect)
                
            # 3. Boost Text
            if self.player.boost_timer > 0:
                text = self.font_small.render("haaaw,,haww", True, (0, 255, 255))
                # Jitter it slightly for effect?
                import random
                offset_x = random.randint(-2, 2)
                offset_y = random.randint(-2, 2)
                rect = text.get_rect(center=(self.player.pos.x + offset_x, self.player.pos.y - 50 + offset_y))
                self.screen.blit(text, rect)
                
        elif self.state == "GAMEOVER":
            # Overlay
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            s.set_alpha(150)
            s.fill((0,0,0))
            self.screen.blit(s, (0,0))
            
            msg = self.font_large.render("FAILURE", True, (255, 50, 50))
            rect = msg.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(msg, rect)
            
            sub = self.font_small.render("Press SPACE to Reset Loop", True, (200, 200, 200))
            rect_sub = sub.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
            self.screen.blit(sub, rect_sub)

        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()
