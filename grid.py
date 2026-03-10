import pygame
from settings import *

import heapq
import random
from genetic_map_gen import GeneticOptimizer


class Node:
    def __init__(self, x, y, tile_size):
        self.x = x
        self.y = y
        self.tile_size = tile_size
        self.rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
        self.is_wall = False
        self.is_portal = False 
        self.is_energy = False # Energy Node
        self.movement_penalty = 0 
        self.g_cost = float('inf')
        self.h_cost = 0
        self.f_cost = float('inf')
        self.parent = None
        self.visited_count = 0 
        
    def draw(self, surface):
        if self.is_wall:
            color = COLOR_WALL
        elif self.is_portal:
            color = COLOR_PORTAL
        elif self.is_energy:
            color = COLOR_ENERGY
        else:
            # Visualize penalty/usage
            base_color = list(COLOR_BG)
            if self.movement_penalty > 0:
                base_color[0] = min(255, base_color[0] + self.movement_penalty * 2)
                base_color[1] = max(0, base_color[1] - self.movement_penalty)
            
            if self.visited_count > 0:
                # Visited often -> "stabilised" -> Blue/Cyan
                base_color[2] = min(255, base_color[2] + self.visited_count * 20)

            color = tuple(base_color)
                
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (30, 30, 35), self.rect, 1) # Border

    def get_pos(self):
        return self.x, self.y

    def __lt__(self, other):
        return self.f_cost < other.f_cost

class Grid:
    def __init__(self, width, height, tile_size, headless=False):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.headless = headless # If True, don't load images or heavy logic
        self.nodes = [[Node(x, y, tile_size) for y in range(height)] for x in range(width)]
        
        self.optimizer = GeneticOptimizer() # Initialize GA
        
        if not self.headless:
            self.generate_map(level=1)
            
    def generate_map(self, level=1):
        # EVOLVE the next map parameters
        print(f"--- Generating Level {level} (Evolutionary Strategy) ---")
        best_genes = self.optimizer.evolve(Grid, self.width, self.height, level)
        self.apply_genes(best_genes)

    def apply_genes(self, genes):
        # Use Genes to determine generation logic
        fill_percent = genes.fill_percent
        smooth_iterations = genes.smooth_iterations
        wall_birth_limit = genes.wall_birth_limit
        wall_death_limit = genes.wall_death_limit
        
        # Initial Random Fill
        for x in range(self.width):
            for y in range(self.height):
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    self.nodes[x][y].is_wall = True
                else:
                    if random.random() < fill_percent:
                        self.nodes[x][y].is_wall = True
                    else:
                        self.nodes[x][y].is_wall = False
        
        # Cellular Automata Smoothing
        for _ in range(smooth_iterations): 
            self.smooth_map(wall_birth_limit, wall_death_limit)
            
        # Ensure Start/End/Portal are open
        self.clear_vital_areas()
        
        # Ensure Connectivity
        self.ensure_connectivity()
        
        # Place Energy Nodes (in open spaces)
        self.place_energy_nodes()

    def smooth_map(self, birth_limit=4, death_limit=4):
        new_map_walls = [[False for _ in range(self.height)] for _ in range(self.width)]
        
        for x in range(self.width):
            for y in range(self.height):
                neighbor_walls = self.get_wall_count(x, y)
                
                if self.nodes[x][y].is_wall:
                    if neighbor_walls < death_limit:
                        new_map_walls[x][y] = False
                    else:
                        new_map_walls[x][y] = True
                else:
                    if neighbor_walls > birth_limit:
                        new_map_walls[x][y] = True
                    else:
                        new_map_walls[x][y] = False
                    
        # Apply changes
        for x in range(self.width):
            for y in range(self.height):
                self.nodes[x][y].is_wall = new_map_walls[x][y]

    def get_wall_count(self, grid_x, grid_y):
        wall_count = 0
        for neighbor_x in range(grid_x - 1, grid_x + 2):
            for neighbor_y in range(grid_y - 1, grid_y + 2):
                if neighbor_x >= 0 and neighbor_x < self.width and neighbor_y >= 0 and neighbor_y < self.height:
                    if neighbor_x != grid_x or neighbor_y != grid_y:
                        if self.nodes[neighbor_x][neighbor_y].is_wall:
                            wall_count += 1
                else:
                    wall_count += 1 # Out of bounds counts as wall
        return wall_count

    def clear_vital_areas(self):
        # Spawn
        for x in range(1, 4):
            for y in range(1, 4):
                self.nodes[x][y].is_wall = False
                
        # Portal / End
        for x in range(self.width - 4, self.width - 1):
            for y in range(self.height - 4, self.height - 1):
                self.nodes[x][y].is_wall = False
                
        self.nodes[self.width - 2][self.height - 2].is_portal = True

    def place_energy_nodes(self):
        for x in range(self.width):
            for y in range(self.height):
                if not self.nodes[x][y].is_wall and not self.nodes[x][y].is_portal:
                    if random.random() < 0.03: # 3% chance in open space
                         self.nodes[x][y].is_energy = True

    def ensure_connectivity(self):
        start_node = self.nodes[1][1]
        end_node = self.nodes[self.width - 2][self.height - 2]
        
        path = self.find_path(start_node, end_node)
        
        if not path:
            # If no path, force carve one (naive approach: straight line or random walk)
            # Better: Regenerate? Or drunkard's walk.
            # Let's do Drunkard's Walk from start to end to force a tunnel.
            current = start_node
            while current != end_node:
                # Force wall open
                current.is_wall = False
                
                # Move towards end (simple step)
                cx, cy = current.x, current.y
                ex, ey = end_node.x, end_node.y
                
                dx = 0
                dy = 0
                
                if cx < ex: dx = 1
                elif cx > ex: dx = -1
                
                if cy < ey: dy = 1
                elif cy > ey: dy = -1
                
                # Randomly pick an axis to move along to make it jagged
                if dx != 0 and dy != 0:
                    if random.random() < 0.5: dy = 0
                    else: dx = 0
                
                self.nodes[cx + dx][cy + dy].is_wall = False
                current = self.nodes[cx + dx][cy + dy]

    def adapt_to_history(self, heatmap):
        # Improve prediction and restructure environment
        for x in range(self.width):
            for y in range(self.height):
                visits = heatmap[x][y]
                self.nodes[x][y].visited_count = visits
                self.nodes[x][y].movement_penalty = 0 # Reset runtime penalties (hesitation)
                
                if visits > 0:
                    # Frequent path: Ensure it is open
                    self.nodes[x][y].is_wall = False
                    
        # NOTE: Removed random wall flipping (random.random() < 0.1) because it was sealing off paths 
        # and breaking the cellular automata structure.
        
        # Ensure Start/End/Portal are open
        self.clear_vital_areas()
        
        # KEY FIX: Ensure connectivity after adapting
        self.ensure_connectivity()
        
        # Re-set portal (just in case)
        self.nodes[self.width - 2][self.height - 2].is_portal = True

    def draw(self, surface):
        for x in range(self.width):
            for y in range(self.height):
                self.nodes[x][y].draw(surface)

    def get_neighbors(self, node):
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]: # 4-directional for now, can add diagonals
            nx, ny = node.x + dx, node.y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                if not self.nodes[nx][ny].is_wall:
                    neighbors.append(self.nodes[nx][ny])
        return neighbors

    def reset_path_costs(self):
        for col in self.nodes:
            for node in col:
                node.g_cost = float('inf')
                node.h_cost = 0
                node.f_cost = float('inf')
                node.parent = None

    def find_path(self, start_node, end_node):
        self.reset_path_costs()
        start_node.g_cost = 0
        start_node.h_cost = self.heuristic(start_node, end_node)
        start_node.f_cost = start_node.g_cost + start_node.h_cost
        
        open_set = []
        heapq.heappush(open_set, start_node)
        
        closed_set = set() 
        
        while open_set:
            current = heapq.heappop(open_set)
            
            if current == end_node:
                return self.retrace_path(start_node, end_node)
                
            closed_set.add(current)
            
            for neighbor in self.get_neighbors(current):
                if neighbor in closed_set:
                    continue
                
                # Cost Calculation: Distance + Node Penalty
                base_dist = self.get_distance(current, neighbor)
                penalty = neighbor.movement_penalty
                new_movement_cost_to_neighbor = current.g_cost + base_dist + penalty
                
                if new_movement_cost_to_neighbor < neighbor.g_cost:
                    neighbor.g_cost = new_movement_cost_to_neighbor
                    neighbor.h_cost = self.heuristic(neighbor, end_node)
                    neighbor.f_cost = neighbor.g_cost + neighbor.h_cost
                    neighbor.parent = current
                    
                    if neighbor not in open_set:
                        heapq.heappush(open_set, neighbor)
                        
        return [] # No path found

    def retrace_path(self, start_node, end_node):
        path = []
        current = end_node
        while current != start_node:
            path.append(current)
            current = current.parent
        path.reverse()
        return path

    def get_distance(self, node_a, node_b):
        # Manhattan distance for 4-way movement, Euclidean for 8-way
        dist_x = abs(node_a.x - node_b.x)
        dist_y = abs(node_a.y - node_b.y)
        
        if dist_x > dist_y:
            return 14 * dist_y + 10 * (dist_x - dist_y)
        return 14 * dist_x + 10 * (dist_y - dist_x)
        # Using 10 for straight, 14 for diagonal (if we had diagonal). 
        # For now just returns base cost if straight.
        # Let's simplify for 4-way:
        # return 10

    def heuristic(self, node_a, node_b):
        # Manhattan distance * 10
        return (abs(node_a.x - node_b.x) + abs(node_a.y - node_b.y)) * 10
